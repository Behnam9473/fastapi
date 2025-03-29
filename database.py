"""
Database Configuration Module

This module provides the database configuration and session management for the ZOHOOR-AR application.
It implements a SQLAlchemy-based database interface with session management and connection pooling.

Key Features:
- Database connection setup using SQLAlchemy
- Session management with context managers
- Protocol definition for database interfaces
- Error handling and logging
- Connection pooling configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, Protocol, runtime_checkable
from config import settings
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@runtime_checkable
class Database(Protocol):
    """
    Protocol defining the interface for database implementations.
    
    This protocol ensures that any database implementation provides:
    - Session management functionality
    - Table creation capabilities
    """
    def get_session(self) -> Generator[Session, None, None]: ...
    def create_tables(self) -> None: ...

class SQLAlchemyDatabase:
    """
    SQLAlchemy implementation of the Database protocol.
    
    This class provides concrete implementation for:
    - Database engine initialization
    - Session management
    - Table creation and management
    - Connection pooling
    """
    
    def __init__(self, url: str):
        """
        Initialize the SQLAlchemy database connection.
        
        Args:
            url (str): Database connection URL
            
        Note:
            Special handling for SQLite connections to allow multiple threads
        """
        self.engine = create_engine(
            url,
            connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database session handling.
        
        Yields:
            Session: SQLAlchemy database session
            
        Raises:
            Exception: Any database-related exceptions that occur during session use
            
        Note:
            - Automatically handles session cleanup
            - Implements rollback on error
            - Ensures session closure in all cases
        """
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def create_tables(self) -> None:
        """
        Creates all tables defined in SQLAlchemy models.
        
        This method should be called during application startup to ensure
        all required database tables exist.
        """
        self.Base.metadata.create_all(bind=self.engine)

# Create the database instance
db = SQLAlchemyDatabase(settings.DATABASE_URL)
Base = db.Base
engine = db.engine  # Expose engine for backward compatibility

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session injection.
    
    This function is used as a FastAPI dependency to provide database
    sessions to route handlers.
    
    Yields:
        Session: An active SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    with db.get_session() as session:
        yield session
