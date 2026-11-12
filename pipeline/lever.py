
import time
import logging
from typing import Any

import requests

from pipeline.greenhouse import create_session
from pipeline.raw_cache import save_raw_response


BASE_URL = "https://api.lever.co/v0/postings"

COMPANIES = [
    "palantir",
    "metabase"
]
logger = logging.getLogger(__name__)


def normalize_job(
    job: dict[str, Any],
    company: str
) -> dict[str, Any]:

    categories = job.get("categories") or {}

    return {
        "company": company.title(),

        "job_id": str(job["id"]),

        "title": job.get("text"),

        "location": categories.get("location"),

        "description": (
            job.get("descriptionPlain")
            or job.get("description")
        ),

        "url": job.get("hostedUrl"),

        "updated_at": None,

        "source": "lever"
    }


def fetch_lever_jobs(
    company: str,
    session: requests.Session | None = None
) -> list[dict[str, Any]]:

    if not company.strip():
        raise ValueError("Company token cannot be empty")

    url = f"{BASE_URL}/{company}"

    params = {
        "mode": "json"
    }

    own_session = session is None

    if own_session:
        session = create_session()

    try:

        response = session.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        save_raw_response(
        source="lever",
        identifier=company,
        content=response.content,
        extension="json"
        )

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "application/json" not in content_type:
            raise ValueError(
                f"Expected JSON, received: {content_type}"
            )

        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Invalid Lever response structure")

        normalized_jobs = [
            normalize_job(job, company)
            for job in data
        ]

        logger.info(
            "%s: Retrieved %d jobs",
            company,
            len(normalized_jobs)
        )

        return normalized_jobs

    except requests.RequestException:

        logger.exception(
            "Lever API request failed for %s",
            company
        )

        raise

    finally:

        if own_session:
            session.close()


def fetch_all_lever_jobs():

    all_jobs = []

    session = create_session()

    try:

        for index, company in enumerate(COMPANIES):

            try:

                jobs = fetch_lever_jobs(
                    company,
                    session
                )

                all_jobs.extend(jobs)

            except Exception:

                logger.exception(
                    "Skipping failed company: %s",
                    company
                )

            if index < len(COMPANIES) - 1:
                time.sleep(1)

    finally:

        session.close()

    logger.info(
        "Total Lever jobs retrieved: %d",
        len(all_jobs)
    )

    return all_jobs


if __name__ == "__main__":

    jobs = fetch_all_lever_jobs()

    print("\nTotal Lever jobs:", len(jobs))

    for job in jobs[:5]:

        print("\n-------------------------")

        print("Company:", job["company"])
        print("Job ID:", job["job_id"])
        print("Title:", job["title"])
        print("Location:", job["location"])
        print("URL:", job["url"])
