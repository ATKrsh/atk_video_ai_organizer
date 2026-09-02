"""
Initial schema migration script.
Creates all database tables defined in database.schema.Base and sets up FTS5.
"""

from database.database import engine, Base
from database.schema import CREATE_FTS5_SQL
from logs.logger import logger


def run_migrations():
    """Create all ORM tables and FTS5 search index."""
    logger.info("Executing database migrations (create_all)...")
    Base.metadata.create_all(bind=engine)

    # Initialize FTS5 table
    with engine.connect() as conn:
        try:
            conn.exec_driver_sql(CREATE_FTS5_SQL)
            conn.commit()
            logger.info("FTS5 virtual table created successfully.")
        except Exception as e:
            logger.warning(f"FTS5 initialization warning: {e}")

    logger.info("Database migrations completed successfully.")


if __name__ == "__main__":
    run_migrations()
