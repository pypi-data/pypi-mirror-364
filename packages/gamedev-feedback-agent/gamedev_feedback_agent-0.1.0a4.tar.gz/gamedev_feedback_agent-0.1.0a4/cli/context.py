# cli/context.py

import os
import json
from pathlib import Path

DEFAULT_WORKSPACE = Path.home() / ".gdcfa"
_context = {}

def load_context(workspace_path: Path | None = None) -> None:
    """
    Load config.json and populate shared _context state.
    If no path is given, fallback to default workspace (~/.gdcfa).
    """
    workspace = resolve_workspace(workspace_path)
    config_path = workspace / "config.json"
    
    # load .env if it exists
    env_path = workspace / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)

    if not config_path.exists():
        raise FileNotFoundError(f"[Context] Missing config.json in {workspace}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    _context.update({
        "workspace": Path(config["workspace"]),
        "database_url": os.getenv("DATABASE_URL") or config.get("database_url"),
        "data_dir": Path(config["workspace"]) / "data",
        "log_dir": Path(config["workspace"]) / "logs",
        "resources_dir": Path(config["workspace"]) / "resources",
    })
    
    


def get_context() -> dict:
    """Get the current context.

    Returns:
        dict: The current context.
    """
    return _context


def resolve_workspace(cli_arg: Path | None = None) -> Path:
    """Resolve the workspace directory.

    Args:
        cli_arg (Path | None, optional): The CLI argument for the workspace path. Defaults to None.

    Returns:
        Path: The resolved workspace path.
    """
    if cli_arg:
        return cli_arg

    # Check ~/.gdcfa_global.json
    global_config = Path.home() / ".gdcfa_global.json"
    if global_config.exists():
        try:
            with open(global_config, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Path(data["active_workspace"])
        except Exception:
            pass

    # Default fallback
    return DEFAULT_WORKSPACE

