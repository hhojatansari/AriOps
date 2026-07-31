"""SQLAlchemy engine and request-scoped database sessions."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ariops.config import settings


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Create the configured PostgreSQL session factory once per process."""
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Yield one database session for an HTTP request."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
