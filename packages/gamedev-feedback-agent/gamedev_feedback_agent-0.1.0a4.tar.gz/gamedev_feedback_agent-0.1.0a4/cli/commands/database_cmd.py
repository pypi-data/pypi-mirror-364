import argparse
from database.db_bridge import bulk_insert_from_file, export_to_json
from database.db_query_utils import add_row_to_table, get_table_rows
from database.db_session import get_session, close_session
from sqlalchemy.orm import Session
from database.db_models import TABLE_REGISTRY
import sqlalchemy
import json
from cli.context import get_context
import threading
from datetime import datetime
from pathlib import Path

def handle(args) -> None:
    """Handle the database command.

    Args:
        args (list[str]): The arguments for the command.

    Raises:
        ValueError: If the command is invalid or missing required arguments.
    """
    parser = argparse.ArgumentParser(prog="database", description="Database management commands")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # list local json files
    list_json = subparsers.add_parser("list_json", help="List all local JSON files in the data directory")

    # insert_json
    insert_json = subparsers.add_parser("insert_json", help="Import JSON snapshot into the database")
    insert_json.add_argument("--path", required=True, help="Path to JSON snapshot file")
    # insert_json.add_argument("--all", action="store_true", help="Insert all records from the file, not just new ones")
    
    # export_json
    export_json = subparsers.add_parser("export_json", help="Export database tables to JSON files")
    export_json.add_argument("--tables", nargs="+", default=None, help="List of tables to export (default: all tables)")
    export_json.add_argument("--path", required=True, help="Directory to save exported JSON files")

    # add row
    add_row = subparsers.add_parser("add", help="Add a row to a table")
    add_row.add_argument("--table", required=True)
    add_row.add_argument("--values", required=True, help="JSON string representing column values")


    # show table
    show_table = subparsers.add_parser("show", help="View rows from a table")
    show_table.add_argument("--table", required=True)
    show_table.add_argument("--limit", type=int, default=10)

    try:
        parsed = parser.parse_args(args)
    except SystemExit as e:
        print(f"[DB Error] {e} - Invalid command or arguments")
        return

    if parsed.subcommand == "list_json":
        try:
            context = get_context()
            if not context:
                print("[DB Error] No workspace context found. Please initialize the workspace first.")
                return
            data_dir = context.get("data_dir", "data")
            json_files = [f for f in data_dir.glob("*.jsonl")] + [f for f in data_dir.glob("*.json")]
            if not json_files:
                print("[DB] No JSON files found in the data directory.")
            else:
                print("[DB] Local JSON files:")
                for file in json_files:
                    print(f" - {file.name}")
        except Exception as e:
            print(f"[DB Error] {e}")
            return
        
    elif parsed.subcommand == "insert_json":
        try:
            inserted_ids = bulk_insert_from_file(parsed.path)
            if inserted_ids == [-1]:
                print(f"[DB Error] Failed to insert records from {parsed.path}")
            else:
                print(f"[DB] Inserted {len(inserted_ids)} records from {parsed.path}")
        except Exception as e:
            print(f"[DB Error] {e}")

    elif parsed.subcommand == "export_json":
        try:
            table_names = parsed.tables if parsed.tables else list(TABLE_REGISTRY.keys())
            if not table_names:
                print("[DB Error] No tables specified for export and no default tables found in the registry")
                return
            if not isinstance(table_names, list):
                print("[DB Error] --tables argument must be a list of table names")
                return
            if parsed.path is None:
                print("[DB Error] --path argument is required for export")
                return
            # Check that the path ends with .json or .jsonl
            if not isinstance(parsed.path, str) or not parsed.path.strip() or not (parsed.path.endswith(".json") or parsed.path.endswith(".jsonl")):
                print("[DB Error] --path must be a valid JSON file path ending with .json or .jsonl")
                return
            # get workspace path
            context = get_context()
            if not context:
                print("[DB Error] No workspace context found. Please initialize the workspace first.")
                return
            workspace_path = context.get("workspace", Path.cwd())
            output_path = Path(parsed.path)
            if not output_path.is_absolute():
                output_path = workspace_path / output_path

            result = export_to_json(table_names, output_path)
            if result:
                print(f"[DB] Exported tables to JSON files in {output_path}")
            else:
                print("[DB Error] Failed to export tables to JSON")
        except Exception as e:
            print(f"[DB Error] {e}")

    elif parsed.subcommand == "add":
        session = None
        try:
            values_dict = None
            values_dict = get_values_dict(parsed.values)
            if not values_dict:
                raise ValueError("No valid values provided for the new row")
            
            # Validate table name
            if parsed.table.lower() not in TABLE_REGISTRY:
                raise ValueError(f"Table '{parsed.table}' not found in the database schema")

            # Validate column names
            model_class = TABLE_REGISTRY[parsed.table.lower()]
            for col in model_class.__table__.columns:
                if col.name not in values_dict:
                    if col.nullable or col.default is not None or col.primary_key:
                        continue
                    raise ValueError(f"Missing value for column '{col.name}'")

            model_class = TABLE_REGISTRY[parsed.table.lower()]
            session = get_session()
            new_row = model_class(**values_dict)
            session.add(new_row)
            session.commit()
            print(f"[DB] Added new row to '{parsed.table}': {values_dict}")
        except Exception as e:
            print(f"[DB Error] {e}")
        finally:
            close_session()


    elif parsed.subcommand == "show":
        session = get_session()
        try:
            rows = get_table_rows(session, parsed.table, parsed.limit)
            if not rows:
                print(f"[DB] No rows found in '{parsed.table}'")
            else:
                for row in rows:
                    # format the row output nicely
                    row_data = {col.name: getattr(row, col.name) for col in row.__table__.columns}
                    print(row_data)
        except Exception as e:
            print(f"[DB Error] {e}")
        finally:
            close_session()


def get_values_dict(prompt: str) -> dict:
    """Validate and get a dictionary of values for a new row.

    Returns:
        dict: A dictionary containing the column names and user-provided values for the new row.
    """
    # parse the input as name=value pairs
    values_dict = {}
    for pair in prompt.split(","):
        try:
            key, value = pair.split("=")
            values_dict[key.strip()] = value.strip()
        except ValueError:
            continue
    return values_dict


