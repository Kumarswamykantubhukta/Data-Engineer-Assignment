
import re
from difflib import SequenceMatcher
from copy import deepcopy


def normalize_text(value: str | None) -> str:
    """Normalize text for comparison."""
    if not value:
        return ""

    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def normalize_company(value: str | None) -> str:
    """Normalize company names."""
    company = normalize_text(value)

    # Remove common legal suffixes.
    company = re.sub(
        r"\b(inc|llc|ltd|limited|corporation|corp|technologies)\b",
        "",
        company,
    )

    return " ".join(company.split())


def similarity(first: str, second: str) -> float:
    """Calculate string similarity."""
    if not first or not second:
        return 0.0

    return SequenceMatcher(None, first, second).ratio()


def token_similarity(first: str, second: str) -> float:
    """Calculate Jaccard similarity between word sets."""
    first_tokens = set(normalize_text(first).split())
    second_tokens = set(normalize_text(second).split())

    if not first_tokens or not second_tokens:
        return 0.0

    return len(first_tokens & second_tokens) / len(
        first_tokens | second_tokens
    )


def get_job_title(job: dict) -> str:
    return job.get("job_title") or job.get("title") or ""


def get_job_url(job: dict) -> str:
    return job.get("url") or ""


def get_job_description(job: dict) -> str:
    return job.get("description") or ""


def jobs_are_duplicates(first: dict, second: dict) -> bool:
    """Conservatively determine whether two records are the same job."""

    first_company = normalize_company(first.get("company"))
    second_company = normalize_company(second.get("company"))

    if not first_company or first_company != second_company:
        return False

    first_location = normalize_text(first.get("location"))
    second_location = normalize_text(second.get("location"))

    if not first_location or first_location != second_location:
        return False

    first_url = get_job_url(first)
    second_url = get_job_url(second)

    first_title = normalize_text(get_job_title(first))
    second_title = normalize_text(get_job_title(second))

    if not first_title or not second_title:
        return False

    if (
        first_url
        and second_url
        and first_url == second_url
        and first_title == second_title
    ):
        return True

    first_title = normalize_text(get_job_title(first))
    second_title = normalize_text(get_job_title(second))

    if not first_title or not second_title:
        return False

    title_score = similarity(first_title, second_title)

    if title_score >= 0.95:
        return True

    if title_score >= 0.85:
        description_score = token_similarity(
            get_job_description(first),
            get_job_description(second),
        )

        return description_score >= 0.65

    return False


def merge_duplicate_jobs(jobs: list[dict]) -> list[dict]:
    """
    Merge duplicate job records.

    Retain all source URLs and source names.
    Keep the first record as the canonical record.
    """

    merged = []

    for job in jobs:
        duplicate = None

        for existing in merged:
            if jobs_are_duplicates(existing, job):
                duplicate = existing
                break

        if duplicate is None:
            new_job = deepcopy(job)

            new_job["source_urls"] = (
                [get_job_url(job)] if get_job_url(job) else []
            )

            new_job["sources"] = (
                [job["source"]] if job.get("source") else []
            )

            new_job["source_records"] = [deepcopy(job)]

            merged.append(new_job)

        else:
            url = get_job_url(job)

            if url and url not in duplicate["source_urls"]:
                duplicate["source_urls"].append(url)

            source = job.get("source")

            if source and source not in duplicate["sources"]:
                duplicate["sources"].append(source)

            duplicate["source_records"].append(deepcopy(job))

    return merged
