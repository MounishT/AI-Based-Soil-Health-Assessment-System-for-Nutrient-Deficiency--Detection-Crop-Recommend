"""
database.py
-----------
Database connection and session management for the
AI-Based Soil Health Assessment System.

Uses SQLAlchemy 2.x with a PostgreSQL backend.
All database sessions are managed via dependency injection.
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

from backend.config import settings

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─── SQLAlchemy Engine ────────────────────────────────────────────────────────
# pool_pre_ping=True  → test connections before use (handles stale connections)
# pool_size          → number of persistent connections in the pool
# max_overflow       → extra connections allowed beyond pool_size
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DB_ECHO,          # log SQL statements in debug mode
)


# ─── Session Factory ──────────────────────────────────────────────────────────
# autocommit=False → we control transactions explicitly
# autoflush=False  → flush only on commit / explicit flush
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ─── Declarative Base ─────────────────────────────────────────────────────────
# All ORM models inherit from this Base class.
class Base(DeclarativeBase):
    pass


# ─── Dependency: Get DB Session ───────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a database session per request.
    Guarantees the session is closed after the request completes,
    even if an exception is raised.

    Usage in a router:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()   # roll back on any unhandled exception
        raise
    finally:
        db.close()      # always close the session


# ─── Database Health Check ────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """
    Verify that the database is reachable.
    Called during application startup.

    Returns:
        True  — connection succeeded
        False — connection failed (logs the error)
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("[OK] PostgreSQL connection established successfully.")
        return True
    except OperationalError as exc:
        logger.error("[ERROR] Failed to connect to PostgreSQL: %s", exc)
        return False


# ─── Create All Tables ────────────────────────────────────────────────────────
def init_db() -> None:
    """
    Create all tables defined in the ORM models.
    Should be called once at application startup (via main.py lifespan).

    Note:
        In production, prefer Alembic migrations over create_all().
        create_all() is safe to call repeatedly — it skips existing tables.
    """
    try:
        # Import models here so Base.metadata is populated before create_all()
        from backend import models  # noqa: F401  (side-effect import)

        Base.metadata.create_all(bind=engine)
        logger.info("[OK] All database tables created / verified.")
    except Exception as exc:
        logger.error("[ERROR] Error creating database tables: %s", exc)
        raise
