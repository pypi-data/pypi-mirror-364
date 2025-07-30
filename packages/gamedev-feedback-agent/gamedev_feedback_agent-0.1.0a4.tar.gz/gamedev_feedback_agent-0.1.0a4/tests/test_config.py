import pytest
import os
from dotenv import load_dotenv
import tempfile
from cli.context import get_context
from pathlib import Path
import json

def test_env_file_loading(monkeypatch):

    # Load environment variables from .env file
    
    env_file = tempfile.NamedTemporaryFile(delete=False)
    env_file.write(b"TEST_ENV_VAR=This is a test\n")
    env_file.close()

    # Load the environment variables from the temporary .env file
    load_dotenv(dotenv_path=env_file.name)

    # Check if the environment variable is set correctly
    assert os.getenv("TEST_ENV_VAR") == "This is a test"

def test_env_file_not_found():
    # Test that load_dotenv returns False if the .env file does not exist
    result = load_dotenv(dotenv_path="non_existent_file.env")
    assert result is False
        
    
def test_environment_variables():
    # Check if the environment variables are set correctly
    assert os.getenv("DATABASE_URL") != "" and os.getenv("DATABASE_URL") is not None and os.getenv("DATABASE_URL") != "your_database_url"
    assert os.getenv("REDDIT_CLIENT_ID") != "" and os.getenv("REDDIT_CLIENT_ID") is not None and os.getenv("REDDIT_CLIENT_ID") != "your_client_id"
    assert os.getenv("REDDIT_CLIENT_SECRET") != "" and os.getenv("REDDIT_CLIENT_SECRET") is not None and os.getenv("REDDIT_CLIENT_SECRET") != "your_client_secret"
    assert os.getenv("REDDIT_USER_AGENT") != "" and os.getenv("REDDIT_USER_AGENT") is not None and os.getenv("REDDIT_USER_AGENT") != "your_user_agent"
    assert os.getenv("DISCORD_BOT_TOKEN") != "" and os.getenv("DISCORD_BOT_TOKEN") is not None and os.getenv("DISCORD_BOT_TOKEN") != "your_discord_bot_token"
    
    
def test_database_url_format():
    # Check if the DATABASE_URL is in the correct format
    db_url = os.getenv("DATABASE_URL")
    assert db_url.startswith("postgresql+psycopg2://postgres:") and "@localhost/gdcfa_feedback_agent" in db_url
    
    
    
def test_workspace_directory_creation_with_tmp_path(tmp_path):
    from cli.commands import init_cmd
    
    # remember the original working directory
    global_ptr = Path.home() / ".gdcfa_global.json"
    original_workspace = {}
    try:
        with open(global_ptr, "r", encoding="utf-8") as f:
            original_workspace = json.load(f)
    except Exception as e:
        print("Failed to remember original working directory:", e)
        assert False, "Failed to remember original working directory"

    workspace = tmp_path / "my_temp_ws"
    try:
        init_cmd.handle(["--workspace", str(workspace)])

        assert workspace.exists()
        assert (workspace / "data").exists()
        assert (workspace / "logs").exists()
        assert (workspace / "config.json").exists()
        
        # Check if the global workspace file is updated
        with open(global_ptr, "r", encoding="utf-8") as f:
            updated_workspace = json.load(f)
        assert str(workspace) in updated_workspace["active_workspace"]
    except Exception as e:
        assert False, f"Workspace creation failed: {e}"
    finally:
        # Restore the original workspace
        with open(global_ptr, "w", encoding="utf-8") as f:
            json.dump(original_workspace, f)
        
        # clean up the created workspace directory
        for item in workspace.iterdir():
            if item.is_file():
                item.unlink()
            else:
                for sub_item in item.iterdir():
                    sub_item.unlink()
                item.rmdir()
        workspace.rmdir()
    
    
    
def test_context_initialization():
    from cli.context import load_context, get_context

    # Load the context
    load_context()

    # Get the current context
    context = get_context()

    # Check if the context is initialized correctly
    assert "workspace" in context
    assert "database_url" in context
    assert "data_dir" in context
    assert "log_dir" in context

    # Check if the workspace path is correct
    assert context["workspace"].exists()
    
