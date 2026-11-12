
import argparse
import logging
from collections import Counter

from pipeline.ingestion import ingest_all_sources
from pipeline.hackernews_parser import split_hackernews_comment
from pipeline.filtering import filter_jobs
from pipeline.deduplication import merge_duplicate_jobs
from pipeline.incremental import process_jobs
from pipeline.evidence_validator import validate_evidence
from pipeline.schemas import ExtractedJob
from pipeline.exporter import export_jobs_to_csv
from pipeline.init_db import initialize_database


logger = logging.getLogger(__name__)


def prepare_jobs():
    """Ingest, parse, filter and deduplicate all source records."""

    raw_jobs, source_results = ingest_all_sources()

    parsed_jobs = []

    for job in raw_jobs:
        if job.get("source") == "hackernews":
            parsed_jobs.extend(split_hackernews_comment(job))
        else:
            parsed_jobs.append(job)

    filtered_jobs = filter_jobs(parsed_jobs)
    unique_jobs = merge_duplicate_jobs(filtered_jobs)

    print("\n========== PIPELINE SUMMARY ==========")
    print("Raw records:", len(raw_jobs))
    print("Parsed records:", len(parsed_jobs))
    print("Eligible records:", len(filtered_jobs))
    print("Unique records:", len(unique_jobs))
    print("Source counts:", source_results)

    return unique_jobs


def mock_extract_job(job):
    """
    Offline extraction for integration testing.

    This is NOT an LLM extraction result.
    It only uses fields already available in the source record.
    """

    company = job.get("company")
    title = job.get("job_title") or job.get("title")
    location = job.get("location")

    evidence = {}

    if company:
        evidence["company"] = company

    if title:
        evidence["job_title"] = title

    if location:
        evidence["location"] = location

    return ExtractedJob(
        company=company,
        job_title=title,
        location=location,
        country=None,
        work_arrangement=None,
        employment_type=None,
        experience_required=None,
        salary=None,
        required_skills=[],
        preferred_skills=[],
        evidence=evidence,
    )


def mock_validate_job(job, extracted):
    """Validate the deterministic mock extraction."""

    if not isinstance(extracted, ExtractedJob):
        extracted = ExtractedJob.model_validate(extracted)

    return validate_evidence(extracted, job)


def run_dry_run():
    print("\nMODE: DRY RUN")
    print("Gemini: Disabled")
    print("Database writes: Disabled")

    jobs = prepare_jobs()

    for index, job in enumerate(jobs[:10], start=1):
        print(
            f"\n{index}. "
            f"{job.get('job_title') or job.get('title')}"
        )
        print("Company:", job.get("company"))
        print("Location:", job.get("location"))
        print("Sources:", job.get("sources"))

    print("\nDry run completed.")


def run_mock_pipeline():
    print("\nMODE: MOCK DATABASE PIPELINE")
    print("Gemini: Disabled")
    print("Using deterministic mock extraction.")

    # Create tables if they do not already exist.
    initialize_database()

    # Collect and prepare jobs.
    jobs = prepare_jobs()

    # Incremental processing and PostgreSQL persistence.
    counts = process_jobs(
        jobs=jobs,
        extract_fn=mock_extract_job,
        validate_fn=mock_validate_job,
    )

    print("\n========== PROCESSING RESULTS ==========")
    for status, count in counts.items():
        print(f"{status}: {count}")

    # Export stored records.
    exported = export_jobs_to_csv()

    print("\nCSV records exported:", exported)
    print("\nMock database pipeline completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["dry-run", "mock"],
        default="dry-run",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if args.mode == "dry-run":
        run_dry_run()
    else:
        run_mock_pipeline()
