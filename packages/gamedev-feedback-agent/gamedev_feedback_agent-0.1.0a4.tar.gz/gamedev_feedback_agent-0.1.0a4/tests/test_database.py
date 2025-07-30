import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database.db_models import Base, Platform, Author, Post, Game, Alert, Tag, PostTag, GamePost, TABLE_REGISTRY
import re
from sqlalchemy import String, Integer, Float, Text, UniqueConstraint
from database.db_query_utils import add_row_to_table, get_table_rows
from unittest.mock import MagicMock
from database.db_bridge import get_or_create_platform, get_or_create_author, insert_post_from_json, bulk_insert_from_file, export_to_json
import json
from unittest.mock import mock_open, patch
from pathlib import Path
from cli.context import get_context
from threading import Thread
from database.db_bridge import trigger_background_analysis
from unittest.mock import patch, MagicMock
import importlib


@pytest.fixture(scope='module')
def schema_read():
    schema_file = 'database/schema.sql'
    with open(schema_file, 'r') as file:
        schema_content = file.read()
    normalized_sql = " ".join(schema_content.lower().split())
    return normalized_sql

# fixture a context with workspace, data_dir
@pytest.fixture(scope='module')
def workspace_context():
    context = {
        "data_dir": Path("data")
    }
    with patch("cli.context.get_context", return_value=context):
        return context


# 1. test compare table name with schema.sql
# directly compare the table names with the schema.sql file
def test_table_names(schema_read):
    normalized_sql = schema_read

    # get expected table from db_models.py
    expected_tables = [table.name for table in Base.metadata.sorted_tables]

    for table_name in expected_tables:
        assert f'create table {table_name.lower()}' in normalized_sql

    missing = [t for t in expected_tables if f'create table {t.lower()}' not in normalized_sql]
    assert not missing, f"Missing tables in schema.sql: {missing}"


# 2. test compare column definitions
def test_column_definitions(schema_read):
    schema = schema_read

    for table in Base.metadata.sorted_tables:
        table_name = table.name.lower()
        match = re.search(rf'create table "?{table_name}"?\s*\((.*?)\);', schema, re.DOTALL)
        assert match, f"Table {table_name} not found in schema.sql"

        schema_cols = match.group(1)
        for column in table.columns:
            col_name = column.name.lower()
            assert col_name in schema_cols, f"Column '{col_name}' missing in table '{table_name}'"

            # Optional: check basic type (simple heuristic)
            col_type = str(column.type).lower()
            if isinstance(column.type, (String, Text)):
                assert "text" in schema_cols or "varchar" in schema_cols
            elif isinstance(column.type, Integer):
                assert any(x in schema_cols for x in ["int", "integer", "serial", "bigint"]), \
                    f"Column '{col_name}' in '{table_name}' should be an integer type"
            elif isinstance(column.type, Float):
                assert "float" in schema_cols or "real" in schema_cols
                


# 3. test constraints and foreign keys
def test_constraints(schema_read):
    schema = schema_read

    for table in Base.metadata.sorted_tables:
        for constraint in table.constraints:
            if hasattr(constraint, "columns") and constraint.columns:
                col_names = [c.name.lower() for c in constraint.columns]
                if constraint.name and "unique" in constraint.name.lower():
                    for col in col_names:
                        assert f'unique({col}' in schema or col in schema and "unique" in schema, f"Missing UNIQUE constraint for {col}"
        
        for fk in table.foreign_keys:
            print(fk)
            source_col = fk.parent.name.lower()             # e.g., parent_post_id
            target_col = fk.column.name.lower()             # e.g., post_id
            target_table = fk.column.table.name.lower()     # e.g., post
            
            type_name = str(fk.column.type).lower()

            # Check for the pattern: column_name <type> REFERENCES referenced_table(referenced_column)
            # check if column is in the same line as the REFERENCES clause
            assert f'{source_col} {type_name} references {target_table}({target_col})' in schema, \
                f"Missing foreign key constraint for {source_col} referencing {target_table}({target_col})"
        

# 4. test database query utils
def test_database_query_utils():
    # Register model
    TABLE_REGISTRY["platform"] = Platform

    # ----- Test add_row_to_table (success) -----
    success_session = MagicMock()
    row = add_row_to_table(success_session, "platform", {"name": "mocked_platform"})

    assert isinstance(row, Platform)
    assert row.name == "mocked_platform"
    success_session.add.assert_called_once_with(row)
    success_session.commit.assert_called_once()

    # ----- Test add_row_to_table (commit failure) -----
    fail_session = MagicMock()
    fail_session.commit.side_effect = Exception("DB commit failed")

    with pytest.raises(Exception, match="DB commit failed"):
        add_row_to_table(fail_session, "platform", {"name": "fail"})

    fail_session.add.assert_called_once()
    fail_session.commit.assert_called_once()

    # ----- Test get_table_rows -----
    mock_query_result = [Platform(name="p1"), Platform(name="p2")]
    get_session = MagicMock()
    get_session.query.return_value.limit.return_value.all.return_value = mock_query_result

    results = get_table_rows(get_session, "platform", limit=2)

    get_session.query.assert_called_once_with(Platform)
    get_session.query.return_value.limit.assert_called_once_with(2)
    assert len(results) == 2
    assert results[0].name == "p1"
    
    
# 5. test bridge functions get_or_create_platform, get_or_create_author, insert_post_from_json
def test_db_bridge_functions():
    mock_session = MagicMock()

    # -------- get_or_create_platform --------
    mock_session.query().filter_by().first.return_value = None
    platform = get_or_create_platform(mock_session, "reddit")
    assert isinstance(platform, Platform)
    assert platform.name == "reddit"
    mock_session.add.assert_called_with(platform)
    mock_session.commit.assert_called()

    # reset
    mock_session.reset_mock()

    # -------- get_or_create_author --------
    mock_session.query().filter_by().first.return_value = None
    author = get_or_create_author(mock_session, "alice", 1)
    assert isinstance(author, Author)
    assert author.username == "alice"
    assert author.platform_id == 1
    mock_session.add.assert_called_with(author)
    mock_session.commit.assert_called()

    # reset
    mock_session.reset_mock()

    # -------- insert_post_from_json (success) --------
    # mock_session.query().filter_by().first.side_effect = [  # platform, author, duplicate post check, parent lookup
    #     None,  # platform not found
    #     None,  # author not found
    #     None,  # post is not a duplicate
    #     None   # parent post not found
    # ]
    mock_session.query().filter_by().first.side_effect = [None] * 12  # 3x 4 calls for each query

    sample_data = {
        "id": "abc123",
        "platform": "reddit",
        "author": "alice",
        "type": "reddit_post",
        "content": "hello world",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_url": "https://reddit.com/test",
        "metadata": {
            "subreddit": "gamedev",
            "upvotes": 42,
            "downvotes": 3,
            "num_comments": 2
        },
        "raw_data": {}
    }
    
    sample_data2 = {
        "id": "def456",
        "platform": "steam",
        "author": "bob",
        "type": "steam_review",
        "content": "hello world2",
        "timestamp": "2025-01-01T10:00:00Z",
        "source_url": "https://steamcommunity.com/app/123456/reviews",
        "metadata": {
            "app_id": "123456",
            "votes_up": 100,
            "playtime_forever": 3600,
            "voted_up": True,
            "votes_funny": 10,
            "weighted_vote_score": 0.8
        },
        "raw_data": {}
    }
    
    sample_data3 = {
        "id": "ghi789",
        "platform": "discord",
        "author": "charlie",
        "type": "discord_message",
        "content": "hello world3",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_url": "https://discord.com/channels/123/456/789",
        "metadata": {
            "channel_id": "123",
            "server_id": "456",
            "mentioned_users": ["user1", "user2"],
            "pinned": False
        },
        "raw_data": {}
    }

    result = insert_post_from_json(mock_session, sample_data)
    assert "Inserted post abc123" in result
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.add.reset_mock()
    mock_session.commit.reset_mock()
    mock_session.reset_mock()

    result2 = insert_post_from_json(mock_session, sample_data2)
    assert "Inserted post def456" in result2
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.add.reset_mock()
    mock_session.commit.reset_mock()
    mock_session.reset_mock()
    

    result3 = insert_post_from_json(mock_session, sample_data3)
    assert "Inserted post ghi789" in result3
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.add.reset_mock()
    mock_session.commit.reset_mock()
    mock_session.reset_mock()

    mock_session.reset_mock()
    mock_session.query().filter_by().first.side_effect = Exception("DB failure")
    post_id, fail_result = insert_post_from_json(mock_session, sample_data)
    assert "Error inserting post" in fail_result and post_id == -1
    mock_session.rollback.assert_called()
    
    
# 6. test bulk_insert_from_file
def test_bulk_insert_from_file(capsys):
    # --- Mock JSON content: one good, one malformed ---
    good_entry = {
        "id": "test123",
        "platform": "reddit",
        "author": "user",
        "type": "reddit_post",
        "content": "Test content",
        "timestamp": "2025-01-01T00:00:00Z",
        "source_url": "https://reddit.com",
        "metadata": {},
        "raw_data": {}
    }
    bad_line = '{"id": "malformed" '  # invalid JSON
    mock_file_data = f"{json.dumps(good_entry)}\n{bad_line}\n"
    
    # test if workspace context is set
    with patch("database.db_bridge.get_context", return_value=None):
        result = bulk_insert_from_file("nonexistent.json")
        captured = capsys.readouterr()
        assert result == [-1]
        assert "No workspace context found. Please initialize the workspace first." in captured.out
    
    # test if file not exists
    with patch("database.db_bridge.get_context", return_value={"data_dir": Path(".")}):
        result = bulk_insert_from_file("nonexistent.json")
        captured = capsys.readouterr()
        assert result == [-1]
        assert "File nonexistent.json does not exist." in captured.out
        
        
    # test if file is empty
    with patch("database.db_bridge.get_context", return_value={"data_dir": Path(".")}), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=0):
        result = bulk_insert_from_file("empty.json")
        captured = capsys.readouterr()
        assert result == [-1]
        assert "File empty.json is empty." in captured.out

    # test if file is not a valid JSON lines file
    with patch("database.db_bridge.get_context", return_value={"data_dir": Path(".")}), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=100):
        result = bulk_insert_from_file("nonexistent.txt")
        captured = capsys.readouterr()
        assert result == [-1]
        assert "File nonexistent.txt is not a valid JSON lines file. Supported formats: .jsonl, .json" in captured.out

    # Patch everything needed to pass prechecks
    with patch("builtins.open", mock_open(read_data=mock_file_data)), \
         patch("database.db_bridge.get_session") as mock_Session, \
         patch("database.db_bridge.insert_post_from_json", return_value="Inserted post") as mock_insert, \
         patch("database.db_bridge.get_context", return_value={"data_dir": Path(".")}), \
         patch("os.path.exists", return_value=True), \
         patch("os.path.getsize", return_value=100):

        # Mock session instance
        mock_session_instance = MagicMock()
        mock_Session.return_value = mock_session_instance

        # Act
        result = bulk_insert_from_file("fake.json")

        # Assert
        assert len(result) == 1  # Only one valid insert
        mock_Session.assert_called_once()
        mock_insert.assert_called_once()
        args, _ = mock_insert.call_args
        assert args[0] == mock_session_instance
        assert args[1]["id"] == "test123"
        

# # 7. test export_to_json
def test_export_to_json_mocked(tmp_path):
    # Prepare a mock Post object
    mock_post = MagicMock(spec=Post)
    mock_post.post_id = 1
    mock_post.platform_id = 1
    mock_post.author_id = 1
    mock_post.content = "Mocked Post"
    mock_post.language = "en"
    mock_post.language_confidence = 0.99
    mock_post.translated_content = None
    mock_post.external_post_id = "abc123"
    mock_post.post_type = "reddit_post"
    mock_post.parent_post_id = None
    mock_post.timestamp = "2025-07-01T10:00:00Z"
    mock_post.url = "https://reddit.com/post/abc123"
    mock_post.source_id = 1
    mock_post.upvotes = 100
    mock_post.downvotes = 5
    mock_post.replies = 2
    mock_post.playtime_forever = None
    mock_post.post_metadata = {"subreddit": "gaming"}
    
    failed_mock_post = MagicMock(spec=Post)
    failed_mock_post.post_id = 2

    # Patch DB_Session, TABLE_REGISTRY, and get_context
    with patch("database.db_bridge.get_session") as mock_session_class, \
         patch("database.db_bridge.TABLE_REGISTRY", {"post": Post}), \
         patch("database.db_bridge.get_context", return_value={"workspace": Path("."), "data_dir": Path("./data")}):
        mock_session = mock_session_class.return_value
        mock_session.query.return_value.all.return_value = [mock_post]

        export_path = tmp_path / "test_mocked_export.json"
        success = export_to_json(["post"], str(export_path))

        assert success is True
        assert export_path.exists()
        with open(export_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["content"] == "Mocked Post"
            assert data["upvotes"] == 100
            
        fail_export_path = tmp_path / "test_mocked_export_fail.json"
        mock_session.query.return_value.all.return_value = [failed_mock_post]
        fail_success = export_to_json(["post"], str(fail_export_path))

        assert fail_success is False
        assert fail_export_path.exists()
        with open(fail_export_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 0






# 8. test trigger_background_process
def test_trigger_background_process(capsys):
    def dummy_process_post(session, post):
        post.processed = True

    with patch("database.db_bridge.Thread") as mock_thread, \
         patch("database.db_bridge.get_session") as mock_get_session, \
         patch("database.db_bridge.Post") as mock_Post, \
         patch("database.db_bridge.process_post", side_effect=dummy_process_post):

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Mock post object for the first run
        mock_post = MagicMock()
        mock_post.processed = False
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_post

        # First test: normal run
        trigger_background_analysis([1, 2, 3])

        # Grab the thread target and call it
        args, kwargs = mock_thread.call_args
        thread_target = kwargs.get("target") or args[0]
        thread_target()

        assert mock_session.query.return_value.filter_by.return_value.first.call_count == 3
        assert mock_post.processed is True
        mock_session.commit.assert_called_once()

        # Now simulate DB error
        def side_effect_failure(*_, **__):
            raise Exception("DB error")

        mock_session.query.return_value.filter_by.return_value.first.side_effect = side_effect_failure

        # Reset mock_thread so we can capture the new call
        mock_thread.reset_mock()
        trigger_background_analysis([4])

        # Get second thread and call its target manually
        args, kwargs = mock_thread.call_args
        thread_target = kwargs.get("target") or args[0]
        thread_target()

        # Capture printed output
        out = capsys.readouterr()
        assert "[Analyze Error] 4" in out.out


        
# 9. test database session management
import database.db_session as db_session_mod
def test_get_session_returns_scoped_session():
    # Patch the global 'session' object
    with patch.object(db_session_mod, "session", autospec=True) as mock_session:
        result = db_session_mod.get_session()
        assert result is mock_session

def test_get_debug_session_returns_scoped_session():
    with patch.object(db_session_mod, "debug_session", autospec=True) as mock_debug_session:
        result = db_session_mod.get_debug_session()
        assert result is mock_debug_session

def test_close_session_success():
    with patch.object(db_session_mod, "session", autospec=True) as mock_session:
        db_session_mod.close_session()
        mock_session.remove.assert_called_once()

def test_close_session_exception_prints_error(capsys):
    with patch.object(db_session_mod, "session", autospec=True) as mock_session:
        mock_session.remove.side_effect = Exception("fail")
        db_session_mod.close_session()
        out = capsys.readouterr()
        assert "[Database Session Closing ERROR]" in out.out

def test_close_debug_session_success():
    with patch.object(db_session_mod, "debug_session", autospec=True) as mock_debug_session:
        db_session_mod.close_debug_session()
        mock_debug_session.remove.assert_called_once()

