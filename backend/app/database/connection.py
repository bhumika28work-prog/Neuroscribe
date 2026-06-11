"""
=============================================================
  app/database/connection.py — PostgreSQL Database Connection
=============================================================

📌 WHAT IS THIS FILE?
  This file sets up the connection between FastAPI and
  PostgreSQL using SQLAlchemy — the most popular Python ORM
  (Object Relational Mapper).

📌 WHAT IS AN ORM?
  ORM = Object Relational Mapper
  
  Instead of writing raw SQL queries like:
    SELECT * FROM reports WHERE id = 1;
  
  You write Python code like:
    db.query(Report).filter(Report.id == 1).first()
  
  SQLAlchemy converts your Python code into SQL automatically.
  This means:
  ✅ No SQL injection vulnerabilities
  ✅ Easier to switch databases (e.g., PostgreSQL → MySQL)
  ✅ Python objects instead of raw SQL strings
  ✅ Built-in validation

📌 HOW SQLALCHEMY WORKS:
  Engine     → The "connection manager" to the database
  Session    → A single "conversation" with the database
               (like a transaction — begin, do stuff, commit or rollback)
  Base       → The base class all your database models inherit from
  SessionLocal → A factory that creates new Session instances

📌 WHAT IS A DATABASE SESSION?
  Think of a Session like a shopping cart at a store:
  1. You open a cart (begin session)
  2. You add/remove items (create/update/delete records)
  3. You checkout (commit) OR abandon your cart (rollback)
  4. You close the cart (close session)
  
  Every request gets its OWN session and it must be closed
  after the request is done. This is handled by our
  get_db() dependency function below.

📌 WHAT IS DEPENDENCY INJECTION in FastAPI?
  Instead of creating a DB session inside every route function,
  FastAPI lets you "inject" the session using Depends():
  
  @router.get("/reports")
  async def get_reports(db: Session = Depends(get_db)):
      reports = db.query(Report).all()
      return reports
  
  FastAPI automatically:
  1. Calls get_db() to create the session
  2. Passes it to your function as `db`
  3. Ensures it's closed after the request (via finally block)
  
  This is called the "Dependency Injection" pattern.
  It makes testing much easier too!

📌 COMMON BEGINNER MISTAKES:
  ❌ Not closing the database session (causes connection leaks!)
  ❌ Creating a new engine on every request (very slow!)
  ❌ Using the same session across multiple requests (thread-unsafe!)
  ✅ Create the engine ONCE at module load time
  ✅ Use get_db() with Depends() to inject sessions
  ✅ Always use try/finally to ensure session is closed
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

# SQLAlchemy core components
from sqlalchemy import create_engine, text

# sessionmaker creates a factory for database sessions
from sqlalchemy.orm import sessionmaker

# DeclarativeBase is the base class for all ORM models
from sqlalchemy.orm import DeclarativeBase

# Generator type hint for get_db()
from typing import Generator

# Our settings to get the DATABASE_URL
from app.core.config import settings

# ──────────────────────────────────────────────
# CREATE THE DATABASE ENGINE
# ──────────────────────────────────────────────

"""
📌 create_engine():
  This creates the "engine" — the core interface to the database.
  
  Arguments explained:
  
  settings.DATABASE_URL
    → The connection string: postgresql://user:pass@host:port/dbname
  
  echo=settings.DEBUG
    → If True, SQLAlchemy prints every SQL query it runs.
    → Useful for debugging. Set to False in production.
  
  pool_pre_ping=True
    → Before using a connection from the pool, test if it's still alive.
    → Prevents "stale connection" errors after database restarts.
  
  pool_size=5
    → Keep 5 connections open in the "connection pool".
    → Connection pooling reuses connections instead of creating
      new ones for every request (much faster!).
  
  max_overflow=10
    → Allow up to 10 EXTRA connections beyond pool_size
      when all pool connections are in use.
    → So max 15 connections total (5 pool + 10 overflow).
"""

try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,        # Print SQL queries in debug mode
        pool_pre_ping=True,         # Check connection health before use
        pool_size=5,                # Number of persistent connections
        max_overflow=10,            # Max extra connections when pool is full
    )
    print("✅ Database engine created successfully")
except Exception as e:
    # Don't crash the app if DB is not available at startup
    # We'll handle this gracefully
    print(f"⚠️  Database engine creation warning: {e}")
    print("   → The app will still start, but DB features won't work")
    print("   → Make sure PostgreSQL is running and DATABASE_URL is correct")
    engine = None

# ──────────────────────────────────────────────
# CREATE SESSION FACTORY
# ──────────────────────────────────────────────

"""
📌 sessionmaker():
  Creates a factory class that produces Session instances.
  
  autocommit=False
    → Don't automatically commit changes.
    → We control when to commit (safer for transactions).
    → If something fails, we can rollback.
  
  autoflush=False
    → Don't automatically flush (send pending changes to DB)
      before queries.
    → We control this explicitly.
  
  bind=engine
    → Which engine (database) these sessions connect to.
"""

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ──────────────────────────────────────────────
# DECLARE BASE FOR ORM MODELS
# ──────────────────────────────────────────────

"""
📌 Base class for all database models:
  All your ORM model classes will inherit from Base.
  
  Example (in app/models/report.py):
    class Report(Base):
        __tablename__ = "reports"
        id = Column(Integer, primary_key=True)
        title = Column(String)
  
  When you call Base.metadata.create_all(engine),
  SQLAlchemy creates the actual tables in PostgreSQL.
"""

class Base(DeclarativeBase):
    """Base class that all ORM models will inherit from."""
    pass

# ──────────────────────────────────────────────
# DATABASE DEPENDENCY (for Dependency Injection)
# ──────────────────────────────────────────────

def get_db() -> Generator:
    """
    FastAPI Dependency: Provides a database session per request.
    
    📌 HOW TO USE IN ROUTES:
    
    from app.database.connection import get_db
    from sqlalchemy.orm import Session
    from fastapi import Depends
    
    @router.get("/reports")
    async def get_reports(db: Session = Depends(get_db)):
        # 'db' is automatically provided by FastAPI
        # It's a fresh session just for this request
        results = db.query(Report).all()
        return results
    
    📌 THE yield KEYWORD:
    This is a Python generator. The code runs up to 'yield',
    then FastAPI calls your route function with the db session.
    After the route finishes, execution resumes after 'yield'
    (the finally block runs, closing the session).
    
    This ensures the session is ALWAYS closed, even if an
    exception occurs in your route.
    
    Yields:
        Session: SQLAlchemy database session
    """
    if engine is None:
        raise Exception("Database is not connected. Check your DATABASE_URL in .env")
    
    # Create a new session for this request
    db = SessionLocal()
    
    try:
        # 'yield' pauses this function and gives the session to the route
        yield db
        # After the route finishes successfully, commit any pending changes
        db.commit()
    except Exception:
        # If anything goes wrong, rollback all changes in this session
        db.rollback()
        raise  # Re-raise the exception so FastAPI can handle it
    finally:
        # ALWAYS close the session, whether success or failure
        # This returns the connection back to the pool
        db.close()


# ──────────────────────────────────────────────
# DATABASE HEALTH CHECK FUNCTION
# ──────────────────────────────────────────────

def check_database_connection() -> dict:
    """
    Tests if the database connection is working.
    
    Used by the health check endpoint to report DB status.
    
    Returns:
        dict: Connection status and any error message
    """
    if engine is None:
        return {
            "status": "disconnected",
            "message": "Database engine not initialized"
        }
    
    try:
        # Try to execute a simple query to test the connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "message": "PostgreSQL connection successful ✅"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
