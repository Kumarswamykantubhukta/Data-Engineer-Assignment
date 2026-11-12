
import logging
from pathlib import Path

from pipeline.database import get_connection

logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def initialize_database():
    """Create all project tables and indexes."""

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)

    logger.info("Database schema initialized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_database()
    print("Database tables created successfully.")
