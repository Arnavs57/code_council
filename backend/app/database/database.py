"""Database connection and session lifecycle management."""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.paths import BACKEND_ROOT

# SQLite database file path (default for dev/local)
DB_PATH = BACKEND_ROOT / "code_council.db"
DATABASE_URL = os.getenv("CCAI_DATABASE_URL", f"sqlite:///{DB_PATH}")

# Connect args for SQLite thread safety
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create all database tables on boot."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """Dependency for providing a database session to API endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
