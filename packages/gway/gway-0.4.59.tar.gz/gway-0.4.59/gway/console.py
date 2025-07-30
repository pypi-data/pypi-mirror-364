# file: gway/console.py

import io
import sys
import json
import time
import inspect
import argparse
import argcomplete
import csv
from typing import get_origin, get_args, Literal, Union

from .logging import setup_logging
from .builtins import abort
from .gateway import Gateway, gw


def cli_main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Dynamic Project CLI")

    # Primary behavior flags
    add = parser.add_argument
    add("-a", dest="all", action="store_true", help="Show all text results, not just the last")
    add("-c", dest="client", type=str, help="Specify client environment")
    add("-d", dest="debug", action="store_true", help="Enable debug logging")
    add("-e", dest="expression", type=str, help="Return resolved sigil at the end")
    add("-j", dest="json", nargs="?", const=True, default=False, help="Output result(s) as JSON")
    add("-o", dest="outfile", type=str, help="Write text output(s) to this file")
    add("-p", dest="projects", type=str, help="Root project path for custom functions.")
    add("-r", dest="recipe", type=str, help="Execute a GWAY recipe (.gwr) file.")
    add("-s", dest="server", type=str, help="Override server environment configuration")
    add("-t", dest="timed", action="store_true", help="Enable timing of operations")
    add("-u", dest="username", type=str, help="Operate as the given end-user account.")
    add("-v", dest="verbose", action="store_true", help="Verbose mode (where supported)")
    add("-w", dest="wizard", action="store_true", help="Wizard mode.")
    add("-z", dest="silent", action="store_true", help="Suppress all non-critical output")
    add("commands", nargs=argparse.REMAINDER, help="Project/Function command(s)")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Setup logging
    logfile = f"{args.username}.log" if args.username else "gway.log"
    setup_logging(
        logfile=logfile,
        loglevel="DEBUG" if args.debug else "INFO",
        debug=args.debug,
        verbose=args.verbose
    )
    start_time = time.time() if args.timed else None
    
    # Init Gateway instance
    gw_local = Gateway(
        client=args.client,
        server=args.server,
        verbose=args.verbose,
        silent=args.silent,
        name=args.username or "gw",
        project_path=args.projects,
        debug=args.debug,
        wizard=args.wizard,
        timed=args.timed
    )

    gw_local.verbose(
        f"Saving detailed logs to [BASE_PATH]/logs/gway.log (this file)"
    )

    # Load command sources
    if args.recipe:
        command_sources, comments = load_recipe(args.recipe)
    elif args.commands:
        command_sources = chunk(args.commands)
    else:
        parser.print_help()
        sys.exit(1)

    # Run commands
    run_kwargs = {}
    if args.projects:
        run_kwargs['project_path'] = args.projects
    if args.client:
        run_kwargs['client'] = args.client
    if args.server:
        run_kwargs['server'] = args.server
    if args.timed:
        run_kwargs['timed'] = True
    all_results, last_result = process(command_sources, **run_kwargs)

    # Resolve expression if requested
    if args.expression:
        output = Gateway(**last_result).resolve(args.expression)
    else:
        output = last_result

    # Convert generators to lists
    def realize(val):
        if hasattr(val, "__iter__") and not isinstance(val, (str, bytes, dict)):
            try:
                return list(val)
            except Exception:
                return val
        return val

    all_results = [realize(r) for r in all_results]
    output = realize(output)

    # Emit result(s)
    def emit(data):
        if args.json:
            print(json.dumps(data, indent=2, default=str))
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            csv_str = _rows_to_csv(data)
            print(csv_str or data)
        elif data is not None:
            print(data)

    if args.all:
        for result in all_results:
            emit(result)
    else:
        emit(output)

    # Write to file if needed
    if args.outfile:
        with open(args.outfile, "w") as f:
            if args.json:
                json.dump(all_results if args.all else output, f, indent=2, default=str)
            elif isinstance(output, list) and output and isinstance(output[0], dict):
                f.write(_rows_to_csv(output))
            else:
                f.write(str(output))

    if start_time:
        print(f"Time: {time.time() - start_time:.3f} seconds")

def process(command_sources, callback=None, **context):
    """Shared logic for executing CLI or recipe commands with optional per-node callback."""
    import argparse
    from gway import gw as _global_gw, Gateway
    from .builtins import abort

    all_results = []
    last_result = None

    gw = Gateway(**context) if context else _global_gw

    def resolve_nested_object(root, tokens):
        """Resolve a sequence of command tokens to a nested object (e.g. gw.project.module.func).

        Returns a tuple ``(obj, remaining, path, error)`` where ``error`` is the
        last ``AttributeError`` encountered while traversing the path. This lets
        callers surface import failures instead of showing a generic 'No project'
        message.
        """
        path = []
        obj = root
        last_error = None

        while tokens:
            normalized = normalize_token(tokens[0])
            try:
                obj = getattr(obj, normalized)
                path.append(tokens.pop(0))
                continue
            except AttributeError as e:
                last_error = e

            # Try to resolve composite function names from remaining tokens
            for i in range(len(tokens), 0, -1):
                joined = "_".join(normalize_token(t) for t in tokens[:i])
                try:
                    obj = getattr(obj, joined)
                    path.extend(tokens[:i])
                    tokens[:] = tokens[i:]
                    return obj, tokens, path, last_error
                except AttributeError as e:
                    last_error = e
                    continue
            break  # No match found; exit lookup loop

        return obj, tokens, path, last_error

    for chunk in command_sources:
        if not chunk:
            continue

        gw.debug(f"Next {chunk=}")

        # Invoke callback if provided
        if callback:
            callback_result = callback(chunk)
            if callback_result is False:
                gw.debug(f"Skipping chunk due to callback: {chunk}")
                continue
            elif isinstance(callback_result, list):
                gw.debug(f"Callback replaced chunk: {callback_result}")
                chunk = callback_result
            elif callback_result is None or callback_result is True:
                pass
            else:
                abort(f"Invalid callback return value for chunk: {callback_result}")

        if not chunk:
            continue

        chunk = join_unquoted_kwargs(list(chunk))

        # Resolve nested project/function path
        resolved_obj, func_args, path, attr_error = resolve_nested_object(
            gw, list(chunk)
        )

        if not callable(resolved_obj):
            if attr_error is not None:
                abort(str(attr_error))
            if hasattr(resolved_obj, '__functions__'):
                show_functions(resolved_obj.__functions__)
            else:
                gw.error(f"Object at path {' '.join(path)} is not callable.")
            abort(f"No project with name '{chunk[0]}'")

        # Parse function arguments, using parse_known_args if **kwargs present
        func_parser = argparse.ArgumentParser(prog=".".join(path))
        add_func_args(func_parser, resolved_obj)

        var_kw_name = getattr(resolved_obj, "__var_keyword_name__", None)
        if var_kw_name:
            parsed_args, unknown = func_parser.parse_known_args(func_args)
            # stash the raw unknown tokens for prepare
            setattr(parsed_args, var_kw_name, unknown)
        else:
            parsed_args = func_parser.parse_args(func_args)

        # Prepare and invoke
        final_args, final_kwargs = prepare(parsed_args, resolved_obj)
        try:
            result = resolved_obj(*final_args, **final_kwargs)
            last_result = result
            all_results.append(result)
        except Exception as e:
            gw.exception(e)
            name = getattr(resolved_obj, "__name__", str(resolved_obj))
            abort(f"Unhandled {type(e).__name__} in {name} -> {str(e)} @ {str(resolved_obj.__module__)}.py")

    return all_results, last_result

def prepare(parsed_args, func_obj):
    """Prepare *args and **kwargs for a function call."""
    func_args = []
    func_kwargs = {}
    extra_kwargs = {}

    sig = inspect.signature(func_obj)
    params = sig.parameters
    expected_names = set(params.keys())

    # 1) Pull out any positional / named args that argparse already parsed:
    for name, value in vars(parsed_args).items():
        if name in expected_names:
            param = params[name]
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                func_args.extend(value or [])
            elif param.kind != inspect.Parameter.VAR_KEYWORD:
                func_kwargs[name] = value

    # 2) Now handle the **kwargs slot (if any) from parse_known_args:
    var_kw_name = getattr(func_obj, "__var_keyword_name__", None)
    if var_kw_name:
        raw_items = getattr(parsed_args, var_kw_name, []) or []
        i = 0
        while i < len(raw_items):
            token = raw_items[i]
            if token.startswith("--") and "=" in token:
                key, val = token[2:].split("=", 1)
                i += 1
            elif token.startswith("--"):
                key = token[2:]
                i += 1
                if i >= len(raw_items):
                    abort(f"Expected a value after `{token}`")
                val_tokens = []
                while i < len(raw_items) and not raw_items[i].startswith("-"):
                    val_tokens.append(raw_items[i])
                    i += 1
                if not val_tokens:
                    abort(f"Expected a value after `{token}`")
                val = " ".join(val_tokens)
            else:
                abort(
                    f"Invalid kwarg format `{token}`; expected `--key[=value]` or `--key value`."
                )
            extra_kwargs[key.replace("-", "_")] = val

    return func_args, {**func_kwargs, **extra_kwargs}

def join_unquoted_kwargs(tokens: list[str]) -> list[str]:
    """Combine values after ``--key`` up to the next dash token.

    This allows passing multi-word strings without quoting as documented
    in the "Unquoted Kwargs" section of :mod:`README`.
    """
    combined: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        combined.append(token)
        if token.startswith("--") and "=" not in token:
            i += 1
            value_parts = []
            while i < len(tokens) and not tokens[i].startswith("-"):
                value_parts.append(tokens[i])
                i += 1
            if value_parts:
                combined.append(" ".join(value_parts))
            continue
        i += 1
    return combined

def chunk(args_commands):
    """Split args.commands into logical chunks without breaking quoted arguments."""
    chunks = []
    current_chunk = []

    for token in args_commands:
        if token in ('-', ';'):
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
        else:
            current_chunk.append(token)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def show_functions(functions: dict):
    """Display a formatted view of available functions."""
    from .builtins import sample_cli

    print("Available functions:")
    for name, func in functions.items():
        name_cli = name.replace("_", "-")
        cli_args = sample_cli(func)
        doc = ""
        if func.__doc__:
            doc_lines = [line.strip() for line in func.__doc__.splitlines()]
            doc = next((line for line in doc_lines if line), "")

        print(f"  > {name_cli} {cli_args}")
        if doc:
            print(f"      {doc}")

def add_func_args(subparser, func_obj):
    """Add the function's arguments to the CLI subparser."""
    sig = inspect.signature(func_obj)
    seen_kw_only = False

    for arg_name, param in sig.parameters.items():
        # VAR_POSITIONAL: e.g. *args
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            subparser.add_argument(
                arg_name,
                nargs='*',
                help=f"Variable positional arguments for {arg_name}"
            )

        # VAR_KEYWORD: e.g. **kwargs
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            func_obj.__var_keyword_name__ = arg_name  # e.g. "fields or kwargs"

        # regular args or keyword-only
        else:
            is_positional = not seen_kw_only and param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD
            )

            # before the first kw-only marker (*) → positional
            if is_positional:
                opts = get_arg_opts(arg_name, param, gw)
                # argparse forbids 'required' on positionals:
                opts.pop('required', None)

                if param.default is not inspect.Parameter.empty:
                    # optional positional
                    subparser.add_argument(
                        arg_name,
                        nargs='?',
                        **opts
                    )
                else:
                    # required positional
                    subparser.add_argument(
                        arg_name,
                        **opts
                    )

            # after * or keyword-only → flags
            else:
                seen_kw_only = True
                cli_name = f"--{arg_name.replace('_', '-')}"
                if param.annotation is bool or isinstance(param.default, bool):
                    grp = subparser.add_mutually_exclusive_group(required=False)
                    grp.add_argument(
                        cli_name,
                        dest=arg_name,
                        action="store_true",
                        help=f"Enable {arg_name}"
                    )
                    grp.add_argument(
                        f"--no-{arg_name.replace('_', '-')}",
                        dest=arg_name,
                        action="store_false",
                        help=f"Disable {arg_name}"
                    )
                    subparser.set_defaults(**{arg_name: param.default})
                else:
                    opts = get_arg_opts(arg_name, param, gw)
                    subparser.add_argument(cli_name, **opts)


def get_arg_opts(arg_name, param, gw=None):
    """Infer argparse options from parameter signature."""
    opts = {}
    annotation = param.annotation
    default = param.default

    origin = get_origin(annotation)
    args = get_args(annotation)
    inferred_type = str

    if origin == Literal:
        opts["choices"] = args
        inferred_type = type(args[0]) if args else str
    elif origin == Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            inner_param = type("param", (), {"annotation": non_none[0], "default": default})
            return get_arg_opts(arg_name, inner_param, gw)
        elif all(a in (str, int, float) for a in non_none):
            inferred_type = str
    elif annotation != inspect.Parameter.empty:
        inferred_type = annotation

    opts["type"] = inferred_type

    if default != inspect.Parameter.empty:
        if isinstance(default, str) and default.startswith("[") and default.endswith("]") and gw:
            try:
                default = gw.resolve(default)
            except Exception as e:
                print(f"Failed to resolve default for {arg_name}: {e}")
        opts["default"] = default
    else:
        opts["required"] = True

    return opts


...

# We keep recipe functions in console.py because anything that changes cli_main
# typically has an impact in the recipe parsing process and must be reviewed together.

def load_recipe(recipe_filename):
    """Load commands and comments from a .gwr file.
    
    Supports indented 'chained' lines: If a line begins with whitespace and its first
    non-whitespace characters are `--`, prepend the last full non-indented command prefix.
    
    Example:
        web app setup:
            - web.site --home reader
            - vbox --home upload
            - games.conway --home board --path conway
        web server start-app --host 127.0.0.1 --port 8888

    This parses the indented lines as continuations of the previous non-indented command.
    """
    import os
    from gway import gw

    commands = []
    comments = []
    recipe_path = None

    # --- Recipe file resolution (unchanged) ---
    if not os.path.isabs(recipe_filename):
        candidate_names = []
        base_names = [recipe_filename]
        if "." in recipe_filename:
            base_names.append(recipe_filename.replace(".", "_"))
            base_names.append(recipe_filename.replace(".", os.sep))

        seen = set()
        for base in base_names:
            if base not in seen:
                candidate_names.append(base)
                seen.add(base)
            if not os.path.splitext(base)[1]:
                for ext in (".gwr", ".txt"):
                    name = base + ext
                    if name not in seen:
                        candidate_names.append(name)
                        seen.add(name)

        for name in candidate_names:
            recipe_path = gw.resource("recipes", name)
            if os.path.isfile(recipe_path):
                break
        else:
            abort(f"Recipe not found in recipes/: tried {candidate_names}")
    else:
        recipe_path = recipe_filename
        if not os.path.isfile(recipe_path):
            raise FileNotFoundError(f"Recipe not found: {recipe_path}")

    gw.info(f"Loading commands from recipe: {recipe_path}")
    
    deindented_lines = []
    last_prefix = ""
    colon_prefix = None
    colon_suffix = ""
    with open(recipe_path) as f:
        continuation = None

        def process_line(line: str):
            nonlocal colon_prefix, colon_suffix, last_prefix
            stripped_line = line.lstrip()
            if not stripped_line:
                colon_prefix = None
                return  # skip blank lines
            if stripped_line.startswith("#"):
                comments.append(stripped_line)
                colon_prefix = None
                return
            if colon_prefix:
                if stripped_line.startswith("- "):
                    addition = stripped_line[1:].lstrip()
                    line_to_add = colon_prefix + " " + addition
                    if colon_suffix:
                        line_to_add += " " + colon_suffix
                    deindented_lines.append(line_to_add)
                    return
                if stripped_line.startswith("--"):
                    line_to_add = colon_prefix + " " + stripped_line
                    if colon_suffix:
                        line_to_add += " " + colon_suffix
                    deindented_lines.append(line_to_add)
                    return
                colon_prefix = None
                colon_suffix = ""
            if stripped_line.endswith(":"):
                colon_prefix = stripped_line[:-1].rstrip()
                colon_suffix = ""
                last_prefix = colon_prefix
                return
            # Detect colon inside line after a flag
            no_comment = stripped_line.split("#", 1)[0].rstrip()
            tokens = no_comment.split()
            for idx, token in enumerate(tokens):
                if token.endswith(":"):
                    colon_prefix = " ".join(tokens[:idx + 1])[:-1].rstrip()
                    colon_suffix = " ".join(tokens[idx + 1:])
                    last_prefix = colon_prefix + (" " + colon_suffix if colon_suffix else "")
                    break
            if colon_prefix:
                return
            # Detect if line is indented and starts with '--'
            if line[:1].isspace() and stripped_line.startswith("--"):
                # Prepend previous prefix if available
                if last_prefix:
                    deindented_lines.append(last_prefix + " " + stripped_line)
                else:
                    # Malformed: indented line but no previous command
                    deindented_lines.append(stripped_line)
            else:
                # New command: save everything up to the first '--' (including trailing spaces)
                parts = line.split("--", 1)
                if len(parts) == 2:
                    last_prefix = parts[0].rstrip()
                else:
                    last_prefix = line.rstrip()
                deindented_lines.append(line)

        for raw_line in f:
            line = raw_line.rstrip("\n")
            if continuation is not None:
                line = continuation + line.lstrip()
                continuation = None
            if line.endswith("\\"):
                continuation = line[:-1].rstrip() + " "
                continue
            process_line(line)

        if continuation is not None:
            process_line(continuation.rstrip())

    # --- Split deindented lines into commands ---
    for line in deindented_lines:
        if line.strip() and not line.strip().startswith("#"):
            commands.append(line.strip().split())

    return commands, comments


def normalize_token(token):
    return token.replace("-", "_").replace(" ", "_").replace(".", "_")


def _rows_to_csv(rows):
    if not rows:
        return ""
    try:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
    except Exception:
        return None
    