"""
Database management and connection handling for the Legal Document Analyzer.
Provides database initialization, session management, and utility functions.
"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import sqlite3

from src.config import config
from src.utils import logger
from .models import Base


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database engine and session factory."""
        try:
            # Create engine with appropriate configuration
            if config.DATABASE_URL.startswith("sqlite"):
                self.engine = create_engine(
                    config.DATABASE_URL,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=config.LOG_LEVEL == "DEBUG"
                )
                
                # Enable WAL mode for SQLite for better concurrency
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    if isinstance(dbapi_connection, sqlite3.Connection):
                        cursor = dbapi_connection.cursor()
                        cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute("PRAGMA synchronous=NORMAL")
                        cursor.execute("PRAGMA cache_size=10000")
                        cursor.execute("PRAGMA temp_store=MEMORY")
                        cursor.close()
            else:
                self.engine = create_engine(
                    config.DATABASE_URL,
                    pool_pre_ping=True,
                    echo=config.LOG_LEVEL == "DEBUG"
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized: {config.DATABASE_URL}")
            
        except Exception as e:
            logger.error("Failed to initialize database", exception=e)
            raise
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Failed to create database tables", exception=e)
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error("Failed to drop database tables", exception=e)
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Database session error", exception=e)
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get a synchronous database session (remember to close it)."""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check if database is accessible."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", exception=e)
            return False
    
    def get_database_info(self) -> dict:
        """Get database information and statistics."""
        try:
            with self.get_session() as session:
                # Get table information
                if config.DATABASE_URL.startswith("sqlite"):
                    tables_result = session.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                    tables = [row[0] for row in tables_result]
                    
                    # Get database size
                    size_result = session.execute("PRAGMA page_count").fetchone()
                    page_size_result = session.execute("PRAGMA page_size").fetchone()
                    db_size = (size_result[0] * page_size_result[0]) if size_result and page_size_result else 0
                else:
                    tables = []
                    db_size = 0
                
                return {
                    "url": config.DATABASE_URL,
                    "tables": tables,
                    "size_bytes": db_size,
                    "healthy": True
                }
        except Exception as e:
            logger.error("Failed to get database info", exception=e)
            return {
                "url": config.DATABASE_URL,
                "tables": [],
                "size_bytes": 0,
                "healthy": False,
                "error": str(e)
            }


# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db() -> Generator[Session, None, None]:
    """Dependency function for getting database sessions."""
    with db_manager.get_session() as session:
        yield session

def init_database():
    """Initialize database and create tables."""
    try:
        config.create_directories()
        db_manager.create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error("Database initialization failed", exception=e)
        raise

def reset_database():
    """Reset database by dropping and recreating all tables."""
    try:
        logger.warning("Resetting database - all data will be lost!")
        db_manager.drop_tables()
        db_manager.create_tables()
        logger.info("Database reset completed")
    except Exception as e:
        logger.error("Database reset failed", exception=e)
        raise

# Database session decorator
def with_db_session(func):
    """Decorator to automatically provide database session to functions."""
    def wrapper(*args, **kwargs):
        with db_manager.get_session() as session:
            return func(session, *args, **kwargs)
    return wrapper
