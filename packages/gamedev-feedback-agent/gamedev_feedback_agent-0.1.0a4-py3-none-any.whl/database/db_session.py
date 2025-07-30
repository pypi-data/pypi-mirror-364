# database session management
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
import os

# Database URL, loaded from .env
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")

# Create a SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# debug_engine = create_engine(DATABASE_URL, echo=True)  # For debugging, set echo=True

# Create a configured "Session" class
# Session = sessionmaker(bind=engine)
# debug_Session = sessionmaker(bind=debug_engine)  # For debugging, set echo=True

# Create a scoped session
# session = scoped_session(Session)
# debug_session = scoped_session(debug_Session)  # For debugging, set echo=True


_engine = None
_Session = None
_session = None

_debug_engine = None
_debug_Session = None
_debug_session = None

def get_engine(echo=False):
    global _engine
    if _engine is None:
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        _engine = create_engine(db_url, echo=echo)
    return _engine

def get_session():
    global _Session, _session
    if _Session is None or _session is None:
        engine = get_engine()
        _Session = sessionmaker(bind=engine)
        _session = scoped_session(_Session)
    return _session

def close_session():
    global _session
    if _session:
        try:
            _session.remove()
        except Exception as e:
            print(f"Error closing session: {e}")
            pass
        
def get_debug_engine():
    global _debug_engine
    if _debug_engine is None:
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        _debug_engine = create_engine(db_url, echo=True)  # For debugging, set echo=True
    return _debug_engine

def get_debug_session():
    """
    Returns a scoped session for debugging purposes.
    This ensures that each thread/request gets its own session instance with debug settings.
    """
    global _debug_Session, _debug_session
    if _debug_Session is None or _debug_session is None:
        debug_engine = get_debug_engine()
        _debug_Session = sessionmaker(bind=debug_engine)
        _debug_session = scoped_session(_debug_Session)
    return _debug_session
    
def close_debug_session():
    """
    Closes the current debug session.
    This should be called when the debug session is no longer needed.
    """
    global _debug_session
    if _debug_session:
        try:
            _debug_session.remove()
        except Exception as e:
            print(f"Error closing debug session: {e}")
            pass