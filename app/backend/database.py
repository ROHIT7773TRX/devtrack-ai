# ============================================================
# database.py
# Sets up the SQLAlchemy database engine and session factory.
#
# WHAT THIS FILE DOES:
#   - Reads DATABASE_URL from environment variables
#   - Creates the SQLAlchemy engine (the connection pool to PostgreSQL)
#   - Creates a SessionLocal factory (each request gets its own session)
#   - Provides a get_db() dependency that FastAPI injects into routes
#
# WHY SQLALCHEMY?
#   SQLAlchemy is an ORM (Object Relational Mapper). Instead of writing
#   raw SQL like SELECT * FROM applications, we write Python:
#   db.query(Application).all()
#   SQLAlchemy translates Python into SQL automatically.
#
# TEST vs PRODUCTION:
#   - Production: DATABASE_URL = postgresql://... (uses psycopg2 driver)
#   - Tests:      DATABASE_URL = sqlite:///./test.db (built into Python)
#   Both work with the same SQLAlchemy code — the driver is swapped transparently.
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In production (Docker/Kubernetes), env vars are injected directly
load_dotenv()

# DATABASE_URL format: postgresql://USER:PASSWORD@HOST:PORT/DBNAME
# Example (production): postgresql://devtrack_user:secret@db:5432/devtrack
# Example (tests):      sqlite:///./test_devtrack.db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://devtrack_user:devtrack_pass@localhost:5432/devtrack"
)

# Create the database engine
# The engine manages the connection pool to the database
# pool_pre_ping=True: tests connections before using them (handles dropped connections)
# For SQLite (tests), we need check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

# SessionLocal is a factory for database sessions
# autocommit=False: we control when to commit (explicit is better than implicit)
# autoflush=False:  we control when to flush changes to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our SQLAlchemy models will inherit from
# It keeps track of all models so we can create tables with Base.metadata.create_all()
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.

    HOW IT WORKS:
    - Creates a new database session at the start of each request
    - Yields it to the route handler (via FastAPI's dependency injection)
    - Closes the session after the response is sent (even if an error occurred)

    In tests, this is overridden using:
        app.dependency_overrides[get_db] = override_get_db

    WHY yield INSTEAD OF return?
    Using 'yield' makes this a context manager. The code after 'yield'
    runs as cleanup, guaranteed to run even if an exception occurs.
    This ensures database sessions are always closed — no connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
