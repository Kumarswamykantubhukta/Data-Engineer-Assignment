
import csv
import json
import logging
from pathlib import Path

from pipeline.repository import get_all_jobs

logger = logging.getLogger(__name__)


def export_jobs_to_csv(output_path="data/processed/jobs.csv"):
    jobs = get_all_jobs()

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not jobs:
        logger.warning("No jobs available for CSV export.")
        return 0

    columns = [
        "id",
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
        "description",
        "status",
        "first_seen",
        "last_seen",
    ]

    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="ignore",
        )

        writer.writeheader()

        for job in jobs:
            row = {
                key: job.get(key)
                for key in columns
            }

            for key in ("required_skills", "preferred_skills"):
                row[key] = json.dumps(row[key] or [])

            writer.writerow(row)

    logger.info("Exported %s jobs to %s", len(jobs), output)
    return len(jobs)
