"""
Database configuration and session management for the Student Management System.
Uses SQLite database with SQLAlchemy ORM.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Path to the SQLite database file (stored in the backend directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'students.db')}"

# SQLite requires 'check_same_thread': False when multiple threads access the same connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True if you want to see raw SQL queries in the console
)

# SessionLocal is the factory for creating database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency provider for FastAPI route endpoints.
    Yields a database session and ensures it is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
