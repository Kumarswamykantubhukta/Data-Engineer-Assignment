
import logging

from pipeline.content_hash import generate_content_hash
from pipeline.deduplication import jobs_are_duplicates
from pipeline.repository import (
    get_all_jobs,
    insert_job,
    update_job,
    add_job_source,
    record_history,
)

logger = logging.getLogger(__name__)


def get_extracted_data(extracted):
    """Convert a Pydantic model or dictionary into a dictionary."""
    if hasattr(extracted, "model_dump"):
        return extracted.model_dump()

    return dict(extracted)


def process_job(job, existing_jobs, extract_fn, validate_fn):
    """
    Process one job.

    extract_fn(job) -> Pydantic model or dictionary
    validate_fn(job, extracted_dict) -> validation result dictionary
    """
    content_hash = generate_content_hash(job)

    # Look for an existing canonical job.
    existing = next(
        (
            stored_job
            for stored_job in existing_jobs
            if jobs_are_duplicates(job, stored_job)
        ),
        None,
    )

    source = job.get("source", "unknown")
    source_job_id = str(job.get("job_id") or job.get("id") or job.get("url") or "")
    source_url = job.get("url") or ""

    if existing:
        job_id = existing["id"]

        # Record this source even when the content has not changed.
        add_job_source(
            job_id=job_id,
            source=source,
            source_job_id=source_job_id,
            source_url=source_url,
            raw_record=job,
        )

        # Unchanged job: no LLM call.
        if existing.get("content_hash") == content_hash:
            logger.info("Unchanged job skipped: %s", job.get("title"))
            return "unchanged"

        # Changed job: extract and validate again.
        extracted = get_extracted_data(extract_fn(job))
        validation = validate_fn(job, extracted)

        old_data = {
            key: existing.get(key)
            for key in (
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
            )
        }

        updates = {
            **extracted,
            "description": job.get("description"),
            "content_hash": content_hash,
            "status": "active" if validation["is_valid"] else "review",
        }

        update_job(job_id, updates)

        record_history(
            job_id=job_id,
            change_type="updated",
            old_data=old_data,
            new_data=updates,
        )

        existing.update(updates)

        logger.info("Updated existing job: %s", job_id)
        return "updated"

    # New job: extract and validate.
    extracted = get_extracted_data(extract_fn(job))
    validation = validate_fn(job, extracted)

    new_job = {
        **extracted,
        "company": extracted.get("company") or job.get("company"),
        "job_title": (
            extracted.get("job_title")
            or job.get("job_title")
            or job.get("title")
        ),
        "location": extracted.get("location") or job.get("location"),
        "description": job.get("description"),
        "content_hash": content_hash,
        "status": "active" if validation["is_valid"] else "review",
    }

    job_id = insert_job(new_job)

    add_job_source(
        job_id=job_id,
        source=source,
        source_job_id=source_job_id,
        source_url=source_url,
        raw_record=job,
    )

    new_job["id"] = job_id
    existing_jobs.append(new_job)

    logger.info("Inserted new job: %s", job_id)
    return "inserted"


def process_jobs(jobs, extract_fn, validate_fn):
    """Process a batch of jobs and return processing counts."""
    existing_jobs = get_all_jobs()

    counts = {
        "inserted": 0,
        "updated": 0,
        "unchanged": 0,
        "failed": 0,
    }

    for job in jobs:
        try:
            result = process_job(
                job=job,
                existing_jobs=existing_jobs,
                extract_fn=extract_fn,
                validate_fn=validate_fn,
            )
            counts[result] += 1

        except Exception:
            logger.exception(
                "Failed to process job: %s",
                job.get("title") or job.get("job_title"),
            )
            counts["failed"] += 1

    logger.info("Incremental processing summary: %s", counts)
    return counts
