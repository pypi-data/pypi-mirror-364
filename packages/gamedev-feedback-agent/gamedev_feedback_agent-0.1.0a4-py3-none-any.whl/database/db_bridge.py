# db/bridge.py

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.db_models import Base, Platform, Author, Post, Game, Tag, GamePost, PostTag, Alert, Analysis, Embedding
from database.db_models import TABLE_REGISTRY
from threading import Thread
from database.db_session import get_session, close_session
from intelligence.process import process_post
from datetime import datetime
from dotenv import load_dotenv
import os
from cli.context import get_context
from pathlib import Path

# load from .env file

def get_or_create_platform(session: Session, name: str) -> Platform:
    """Get or create a platform.

    Args:
        session (Session): The database session.
        name (str): The name of the platform.

    Returns:
        Platform: The platform object.
    """
    platform = session.query(Platform).filter_by(name=name).first()
    if not platform:
        platform = Platform(name=name)
        session.add(platform)
        session.commit()
    return platform


def get_or_create_author(session: Session, username: str, platform_id: int) -> Author:
    """Get or create an author.

    Args:
        session (Session): The database session.
        username (str): The username of the author.
        platform_id (int): The ID of the platform.

    Returns:
        Author: The author object.
    """
    author = session.query(Author).filter_by(username=username, platform_id=platform_id).first()
    if not author:
        author = Author(username=username, platform_id=platform_id, created_at=datetime.utcnow())
        session.add(author)
        session.commit()
    return author


# convert json data to Post
def insert_post_from_json(session: Session, data: dict) -> tuple[str, int]:
    """Insert a post into the database from JSON data.

    Args:
        session (Session): The database session.
        data (dict): The JSON data.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        # Validate required fields
        required_fields = ["id", "platform", "author", "content", "type", "timestamp"]
        for field in required_fields:
            if field not in data:
                return -1, f"Missing required field: {field}"
        external_id = data.get("id")
        platform = get_or_create_platform(session, data["platform"])
        author = get_or_create_author(session, data["author"], platform.platform_id)

        # Check for duplicates
        existing = session.query(Post).filter_by(
            external_post_id=external_id,
            platform_id=platform.platform_id
        ).first()
        if existing:
            return -1, f"Skipped duplicate post {external_id} on platform {platform.name}"
        
        # initialize post fields
        _parent_id = None
        _source_id = None
        _upvotes = None
        _downvotes = None
        _replies = None
        _playtime_forever = None
        _metadata = {}

        # extract data and convert to post
        if data["platform"] == "reddit":
            _source_id = data.get("metadata", {}).get("subreddit")
            _upvotes = data.get("metadata", {}).get("upvotes")
            _downvotes = data.get("metadata", {}).get("downvotes")
            _replies = data.get("metadata", {}).get("num_comments") if data["type"] == "reddit_post" else data.get("metadata", {}).get("num_replies")
            _parent_id = data.get("metadata", {}).get("parent_id") if data["type"] == "reddit_comment" else None
            _metadata = {
                "depth": data.get("metadata", {}).get("depth"),
            } if data["type"] == "reddit_comment" else {}
            
        elif data["platform"] == "steam" and data["type"] == "steam_review":
            _source_id = data.get("metadata", {}).get("app_id")
            _upvotes = data.get("metadata", {}).get("votes_up") 
            _playtime_forever = data.get("metadata", {}).get("playtime_forever")
            _metadata = {
                "voted_up": data.get("metadata", {}).get("voted_up"),
                "votes_funny": data.get("metadata", {}).get("votes_funny"),
                "weighted_vote_score": data.get("metadata", {}).get("weighted_vote_score"),
            }
            
        elif data["platform"] == "steam" and data["type"] == "steam_discussion_thread":
            _source_id = data.get("metadata", {}).get("app_id")
            _replies = data.get("metadata", {}).get("replies")
            
        elif data["platform"] == "steam" and data["type"] == "steam_discussion_comment":
            _source_id = data.get("metadata", {}).get("app_id")
            _parent_id = data.get("metadata", {}).get("thread_id")
        elif data["platform"] == "discord":
            _source_id = data.get("metadata", {}).get("channel_id")
            _replies = data.get("metadata", {}).get("reactions_count", 0)  # Discord comments don't have upvotes/downvotes
            _metadata = {
                "server_id": data.get("metadata", {}).get("server_id"),
                "mentioned_users": data.get("raw_data", {}).get("mentions", []),
                "pinned": data.get("metadata", {}).get("pinned"),
                "is_reply": data.get("metadata", {}).get("is_reply", False),
            }
            
        # get parent post by querying the database
        _parent_post_id = None
        if _parent_id:
            _parent_post_id_tuple = session.query(Post.post_id).filter_by(
                external_post_id=_parent_id,
                platform_id=platform.platform_id
            ).first()
            if _parent_post_id_tuple:
                _parent_post_id = _parent_post_id_tuple[0]


        
        post = Post(
            platform_id = platform.platform_id,
            author_id = author.author_id,
            content = data.get("content"),
            external_post_id = external_id,
            post_type = data.get("type"),
            parent_post_id = _parent_post_id,
            timestamp = data.get("timestamp"),
            url = data.get("source_url"),

            source_id = _source_id,
            upvotes = _upvotes,
            downvotes = _downvotes,
            replies = _replies,
            playtime_forever = _playtime_forever,
            
            post_metadata = _metadata
        )
    
        # Add the post to the session and commit
        session.add(post)
        session.commit()
        post_id = post.post_id
        return post_id, f"Inserted post {post.external_post_id}"
    except Exception as e:
        session.rollback()
        return -1, f"Error inserting post: {e}"



def bulk_insert_from_file(file_path: str) -> list[int]:
    """Bulk insert posts into the database from a JSON lines file.

    Args:
        file_path (str): The path to the JSON lines file.
        
    Returns:
        int: The number of records inserted.
    """
    session = get_session()
    # get workspace context
    _context = get_context()
    if not _context:
        print("No workspace context found. Please initialize the workspace first.")
        return [-1]
    # get data directory from context
    data_dir = _context.get("data_dir", "data")
    full_path = Path(file_path)
    if not full_path.is_absolute():
        # if relative path, make it absolute
        full_path = data_dir / full_path.name

    # check if file exists
    if not os.path.exists(full_path):
        print(f"File {full_path} does not exist.")
        return [-1]
    # check if file is empty
    if os.path.getsize(full_path) == 0:
        print(f"File {full_path} is empty.")
        return [-1]
    # check if file is a valid JSON lines file
    if not full_path.suffix in [".jsonl", ".json"]:
        print(f"File {full_path} is not a valid JSON lines file. Supported formats: .jsonl, .json")
        return [-1]

    inserted_count = 0
    try:
        results = []
        post_ids = set()  # to track inserted post IDs
        
        with open(full_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                # check if line is a valid JSON
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    results.append(f"[Line {line_number}] Malformed JSON: {e}")
                    continue
                
                # insert the post from JSON data
                if not isinstance(data, dict):
                    results.append(f"[Line {line_number}] Error: Expected a JSON object, got {type(data).__name__}")
                    continue
                try:
                    post_id, result = insert_post_from_json(session, data)
                    if "Inserted post" in result and post_id != -1:
                        post_ids.add(post_id)
                        inserted_count += 1
                    results.append(f"[Line {line_number}] {result}")
                except Exception as inner_e:
                    results.append(f"[Line {line_number}] Error: {inner_e}")
        print("\n".join(results))
        # Return the number of successful inserts

        
    except Exception as e:
        print(f"Failed to process file {full_path}: {e}")
    finally:
        close_session()
    return list(post_ids) if post_ids else [-1]



def export_to_json(table_names: list[str], file_path: str) -> bool:
    """Export data from specified tables to a JSON file.

    Args:
        table_names (list[str]): The names of the tables to export.
        file_path (str): The path to the output JSON file.

    Raises:
        ValueError: If table_names is empty or file_path is not provided.
        ValueError: If no table is found for a given table_name.

    Returns:
        bool: True if export was successful, False otherwise.
    """
    session = get_session()
    if not table_names or not file_path:
        raise ValueError("Both table_names and file_path must be provided")
    try:
        success = True
        with open(file_path, "a", encoding="utf-8") as f:
            for table_name in table_names:
                model_class = TABLE_REGISTRY.get(table_name.lower())
                if not model_class:
                    raise ValueError(f"No table found for {table_name}")

                rows = session.query(model_class).all()
                
                
                for row in rows:
                    row_data = {}
                    for col in model_class.__table__.columns:
                        col_name = col.name      # The DB column name (e.g. "metadata")
                        attr_name = col.key      # The Python attribute (e.g. "game_metadata")
                        if col_name == "metadata":
                            # Special handling for JSONB columns
                            row_data[col_name] = getattr(row, attr_name, {})
                        else:
                            try:
                                row_data[col_name] = getattr(row, attr_name)
                            except Exception as e:
                                print(f"[ERROR] Failed to access column {col_name}: {e}")
                                success = False
                                raise Exception(f"Failed to access column {col_name} in table {table_name}")
                            
                                
                    try:
                        f.write(json.dumps(row_data, ensure_ascii=False) + "\n")
                    except TypeError as te:
                        print(f"[ERROR] Row serialization failed: {row_data}")
                        success = False
                        raise TypeError(f"Failed to serialize row data for table {table_name}: {te}")
                    except Exception as e:
                        print(f"[ERROR] Unexpected error: {e}")
                        success = False
                print(f"Exporting {len(rows)} rows from {table_name} to {file_path}")
        return success
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False
    finally:
        close_session()
    return success


def trigger_background_analysis(post_ids):
    def analyze_func():
        session = get_session()
        for pid in post_ids:
            try:
                post = session.query(Post).filter_by(post_id=pid).first()
                if post:
                    process_post(session, post)
                    post.processed = True
            except Exception as e:
                print(f"[Analyze Error] {pid}: {e}")
        session.commit()

    thread = Thread(target=analyze_func, daemon=True)
    thread.start()