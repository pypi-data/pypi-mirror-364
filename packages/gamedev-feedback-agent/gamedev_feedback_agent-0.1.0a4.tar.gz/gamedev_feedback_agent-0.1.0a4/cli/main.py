# cli/main.py

import argparse
from pathlib import Path
from cli.context import load_context
from cli.command_router import route_command
from cli.commands import init_cmd
from cli.shell import GDCFA_Shell
# import sys
# import os

# # Ensure the parent directory is in the path for module imports
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    # Parse command name first
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", help="e.g. init, view, etc.")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parsed = parser.parse_args()

    if parsed.command == "init":
        init_cmd.handle(parsed.args)
        return

    # For all other commands, load workspace context
    try:
        load_context()
    except Exception as e:
        print(f"[Error] Failed to load workspace context: {e}")
        return

    if parsed.command is None:
        GDCFA_Shell().cmdloop()
    else:
        route_command(parsed.command, parsed.args)



if __name__ == "__main__":
    main()