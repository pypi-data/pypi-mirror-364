# projects/sql.py

import os
import csv
import queue
import sqlite3
import threading
import re
import time
import inspect
from gway import gw

# Regex mask matching the default gway logging pattern. This captures the
# timestamp, log level, logger name, function name, filename, line number, and
# message from lines formatted by :func:`gway.logging.setup_logging`.
DEFAULT_LOG_MASK = (
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+) "
    r"\[(?P<name>[^\]]+)\] "
    r"(?P<func>\S+) "
    r"(?P<file>[^:]+):(?P<line>\d+)  # (?P<msg>.*)"
)

# # GWAY database functions. These can be called from anywhere safely:
#
# from gway import gw
#
# with gw.sql.open_db() as cursor:
#      gq.sql.execute(query)
#
# # Or from a recipe:
#
# sql open-db
#   - execute "<SQL>"

_write_queue = queue.Queue()
_writer_thread = None
_writer_shutdown = threading.Event()

class WrappedConnection:
    def __init__(self, connection):
        self._connection = connection
        self._cursor = None

    def __enter__(self):
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self._connection.commit()
            gw.verbose("Transaction committed.")
        else:
            self._connection.rollback()
            gw.warning("Transaction rolled back due to exception.")
        self._cursor = None

    def __getattr__(self, name):
        return getattr(self._connection, name)

    def cursor(self):
        return self._connection.cursor()

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()


def infer_type(val):
    t, _ = gw.try_cast(val, INTEGER=int, REAL=float)
    return t or "TEXT"


def load_csv(*, connection=None, folder="data", force=False):
    """
    Recursively loads CSVs from a folder into SQLite tables.
    Table names are derived from folder/file paths.
    """
    assert connection
    base_path = gw.resource(folder)

    def load_folder(path, prefix=""):
        cursor = connection.cursor()
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                sub_prefix = f"{prefix}_{item}" if prefix else item
                load_folder(full_path, sub_prefix)
            elif item.endswith(".csv"):
                base_name = os.path.splitext(item)[0]
                table_name = f"{prefix}_{base_name}" if prefix else base_name
                table_name = table_name.replace("-", "_")

                with open(full_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    try:
                        headers = next(reader)
                        sample_row = next(reader)
                    except StopIteration:
                        gw.warning(f"Skipping empty CSV: {full_path}")
                        continue

                    seen = set()
                    unique_headers = []
                    for h in headers:
                        h_clean = h.strip()
                        h_final = h_clean
                        i = 1
                        while h_final.lower() in seen:
                            h_final = f"{h_clean}_{i}"
                            i += 1
                        unique_headers.append(h_final)
                        seen.add(h_final.lower())

                    types = [
                        infer_type(sample_row[i])
                        if i < len(sample_row) else "TEXT"
                        for i in range(len(unique_headers))
                    ]

                    cursor.execute(
                        "SELECT name FROM sqlite_master "
                        "WHERE type='table' AND name=?", (table_name,)
                    )
                    exists = cursor.fetchone()

                    if exists and force:
                        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                        gw.info(f"Dropped existing table: {table_name}")

                    if not exists or force:
                        colspec = ", ".join(
                            f'"{unique_headers[i]}" {types[i]}'
                            for i in range(len(unique_headers))
                        )
                        create = f'CREATE TABLE "{table_name}" ({colspec})'
                        columns_join = ", ".join(f'"{h}"' for h in unique_headers)
                        placeholders = ", ".join("?" for _ in unique_headers)
                        insert = (
                            f'INSERT INTO "{table_name}" ({columns_join}) '
                            f'VALUES ({placeholders})'
                        )

                        cursor.execute(create)
                        cursor.execute(insert, sample_row)
                        cursor.executemany(insert, reader)
                        connection.commit()

                        gw.info(
                            f"Loaded table '{table_name}' with "
                            f"{len(unique_headers)} columns"
                        )
                    else:
                        gw.verbose(f"Skipped existing table: {table_name}")
        cursor.close()

    load_folder(base_path)


def load_excel(*, connection=None, file=None, folder="data", force=False):
    """Load Excel workbooks into tables, one table per sheet."""
    assert connection
    base_path = gw.resource(folder)

    def load_file(path, prefix=""):
        import pandas as pd
        book = pd.read_excel(path, sheet_name=None)
        base = os.path.splitext(os.path.basename(path))[0].replace("-", "_")
        prefix_final = f"{prefix}_{base}" if prefix else base
        for sheet_name, df in book.items():
            sheet_clean = sheet_name.strip().replace(" ", "_").replace("-", "_")
            table = f"{prefix_final}_{sheet_clean}" if sheet_clean else prefix_final
            try:
                df.to_sql(table, connection._connection,
                           if_exists="replace" if force else "fail",
                           index=False)
                gw.info(f"Loaded sheet '{sheet_name}' as table '{table}'")
            except ValueError as e:
                if "exists" in str(e).lower() and not force:
                    gw.verbose(f"Skipped existing table: {table}")
                else:
                    raise

    def load_folder(path, prefix=""):
        for item in os.listdir(path):
            full = os.path.join(path, item)
            if os.path.isdir(full):
                sub = f"{prefix}_{item}" if prefix else item
                load_folder(full, sub)
            elif item.lower().endswith((".xlsx", ".xls")):
                load_file(full, prefix)

    if file:
        load_file(gw.resource(file))
    else:
        load_folder(base_path)


def load_cdv(*, connection=None, file=None, folder="data", force=False):
    """Load CDV tables (colon-delimited) into SQLite."""
    assert connection
    base_path = gw.resource(folder)

    def load_file(path, prefix=""):
        import pandas as pd
        records = gw.cdv.load_all(path)
        if not records:
            gw.debug(f"No records in CDV: {path}")
            return
        df = pd.DataFrame.from_dict(records, orient="index")
        df.index.name = "id"
        df.reset_index(inplace=True)
        base = os.path.splitext(os.path.basename(path))[0].replace("-", "_")
        table = f"{prefix}_{base}" if prefix else base
        try:
            df.to_sql(table, connection._connection,
                      if_exists="replace" if force else "fail",
                      index=False)
            gw.info(f"Loaded CDV '{os.path.basename(path)}' as table '{table}'")
        except ValueError as e:
            if "exists" in str(e).lower() and not force:
                gw.verbose(f"Skipped existing table: {table}")
            else:
                raise

    def load_folder(path, prefix=""):
        for item in os.listdir(path):
            full = os.path.join(path, item)
            if os.path.isdir(full):
                sub = f"{prefix}_{item}" if prefix else item
                load_folder(full, sub)
            elif item.lower().endswith(".cdv"):
                load_file(full, prefix)

    if file:
        load_file(gw.resource(file))
    else:
        load_folder(base_path)


# --- Connection Management (Drop-in Replacement) ---

_connection_cache = {}
_db_configs = {}

def open_db(
        datafile=None, *,
        project=None,
        sql_engine=None, autoload=False, force=False, row_factory=False, **dbopts):
    """Initialize or reuse a database connection.

    ``project`` allows configuring multiple databases which can later be
    referenced by name.  Subsequent calls for the same ``project`` reuse the
    stored configuration and cached connection.
    """
    project = project or "default"
    cfg = _db_configs.setdefault(project, {})
    if datafile is not None:
        cfg["datafile"] = datafile
    if sql_engine is not None:
        cfg["sql_engine"] = sql_engine
    if row_factory:
        cfg["row_factory"] = row_factory
    if dbopts:
        cfg.setdefault("dbopts", {}).update(dbopts)

    datafile = datafile or cfg.get("datafile")
    sql_engine = sql_engine or cfg.get("sql_engine", "sqlite")
    row_factory = row_factory or cfg.get("row_factory", False)
    dbopts = {**cfg.get("dbopts", {}), **dbopts}

    if sql_engine != "duckdb":
        _start_writer_thread()
    base_key = (project, sql_engine, datafile or "default")
    thread_key = threading.get_ident() if sql_engine in ("sqlite", "duckdb") else "*"
    key = (base_key, thread_key)

    # Reuse cached connection if available
    if key in _connection_cache:
        conn = _connection_cache[key]
        if row_factory:
            gw.warning("Row factory change requires close_connection(). Reconnect manually.")
        gw.verbose(f"Reusing connection: {key}")
        return conn

    # Create connection per backend
    if sql_engine == "sqlite":
        path = gw.resource(datafile or "work/data.sqlite")
        # Note: check_same_thread=False for sharing connections in the writer thread
        try:
            conn = sqlite3.connect(str(path), check_same_thread=False)
        except sqlite3.OperationalError as e:
            gw.abort(
                f"Unable to open SQLite database at {str(path)}. "
                f"Check the path and file permissions. ({e})"
            )
        if row_factory:
            if row_factory is True:
                conn.row_factory = sqlite3.Row
            elif callable(row_factory):
                conn.row_factory = row_factory
            elif isinstance(row_factory, str):
                conn.row_factory = gw[row_factory]
            gw.debug(f"Configured row_factory: {conn.row_factory}")
        gw.info(f"Opened SQLite connection at {path}")
        _start_writer_thread()  # Ensure writer is running
    elif sql_engine == "duckdb":
        import duckdb
        path = gw.resource(datafile or "work/data.duckdb")
        conn = duckdb.connect(path)
        gw.info(f"Opened DuckDB connection at {path}")
    elif sql_engine == "postgres":
        import psycopg2
        conn = psycopg2.connect(**dbopts)
        gw.info(f"Connected to Postgres at {dbopts.get('host', 'localhost')}")
    else:
        raise ValueError(f"Unsupported sql_engine: {sql_engine}")

    # Wrap and cache connection
    conn = WrappedConnection(conn)
    conn._engine = sql_engine
    _connection_cache[key] = conn

    if autoload and sql_engine == "sqlite":
        load_csv(connection=conn, force=force)
        load_excel(connection=conn, force=force)
        load_cdv(connection=conn, force=force)

    return conn


def close_connection(datafile=None, *, project=None, sql_engine=None, all=False):
    """
    Explicitly close one or all cached database connections.
    Shuts down writer thread if all connections closed.
    """
    project = project or "default"
    if all:
        for key, connection in list(_connection_cache.items()):
            try:
                connection.close()
            except Exception as e:
                gw.warning(f"Failed to close connection: {e}")
            _connection_cache.pop(key, None)
        shutdown_writer()
        gw.info("All connections closed.")
        return

    cfg = _db_configs.get(project, {})
    if datafile is None:
        datafile = cfg.get("datafile")
    if sql_engine is None:
        sql_engine = cfg.get("sql_engine", "sqlite")

    base_key = (project, sql_engine, datafile or "default")
    thread_key = threading.get_ident() if sql_engine in ("sqlite", "duckdb") else "*"
    key = (base_key, thread_key)
    connection = _connection_cache.pop(key, None)
    if connection:
        try:
            connection.close()
            gw.info(f"Closed connection: {key}")
        except Exception as e:
            gw.warning(f"Failed to close {key}: {e}")

def _run(cursor, sql, *, args=None, is_script=False):
    """Execute SQL and rethrow errors with the failing statement."""
    try:
        if is_script:
            cursor.executescript(sql)
            return None
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        return cursor.fetchall() if cursor.description else None
    except Exception as e:  # pragma: no cover - interactive
        raise type(e)(f"{e}. SQL: {sql}") from e


def execute(*sql, connection=None, script=None, sep='; ', args=None):
    """
    Thread-safe SQL execution.
    - SELECTs and other read queries run immediately (parallel safe).
    - DML/DDL statements (INSERT/UPDATE/DELETE/etc) are funneled into the write queue.
    - Multi-statement scripts are supported via executescript.
    - All write queue items are always 5-tuple: (sql, args, conn, result_q, is_script)
    """
    assert connection, "Pass connection= from gw.sql.open_db()"

    if script:
        script_text = gw.resource(script, text=True)
        # Recursively call as a multi-statement script
        return execute(script_text, connection=connection)

    if sql:
        sql = sep.join(sql)
    else:
        raise ValueError("SQL statement required")

    # Detect if this is a multi-statement script (very basic: contains semicolon)
    # Note: More robust SQL parsing is possible but out of scope here.
    stripped_sql = sql.strip().rstrip(";")
    is_script = ";" in stripped_sql

    # If it is a read-only statement and not a script, execute directly
    if not _is_write_query(sql) and not is_script:
        cursor = connection.cursor()
        try:
            return _run(cursor, sql, args=args)
        finally:
            cursor.close()
    else:
        # DuckDB connections are not thread-safe, execute writes synchronously
        if getattr(connection, "_engine", "sqlite") == "duckdb":
            cursor = connection.cursor()
            try:
                rows = _run(cursor, sql, args=args, is_script=is_script)
                connection.commit()
                return rows
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
        else:
            # All writes or scripts are serialized via the queue.
            result_q = queue.Queue()
            # Always enqueue a 5-item tuple: (sql, args, conn, result_q, is_script)
            _write_queue.put((sql, args, connection._connection, result_q, is_script))
            rows, error = result_q.get()
            if error:
                raise error
            return rows


def _process_writes():
    while not _writer_shutdown.is_set():
        try:
            item = _write_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        if item is None:
            _write_queue.task_done()
            break
        sql, args, conn, result_q, is_script = item  # Always expect 5!
        try:
            cursor = conn.cursor()
            rows = _run(cursor, sql, args=args, is_script=is_script)
            conn.commit()
            result_q.put((rows, None))
        except Exception as e:
            conn.rollback()
            result_q.put((None, e))
        finally:
            cursor.close()
            _write_queue.task_done()


def _is_write_query(sql):
    sql = sql.strip().lower()
    # Simple heuristic: treat as write if it starts with DML or DDL
    return any(sql.startswith(word)
        for word in ("insert", "update", "delete", "create", "drop", "alter", "replace", "truncate", "vacuum", "attach", "detach"))


def _start_writer_thread():
    global _writer_thread
    if _writer_thread is None or not _writer_thread.is_alive():
        _writer_thread = threading.Thread(target=_process_writes, daemon=True)
        _writer_thread.start()


def shutdown_writer():
    """Signal writer thread to exit and wait for it to finish."""
    global _writer_thread
    _writer_shutdown.set()
    # Put enough poison pills for any possible writer threads (usually 1)
    _write_queue.put(None)
    if _writer_thread:
        _writer_thread.join(timeout=2)
        _writer_thread = None  # Allow restart
    # Clean up: clear shutdown flag for future tests
    _writer_shutdown.clear()
    # Drain any leftover queue items (to avoid memory leaks between tests)
    try:
        while True:
            _write_queue.get_nowait()
            _write_queue.task_done()
    except queue.Empty:
        pass


def parse_log(
    mask: str = DEFAULT_LOG_MASK,
    log_location=None,
    *,
    table,
    connection=None,
    start_at_end=True,
    poll_interval=0.5,
    stop_event=None,
    flags=0,
):
    """Consume a log file in real time and store matching records.

    Parameters:
        mask (str): Regular expression with named groups representing columns.
            Defaults to ``DEFAULT_LOG_MASK`` which parses standard GWay logs.
        log_location (str): Path to the log file to monitor.
        table (str): Table to insert parsed records into.
        connection: Database connection from :func:`open_db`.
        start_at_end (bool): If True, begin tailing from end of file.
        poll_interval (float): Seconds to wait for new lines.
        stop_event (threading.Event): Optional event to stop the tail loop.
        flags (int): Regex flags for ``re.compile``.
    """

    assert connection, "Pass connection= from gw.sql.open_db()"

    regex = re.compile(mask, flags)
    columns = list(regex.groupindex.keys())
    if not columns:
        raise ValueError("Mask must use named capturing groups for columns")

    colspec = ", ".join(f'"{c}" TEXT' for c in columns)
    gw.sql.execute(
        f'CREATE TABLE IF NOT EXISTS "{table}" ({colspec})',
        connection=connection,
    )

    stop_event = stop_event or threading.Event()

    with open(log_location, "r", encoding="utf-8") as f:
        if start_at_end:
            f.seek(0, os.SEEK_END)
        while not stop_event.is_set():
            line = f.readline()
            if not line:
                time.sleep(poll_interval)
                continue
            m = regex.search(line)
            if not m:
                continue
            values = m.groupdict()
            columns_sql = ", ".join(f'"{c}"' for c in columns)
            placeholders = ", ".join("?" for _ in columns)
            gw.sql.execute(
                f'INSERT INTO "{table}" ({columns_sql}) VALUES ({placeholders})',
                args=tuple(values[c] for c in columns),
                connection=connection,
            )

    return stop_event

# --- Migration Helpers ---
_STAGED_SQL = {}

def stage(sql: str, *, dbfile=None):
    """Store SQL to apply later with :func:`migrate`."""
    key = dbfile or 'default'
    _STAGED_SQL.setdefault(key, []).append(sql)
    gw.debug(f"Staged SQL for {key}: {sql}")


def migrate(*, dbfile=None):
    """Execute staged SQL statements for ``dbfile``."""
    key = dbfile or 'default'
    sql_list = _STAGED_SQL.pop(key, [])
    if not sql_list:
        gw.info("No staged SQL to migrate")
        return 0
    with open_db(dbfile) as cur:
        for stmt in sql_list:
            cur.executescript(stmt)
    gw.info(f"Applied {len(sql_list)} statements to {key}")
    return len(sql_list)


def setup_table(table: str, column: str = None, ctype: str = "TEXT", *,
                primary: bool = False, auto: bool = False,
                dbfile=None, drop: bool = False, immediate: bool = False):
    """Stage creation or modification of ``table``.

    Parameters
    ----------
    table: str
        Table to create or extend.
    column: str, optional
        Name of the column to add. If omitted, only ``drop`` is honored.
    ctype: str, optional
        Column type, defaults to ``TEXT``.
    primary: bool
        Mark column as ``PRIMARY KEY``.
    auto: bool
        Add ``AUTOINCREMENT`` to the column.
    dbfile: str, optional
        Target database file.
    drop: bool
        Drop the table before creating it again.
    immediate: bool
        Apply staged SQL immediately via :func:`migrate`.
    """

    if drop:
        stage(f'DROP TABLE IF EXISTS "{table}"', dbfile=dbfile)

    if column:
        spec = f'"{column}" {ctype}'
        if primary:
            spec += " PRIMARY KEY"
        if auto:
            spec += " AUTOINCREMENT"

        key = (dbfile or 'default', table)
        created = getattr(setup_table, "_created", set())
        if key not in created:
            stage(f'CREATE TABLE IF NOT EXISTS "{table}" ({spec})', dbfile=dbfile)
            created.add(key)
            setattr(setup_table, "_created", created)
        else:
            stage(f'ALTER TABLE "{table}" ADD COLUMN {spec}', dbfile=dbfile)

    if immediate:
        migrate(dbfile=dbfile)


class TableProxy:
    """Lightweight helper exposing CRUD operations for a table."""

    def __init__(self, name: str, *, dbfile=None, sql_engine="sqlite", project=None):
        self.name = name
        self.dbfile = dbfile
        self.sql_engine = sql_engine
        self.project = project

    def create(self, **fields):
        """Insert a record and return the last row id."""
        return gw.sql.crud.api_create(
            table=self.name,
            dbfile=self.dbfile,
            sql_engine=self.sql_engine,
            project=self.project,
            **fields,
        )

    def read(self, id, id_col: str = "id"):
        """Read a record by ``id``."""
        return gw.sql.crud.api_read(
            table=self.name,
            id=id,
            id_col=id_col,
            dbfile=self.dbfile,
            sql_engine=self.sql_engine,
            project=self.project,
        )

    def update(self, id, id_col: str = "id", **fields):
        """Update fields for ``id``."""
        gw.sql.crud.api_update(
            table=self.name,
            id=id,
            id_col=id_col,
            dbfile=self.dbfile,
            sql_engine=self.sql_engine,
            project=self.project,
            **fields,
        )

    def delete(self, id, id_col: str = "id"):
        """Delete record by ``id``."""
        gw.sql.crud.api_delete(
            table=self.name,
            id=id,
            id_col=id_col,
            dbfile=self.dbfile,
            sql_engine=self.sql_engine,
            project=self.project,
        )

    def all(self):
        """Return all rows from the table."""
        conn = gw.sql.open_db(self.dbfile, sql_engine=self.sql_engine, project=self.project)
        return gw.sql.execute(f'SELECT * FROM "{self.name}"', connection=conn)


def _python_type_to_sql(tp):
    """Best effort mapping of Python type to SQLite type."""
    if tp in (int, bool):
        return "INTEGER"
    if tp is float:
        return "REAL"
    if tp is bytes:
        return "BLOB"
    return "TEXT"


def _parse_model_definition(defn, name=None):
    """Return (table_name, column_spec) from various definitions."""
    import dataclasses
    import inspect

    if isinstance(defn, str):
        if "(" in defn:
            # Either full CREATE statement or "name(col type, ...)"
            m = re.match(r"\s*create\s+table\s+(?:if\s+not\s+exists\s+)?\[?(?P<name>\w+)\]?\s*\((?P<cols>.+)\)" , defn, re.I | re.S)
            if m:
                return m.group("name"), m.group("cols")
            m = re.match(r"\s*(?P<name>\w+)\s*\((?P<cols>.+)\)\s*", defn, re.S)
            if m:
                return m.group("name"), m.group("cols")
        return defn, None

    if isinstance(defn, dict):
        tbl = name or defn.get("__name__") or defn.get("name") or defn.get("table")
        if not tbl:
            raise ValueError("Table name required for dict definition")
        cols = [f'"{k}" {v}' for k, v in defn.items() if not k.startswith("__") and k not in ("__name__", "table")]
        return tbl, ", ".join(cols) if cols else None

    if dataclasses.is_dataclass(defn):
        tbl = name or getattr(defn, "__name__", None)
        cols = []
        for f in dataclasses.fields(defn):
            ctype = _python_type_to_sql(f.type)
            spec = f'"{f.name}" {ctype}'
            if f.name == "id" and ctype == "INTEGER":
                spec += " PRIMARY KEY AUTOINCREMENT"
            cols.append(spec)
        return tbl, ", ".join(cols)

    if inspect.isclass(defn) and hasattr(defn, "_fields"):
        tbl = name or getattr(defn, "__name__", None)
        cols = [f'"{f}" TEXT' for f in defn._fields]
        return tbl, ", ".join(cols)

    ann = getattr(defn, "__annotations__", None)
    if ann:
        tbl = name or getattr(defn, "__name__", None)
        cols = [f'"{k}" {_python_type_to_sql(t)}' for k, t in ann.items()]
        return tbl, ", ".join(cols)

    return str(defn), None

  
def model(defn, *, dbfile=None, create=True, name=None, sql_engine=None, project=None):
    """Return a :class:`TableProxy` for ``defn``.

    ``defn`` may be a table name, mapping, dataclass, namedtuple or SQL spec.
    If column definitions are available and ``create`` is True the table is
    created automatically using ``CREATE TABLE IF NOT EXISTS``.  When the table
    already exists any missing columns from ``defn`` are added via ``ALTER
    TABLE`` so existing data is preserved.
    """

    caller = inspect.currentframe().f_back
    module = inspect.getmodule(caller)
    if dbfile is None:
        dbfile = getattr(module, "DBFILE", None)
    if sql_engine is None:
        sql_engine = getattr(module, "ENGINE", getattr(module, "SQL_ENGINE", "sqlite"))
    if project is None:
        project = getattr(module, "PROJECT", None)

    table, colspec = _parse_model_definition(defn, name)
    if not table:
        raise ValueError("Could not determine table name from definition")

    if colspec and create:
        conn = gw.sql.open_db(dbfile, sql_engine=sql_engine, project=project)
        gw.sql.execute(
            f'CREATE TABLE IF NOT EXISTS "{table}" ({colspec})',
            connection=conn,
        )
        rows = gw.sql.execute(
            f'PRAGMA table_info("{table}")', connection=conn
        )
        existing = {r[1] for r in rows}
        for col_def in [c.strip() for c in colspec.split(',') if c.strip()]:
            m = re.match(r'[\[\"`]?([^\s\"`\]]+)', col_def)
            if not m:
                continue
            col_name = m.group(1)
            if col_name not in existing:
                gw.sql.execute(
                    f'ALTER TABLE "{table}" ADD COLUMN {col_def}',
                    connection=conn,
                )

    return TableProxy(table, dbfile=dbfile, sql_engine=sql_engine, project=project)

# Backwards compatibility aliases
open_connection = open_db
close_db = close_connection

