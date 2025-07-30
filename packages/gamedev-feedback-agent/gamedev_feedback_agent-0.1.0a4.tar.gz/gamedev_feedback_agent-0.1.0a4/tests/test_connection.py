from pathlib import Path
from cli.context import get_context
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 1. test database connection failure
def test_database_connection_failure():
    # will be added after a centralized database connection is implemented
    pass