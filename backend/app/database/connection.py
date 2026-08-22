"""Database connection and session management"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOCAL_SQLITE_PATH = os.path.join(BASE_DIR, "docuforge.db")


def _build_database_url():
    """Use SQLite for local development unless a valid PostgreSQL URL is configured."""
    configured_url = os.getenv("DATABASE_URL")
    if configured_url and configured_url.startswith("postgresql"):
        try:
            engine = create_engine(configured_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return configured_url, engine
        except Exception:
            pass

    sqlite_url = f"sqlite:///{LOCAL_SQLITE_PATH}"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
    return sqlite_url, sqlite_engine


DATABASE_URL, engine = _build_database_url()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
