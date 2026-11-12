
from pipeline.init_db import initialize_database


def test_initialize_database():
    # This is an integration test: it requires PostgreSQL running.
    initialize_database()

    from pipeline.database import get_connection

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN (
                    'jobs',
                    'job_sources',
                    'job_history'
                );
            """)

            tables = {row[0] for row in cursor.fetchall()}

    assert tables == {
        "jobs",
        "job_sources",
        "job_history"
    }
