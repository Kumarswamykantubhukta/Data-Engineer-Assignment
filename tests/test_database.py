
from pipeline.database import get_connection


def test_database_connection():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            result = cursor.fetchone()

        assert result[0] == "job_market_intelligence"

    finally:
        connection.close()
