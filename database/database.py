"""
SQLAlchemy engine and session management for SQLite.
Configures WAL journal mode, foreign keys, and connection pooling.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

# Database URI
DATABASE_URL = f"sqlite:///{settings.database_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30.0},
    echo=False,
)

# Enable WAL mode and foreign key constraints on connection
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency helper yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
