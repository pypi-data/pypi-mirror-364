# projects/cdv.py

import os
from gway import gw
from urllib.parse import quote, unquote


def _encode(val):
    # Only encode if non-empty string
    return quote(val, safe='') if isinstance(val, str) and val else val


def _decode(val):
    return unquote(val) if isinstance(val, str) and val else val


def _resolve_path(pathlike):
    """Resolve to absolute path using gw.resource."""
    return gw.resource(pathlike)


def _read_table(path):
    """Read and parse a CDV table file."""
    if not path:
        return {}
    if not os.path.exists(path):
        gw.error(f"Table file not found: {path}")
        return {}
    result = {}
    with open(path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or ":" not in line:
                continue
            parts = line.split(":")
            entry = parts[0].strip()
            fields = {}
            for part in parts[1:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    fields[k.strip()] = _decode(v.strip())
            result[entry] = fields
    return result


def _write_table(path, records):
    """Write the complete dict of records to a CDV table file."""
    with open(path, "w") as f:
        for entry_id, fields in records.items():
            line = entry_id + "".join(
                f":{k}={_encode(v)}" for k, v in fields.items()
            )
            f.write(line + "\n")


def load_all(pathlike: str) -> dict[str, dict[str, str]]:
    """Load CDV table with ID followed by colon-separated key=value fields."""
    try:
        path = _resolve_path(pathlike)
        return _read_table(path)
    except Exception as e:
        gw.abort(f"Failed to read table '{pathlike}': {e}")


def update(table_path: str, entry_id: str, **fields):
    """Append or update a record in the CDV table, preserving unspecified fields."""
    if not entry_id or not table_path:
        return
    path = _resolve_path(table_path)
    records = _read_table(path)
    existing = records.get(entry_id, {})
    existing.update(fields)
    records[entry_id] = existing
    _write_table(path, records)
    gw.info(f"Updated table with ID={entry_id}")


def validate(table_path: str, entry: str, *, validator=None) -> bool:
    """
    Validate a CDV entry by ID directly from file.
    Always reloads the file from disk to avoid stale data.
    """
    path = _resolve_path(table_path)
    table = _read_table(path)
    if not table:
        gw.warn("No table loaded — rejecting validation request.")
        return False
    record = table.get(entry)
    if not record:
        return False
    if validator:
        try:
            return bool(validator(**record))
        except Exception as e:
            gw.error(f"validator failed: {e}")
            return False
    return True


def copy(table_path: str, old_entry: str, new_entry: str, **kwargs) -> bool:
    """Copy a record from old_entry to new_entry, optionally updating fields."""
    path = _resolve_path(table_path)
    records = _read_table(path)
    if old_entry not in records:
        gw.warn(f"Entry '{old_entry}' does not exist; cannot copy.")
        return False
    # Shallow copy of fields
    new_fields = records[old_entry].copy()
    new_fields.update(kwargs)
    records[new_entry] = new_fields
    _write_table(path, records)
    gw.info(f"Copied '{old_entry}' to '{new_entry}' with updates: {kwargs}")
    return True


def move(table_path: str, old_entry: str, new_entry: str, **kwargs) -> bool:
    """Move a record from old_entry to new_entry, optionally updating fields."""
    path = _resolve_path(table_path)
    records = _read_table(path)
    if old_entry not in records:
        gw.warn(f"Entry '{old_entry}' does not exist; cannot move.")
        return False
    new_fields = records[old_entry].copy()
    new_fields.update(kwargs)
    records[new_entry] = new_fields
    del records[old_entry]
    _write_table(path, records)
    gw.info(f"Moved '{old_entry}' to '{new_entry}' with updates: {kwargs}")
    return True


def credit(table_path: str, entry: str, *, field: str = 'balance', **kwargs) -> bool:
    """Add 1 (or amount from kwargs) to the given field for a record."""
    path = _resolve_path(table_path)
    records = _read_table(path)
    if entry not in records:
        gw.warn(f"Entry '{entry}' does not exist; cannot credit.")
        return False
    try:
        amt = float(kwargs.pop('amount', 1))
        prev = float(records[entry].get(field, 0))
        records[entry][field] = str(prev + amt)
        records[entry].update(kwargs)
        _write_table(path, records)
        gw.info(f"Credited {amt} to '{entry}' field '{field}'. New value: {records[entry][field]}")
        return True
    except Exception as e:
        gw.error(f"credit failed: {e}")
        return False


def debit(table_path: str, entry: str, *, field: str = 'balance', **kwargs) -> bool:
    """Subtract 1 (or amount from kwargs) from the given field for a record."""
    path = _resolve_path(table_path)
    records = _read_table(path)
    if entry not in records:
        gw.warn(f"Entry '{entry}' does not exist; cannot debit.")
        return False
    try:
        amt = float(kwargs.pop('amount', 1))
        prev = float(records[entry].get(field, 0))
        records[entry][field] = str(prev - amt)
        records[entry].update(kwargs)
        _write_table(path, records)
        gw.info(f"Debited {amt} from '{entry}' field '{field}'. New value: {records[entry][field]}")
        return True
    except Exception as e:
        gw.error(f"debit failed: {e}")
        return False


def view_colon_validator(*, text=None):
    
    # can paste a CDV file into a large textarea and submit for validation as 'text'.
    # If text is received, test and validate it and let the user know if there are any issues
    # found that would impede the file to be processed as a valid CDV. 

    raise NotImplementedError


def save_all(pathlike: str, all_records: dict[str, dict[str, str]]):
    """
    Replace all records in the CDV file at pathlike with the given dict.
    """
    path = _resolve_path(pathlike)
    _write_table(path, all_records)


def read_rows(pathlike: str) -> list[list[str]]:
    """
    Read a CDV as a list of rows: [id, k1, v1, ...].
    """
    records = load_all(pathlike)
    rows = []
    for entry_id, fields in records.items():
        row = [entry_id]
        for k, v in fields.items():
            row += [k, v]
        rows.append(row)
    return rows


def write_rows(pathlike: str, rows: list[list[str]]):
    """
    Write a list of rows: [id, k1, v1, ...] as a CDV file.
    """
    recs = {}
    for row in rows:
        if not row: continue
        entry_id = row[0]
        fields = {row[i]: row[i+1] for i in range(1, len(row)-1, 2)}
        recs[entry_id] = fields
    save_all(pathlike, recs)


def delete(table_path: str, entry_id: str):
    """
    Remove a record by ID from the CDV table.
    """
    path = _resolve_path(table_path)
    records = _read_table(path)
    if entry_id in records:
        del records[entry_id]
        _write_table(path, records)
        gw.info(f"Deleted record '{entry_id}' from table.")
        return True
    return False


def _sanitize_cdv_path(pathlike: str) -> str:
    """Return a sanitized path string safe for gw.resource."""
    from projects.web.site import _sanitize_filename

    parts = [
        _sanitize_filename(p)
        for p in str(pathlike).replace("\\", "/").split("/")
        if p and p not in {"..", "."}
    ]
    return "/".join(parts)


def _parse_cdv_text(text: str) -> dict[str, dict[str, str]]:
    """Parse colon-delimited text into a record dict."""
    records = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        parts = line.split(":")
        entry_id = parts[0].strip()
        fields = {}
        for part in parts[1:]:
            if "=" in part:
                k, v = part.split("=", 1)
                fields[k.strip()] = _decode(v.strip())
        if entry_id:
            records[entry_id] = fields
    return records


def _records_to_text(records: dict[str, dict[str, str]]) -> str:
    """Serialize record dict back to colon-delimited text."""
    lines = []
    for entry_id, fields in records.items():
        line = entry_id + "".join(
            f":{k}={_encode(v)}" for k, v in fields.items()
        )
        lines.append(line)
    return "\n".join(lines)


def view_data_editor(*, cdv: str = None, text: str = None):
    """Interactive editor for CDV files."""
    from bottle import request, response
    import html

    if not cdv:
        return (
            "<h1>CDV Data Editor</h1>"
            "<form method='get'>"
            "<input name='cdv' placeholder='path/to/file.cdv' required> "
            "<button type='submit'>Open</button>"
            "</form>"
        )

    cdv_safe = _sanitize_cdv_path(cdv)
    try:
        path = gw.resource(*cdv_safe.split("/"))
        if os.path.isdir(path):
            raise IsADirectoryError(path)
    except Exception as e:
        return f"<p>Invalid CDV path: {html.escape(str(e))}</p>"

    if request.method == "POST":
        records = _parse_cdv_text(text or "")
        save_all(path, records)
        response.status = 303
        url = gw.web.app.build_url("data-editor", cdv=cdv_safe)
        response.set_header("Location", url)
        return ""

    records = load_all(path)
    cdv_text = html.escape(_records_to_text(records))
    return (
        f"<h1>Editing {html.escape(cdv_safe)}</h1>"
        "<form method='post'>"
        f"<textarea name='text' rows='15' style='width:100%;'>{cdv_text}</textarea>"
        f"<input type='hidden' name='cdv' value='{html.escape(cdv_safe)}'>"
        "<button type='submit'>Save</button>"
        "</form>"
    )
