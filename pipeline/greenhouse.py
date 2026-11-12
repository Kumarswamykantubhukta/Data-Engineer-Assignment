from pipeline.raw_cache import save_raw_response
import time
import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ------------------------------------------------
# 1. Configuration
# ------------------------------------------------

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

COMPANIES = (
    "stripe",
    "airbnb",
    "databricks",
    "figma"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ------------------------------------------------
# 2. Create HTTP session with retry configuration
# ------------------------------------------------

def create_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",)
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "JobMarketIntelligence/1.0"
    })

    return session


# ------------------------------------------------
# 3. Normalize individual job records
# ------------------------------------------------

def normalize_job(
    job: dict[str, Any],
    company: str
) -> dict[str, Any]:

    location = job.get("location") or {}

    return {
        "company": company.title(),
        "job_id": str(job.get("id")),
        "title": job.get("title"),
        "location": location.get("name"),
        "description": job.get("content"),
        "url": job.get("absolute_url"),
        "updated_at": job.get("updated_at"),
        "source": "greenhouse"
    }


# ------------------------------------------------
# 4. Fetch jobs from one Greenhouse company
# ------------------------------------------------

def fetch_greenhouse_jobs(
    company: str,
    session: requests.Session | None = None
) -> list[dict[str, Any]]:

    if not company.strip():
        raise ValueError("Company token cannot be empty")

    url = f"{BASE_URL}/{company}/jobs"

    params = {
        "content": "true"
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
        source="greenhouse",
        identifier=company,
        content=response.content,
        extension="json"
        )

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "application/json" not in content_type:
            raise ValueError(
                f"Expected JSON response, received {content_type}"
            )

        data = response.json()

        raw_jobs = data.get("jobs", [])

        if not isinstance(raw_jobs, list):
            raise ValueError("Invalid jobs response structure")

        normalized_jobs = [
            normalize_job(job, company)
            for job in raw_jobs
        ]

        logger.info(
            "%s: Retrieved %d jobs",
            company,
            len(normalized_jobs)
        )

        return normalized_jobs

    except requests.RequestException:

        logger.exception(
            "API request failed for %s",
            company
        )

        raise

    finally:

        if own_session:
            session.close()


# ------------------------------------------------
# 5. Fetch jobs from all companies
# ------------------------------------------------

def fetch_all_greenhouse_jobs():

    all_jobs = []

    session = create_session()

    try:

        for index, company in enumerate(COMPANIES):

            try:

                jobs = fetch_greenhouse_jobs(
                    company,
                    session
                )

                all_jobs.extend(jobs)

            except Exception:

                logger.exception(
                    "Skipping failed company: %s",
                    company
                )

            # Maximum one API request per second
            # between requests to this domain.

            if index < len(COMPANIES) - 1:
                time.sleep(1)

    finally:

        session.close()

    logger.info(
        "Total Greenhouse jobs retrieved: %d",
        len(all_jobs)
    )

    return all_jobs


# ------------------------------------------------
# 6. Execute independently
# ------------------------------------------------

if __name__ == "__main__":

    jobs = fetch_all_greenhouse_jobs()

    print("\nTotal jobs:", len(jobs))

    for job in jobs[:5]:

        print("\n-------------------------")

        print("Company:", job["company"])
        print("Job ID:", job["job_id"])
        print("Title:", job["title"])
        print("Location:", job["location"])
        print("URL:", job["url"])
