# cli/commands/init_cmd.py

import argparse
import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

DEFAULT_WORKSPACE = Path.home() / ".gdcfa"
CONFIG_FILENAME = "config.json"
DOTENV_FILENAME = ".env"

def handle(args: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="gdcfa init")
    parser.add_argument("--workspace", type=str, help="Path to workspace directory")
    parser.add_argument("--database", type=str, help="Database URL (e.g. postgresql://...)")
    parser.add_argument("--config", type=str, help="Path to an existing config.json")

    parsed = parser.parse_args(args)

    if parsed.config:
        print(f"[Init] Loading config from {parsed.config}")
        try:
            with open(parsed.config, "r", encoding="utf-8") as f:
                config = json.load(f)
            print("[Init] Loaded config:")
            print(json.dumps(config, indent=2))
        except Exception as e:
            print(f"[Init Error] Failed to load config: {e}")
        return

    if parsed.workspace:
        print(f"[Init] Using specified workspace: {parsed.workspace}")
        workspace = Path(parsed.workspace)
    else:
        print("[Init] No workspace specified, using default: ~/.gdcfa")
        # Use default workspace if not specified
        workspace = DEFAULT_WORKSPACE
    
    workspace.mkdir(parents=True, exist_ok=True)

    # Create required subfolders
    for sub in ["data", "logs", "resources"]:
        (workspace / sub).mkdir(parents=True, exist_ok=True)

    # Load .env if it exists
    dotenv_path = workspace / DOTENV_FILENAME
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"[Init] Loaded environment variables from {dotenv_path}")
    else:
        print(f"[Init] No .env file found in {workspace}. You may create one to set API keys.")

    # Determine DB URL
    db_url = parsed.database or os.getenv("DATABASE_URL") or "postgresql+psycopg2://postgres:123456@localhost/postgres"

    config = {
        "workspace": str(workspace.resolve()),
        "database_url": db_url
    }

    try:
        config_path = workspace / CONFIG_FILENAME
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"[Init] Workspace initialized at: {workspace}")
        print(f"[Init] Config written to: {config_path}")
        print(f"[Init] Database URL: {db_url}")
    except Exception as e:
        print(f"[Init Error] Failed to write config: {e}")
        
    # save to global "active workspace" pointer
    global_ptr = Path.home() / ".gdcfa_global.json"
    try:
        with open(global_ptr, "w", encoding="utf-8") as f:
            json.dump({"active_workspace": str(workspace.resolve())}, f)
        print(f"[Init] Set default workspace: {workspace.resolve()}")
    except Exception as e:
        print(f"[Init] Failed to set global default workspace: {e}")

        
    print("[Init] Initialization complete. Run 'gdcfa' to start the CLI.")
