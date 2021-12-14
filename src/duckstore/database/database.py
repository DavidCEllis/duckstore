from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

try:
    from greenlet import getcurrent as _scope_func
except ImportError:
    from threading import get_ident as _scope_func

db_session = scoped_session(sessionmaker(), scopefunc=_scope_func)


def get_engine(db_path, *args, **kwargs):
    return create_engine(f"sqlite:///{db_path}", *args, **kwargs)


# noinspection PyUnresolvedReferences
def create_db(db_path, *, replace=False):
    """
    Create a new database
    :param db_path: path to database
    :param replace: Delete a database if it exists
    """
    from .models import Base
    db_path = Path(db_path)

    db_path.parent.mkdir(exist_ok=True)  # Make the folder for the DB if it doesn't exist

    if replace:
        db_path.unlink(missing_ok=True)

    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


def bind_session(db_path):
    """
    Make the global session

    :param db_path:
    """
    engine = get_engine(db_path)
    db_session.configure(bind=engine, autocommit=False, autoflush=False)


def cleanup_session(resp_or_exc):
    """
    Clean up the database on the app
    :param resp_or_exc: response or exception
    """
    db_session.remove()
