from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger("healthcare_platform.database")

# Build engine kwargs based on dialect
db_url = settings.DATABASE_URL
engine_kwargs = {}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        echo=settings.DEBUG,
        **engine_kwargs
    )
    logger.info(f"Database engine created successfully for URL dialect: {db_url.split(':')[0]}")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session per request
    and ensures proper closing upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
