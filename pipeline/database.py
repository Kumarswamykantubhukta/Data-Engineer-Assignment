
import os
import logging

import psycopg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def get_connection():
    """Create and return a PostgreSQL database connection."""

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing:
        raise ValueError(
            f"Missing database environment variables: {missing}"
        )

    connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    logger.info("Connected to PostgreSQL successfully.")

    return connection
