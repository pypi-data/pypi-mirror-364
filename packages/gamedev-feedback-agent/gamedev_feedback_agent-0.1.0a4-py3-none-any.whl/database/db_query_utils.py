# Database query utility functions


from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from database.db_models import Base
from database.db_models import TABLE_REGISTRY
from database.db_session import get_session, close_session

# add a row to a table
def add_row_to_table(session: Session, table_name: str, values: dict) -> object:
    """Add a new row to the specified table.

    Args:
        session (Session): The database session.
        table_name (str): The name of the table to add the row to.
        values (dict): The values for the new row.

    Raises:
        ValueError: If table_name is empty or values are not provided.

    Returns:
        object: The newly created row object.
    """
    try:
        model_class = TABLE_REGISTRY.get(table_name.lower())
        if not model_class:
            raise ValueError(f"[DB] No model registered for table '{table_name}'")

        new_row = model_class(**values)
        session.add(new_row)
        session.commit()
        return new_row
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def get_table_rows(session: Session, table_name: str, limit: int = 100) -> list[object]:
    """Get rows from the specified table.

    Args:
        session (Session): The database session.
        table_name (str): The name of the table to get rows from.
        limit (int, optional): The maximum number of rows to retrieve. Defaults to 100.

    Raises:
        ValueError: If table_name is empty or limit is not positive.

    Returns:
        list[object]: A list of rows from the specified table.
    """
    try:
        model_class = TABLE_REGISTRY.get(table_name.lower())
        if not model_class:
            raise ValueError(f"[DB] No model registered for table '{table_name}'")

        rows = session.query(model_class).limit(limit).all()
        return rows
    except Exception as e:
        raise
    finally:
        session.close()
