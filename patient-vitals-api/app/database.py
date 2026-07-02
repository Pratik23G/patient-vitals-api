"""
SQLAlchemy engine, session factory, declarative Base, and the FastAPI DB dependency.

Read this file top-to-bottom once — it's the smallest complete example of how
SQLAlchemy 2.0 wires together, and understanding it is 80% of "knowing the ORM".
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite needs a special flag when used across threads (FastAPI is threaded).
# Postgres does not, so we only add it for sqlite URLs.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

# A session is your "unit of work" — you open one per request, do your reads/writes,
# commit, and close. SessionLocal() gives you a fresh one.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """All ORM models inherit from this. metadata on it knows every table."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency. Yields a session and *always* closes it, even on error.
    Endpoints declare `db: Session = Depends(get_db)` to get one.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
