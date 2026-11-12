
import pytest

from pipeline.repository import (
    insert_job,
    add_job_source,
    get_all_jobs,
    update_job,
    record_history,
)


@pytest.fixture
def sample_job():
    return {
        "company": "Test Company",
        "job_title": "Data Engineer",
        "location": "New York, NY",
        "country": "United States",
        "work_arrangement": "Hybrid",
        "employment_type": "Full-time",
        "experience_required": "3+ years",
        "salary": None,
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Spark"],
        "evidence": {
            "job_title": "Data Engineer",
            "required_skills": "Python and SQL required",
        },
        "description": "Test job description",
        "content_hash": "test_hash_123",
    }


def test_insert_and_retrieve_job(sample_job):
    job_id = insert_job(sample_job)

    try:
        jobs = get_all_jobs()
        inserted = next(job for job in jobs if job["id"] == job_id)

        assert inserted["company"] == "Test Company"
        assert inserted["job_title"] == "Data Engineer"
        assert inserted["required_skills"] == ["Python", "SQL"]

    finally:
        from pipeline.database import get_connection

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))


def test_add_job_source(sample_job):
    job_id = insert_job(sample_job)

    try:
        source_id = add_job_source(
            job_id=job_id,
            source="greenhouse",
            source_job_id="test-source-123",
            source_url="https://example.com/jobs/123",
            raw_record={"title": "Data Engineer"},
        )

        assert source_id is not None

    finally:
        from pipeline.database import get_connection

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))


def test_update_job(sample_job):
    job_id = insert_job(sample_job)

    try:
        update_job(job_id, {"location": "Boston, MA"})

        jobs = get_all_jobs()
        updated = next(job for job in jobs if job["id"] == job_id)

        assert updated["location"] == "Boston, MA"

    finally:
        from pipeline.database import get_connection

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))


def test_record_history(sample_job):
    job_id = insert_job(sample_job)

    try:
        history_id = record_history(
            job_id=job_id,
            change_type="updated",
            old_data={"location": "New York, NY"},
            new_data={"location": "Boston, MA"},
        )

        assert history_id is not None

    finally:
        from pipeline.database import get_connection

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))


def test_update_rejects_invalid_fields(sample_job):
    job_id = insert_job(sample_job)

    try:
        with pytest.raises(ValueError):
            update_job(job_id, {"id": 100})

    finally:
        from pipeline.database import get_connection

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
