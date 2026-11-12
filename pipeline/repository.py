
from psycopg.types.json import Jsonb

from pipeline.database import get_connection


def insert_job(job: dict) -> int:
    """Insert a canonical job and return its database ID."""

    query = """
        INSERT INTO jobs (
            company,
            job_title,
            location,
            country,
            work_arrangement,
            employment_type,
            experience_required,
            salary,
            required_skills,
            preferred_skills,
            evidence,
            description,
            content_hash
        )
        VALUES (
            %(company)s,
            %(job_title)s,
            %(location)s,
            %(country)s,
            %(work_arrangement)s,
            %(employment_type)s,
            %(experience_required)s,
            %(salary)s,
            %(required_skills)s,
            %(preferred_skills)s,
            %(evidence)s,
            %(description)s,
            %(content_hash)s
        )
        RETURNING id;
    """

    params = {
        "company": job["company"],
        "job_title": job["job_title"],
        "location": job.get("location"),
        "country": job.get("country"),
        "work_arrangement": job.get("work_arrangement"),
        "employment_type": job.get("employment_type"),
        "experience_required": job.get("experience_required"),
        "salary": job.get("salary"),
        "required_skills": Jsonb(job.get("required_skills", [])),
        "preferred_skills": Jsonb(job.get("preferred_skills", [])),
        "evidence": Jsonb(job.get("evidence", {})),
        "description": job.get("description"),
        "content_hash": job.get("content_hash"),
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()[0]


def add_job_source(
    job_id: int,
    source: str,
    source_job_id: str,
    source_url: str,
    raw_record: dict,
) -> int:
    """Insert or update a source record for a canonical job."""

    query = """
        INSERT INTO job_sources (
            job_id,
            source,
            source_job_id,
            source_url,
            raw_record
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (source, source_job_id)
        DO UPDATE SET
            job_id = EXCLUDED.job_id,
            source_url = EXCLUDED.source_url,
            raw_record = EXCLUDED.raw_record,
            fetched_at = NOW()
        RETURNING id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    job_id,
                    source,
                    source_job_id,
                    source_url,
                    Jsonb(raw_record),
                ),
            )
            return cursor.fetchone()[0]


def get_all_jobs() -> list[dict]:
    """Retrieve all canonical job records."""

    query = """
        SELECT
            id,
            company,
            job_title,
            location,
            country,
            work_arrangement,
            employment_type,
            experience_required,
            salary,
            required_skills,
            preferred_skills,
            evidence,
            description,
            content_hash,
            status
        FROM jobs
        ORDER BY id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column.name for column in cursor.description]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def update_job(job_id: int, updates: dict) -> None:
    """Update selected canonical job fields."""

    allowed_fields = {
        "company",
        "job_title",
        "location",
        "country",
        "work_arrangement",
        "employment_type",
        "experience_required",
        "salary",
        "required_skills",
        "preferred_skills",
        "evidence",
        "description",
        "content_hash",
        "status",
    }

    if not updates:
        raise ValueError("No fields supplied for update.")

    invalid_fields = set(updates) - allowed_fields

    if invalid_fields:
        raise ValueError(f"Invalid fields: {invalid_fields}")

    assignments = []
    values = []

    for field, value in updates.items():
        assignments.append(f"{field} = %s")

        if field in {
            "required_skills",
            "preferred_skills",
            "evidence",
        }:
            value = Jsonb(value)

        values.append(value)

    assignments.append("updated_at = NOW()")
    assignments.append("last_seen = NOW()")

    query = f"""
        UPDATE jobs
        SET {", ".join(assignments)}
        WHERE id = %s;
    """

    values.append(job_id)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)

            if cursor.rowcount == 0:
                raise ValueError(f"Job {job_id} does not exist.")


def record_history(
    job_id: int,
    change_type: str,
    old_data: dict | None,
    new_data: dict | None,
) -> int:
    """Store a historical version of a job."""

    query = """
        INSERT INTO job_history (
            job_id,
            change_type,
            old_data,
            new_data
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    job_id,
                    change_type,
                    Jsonb(old_data) if old_data is not None else None,
                    Jsonb(new_data) if new_data is not None else None,
                ),
            )

            return cursor.fetchone()[0]
