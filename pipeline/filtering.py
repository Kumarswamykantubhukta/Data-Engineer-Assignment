
import re
import html
from bs4 import BeautifulSoup


ROLE_PATTERNS = [
    r"\bdata engineer\b",
    r"\banalytics engineer\b",
    r"\bmachine learning engineer\b",
    r"\bml engineer\b",
    r"\bplatform engineer\b",
]

US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california",
    "colorado", "connecticut", "delaware", "florida", "georgia",
    "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas",
    "kentucky", "louisiana", "maine", "maryland", "massachusetts",
    "michigan", "minnesota", "mississippi", "missouri", "montana",
    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico",
    "new york", "north carolina", "north dakota", "ohio", "oklahoma",
    "oregon", "pennsylvania", "rhode island", "south carolina",
    "south dakota", "tennessee", "texas", "utah", "vermont",
    "virginia", "washington", "west virginia", "wisconsin", "wyoming",
    "district of columbia",
}

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}


def plain_text(value: str | None) -> str:
    """Decode HTML and return plain text."""
    if not value:
        return ""

    decoded = html.unescape(value)
    return BeautifulSoup(
        decoded, "html.parser"
    ).get_text(separator=" ", strip=True)


def is_target_role(title: str | None) -> bool:
    """Check whether the title belongs to a target engineering category."""
    if not title:
        return False

    return any(
        re.search(pattern, title, re.IGNORECASE)
        for pattern in ROLE_PATTERNS
    )


def is_us_eligible(job: dict) -> bool:
    """
    Accept explicitly US-based jobs and explicitly US-remote jobs.

    A generic 'Remote' label is not sufficient.
    """
    location = plain_text(job.get("location"))
    description = plain_text(job.get("description"))

    location_lower = location.casefold()
    description_lower = description.casefold()

    # Explicit US country indicators.
    if re.search(r"\b(united states|usa|u\.s\.a\.|u\.s\.)\b", location_lower):
        return True

    # Explicit US state names.
    if any(state in location_lower for state in US_STATES):
        return True

    # State abbreviations when used in a location, e.g. Austin, TX.
    if re.search(r",\s*(" + "|".join(US_STATE_CODES) + r")\b", location):
        return True

    # Explicitly US-restricted remote positions.
    us_remote_patterns = [
        r"\bremote\s+(within|in|from)\s+(the\s+)?u\.?s\.?a?\.?\b",
        r"\bremote\s+(within|in|from)\s+(the\s+)?united states\b",
        r"\b(us|u\.s\.|usa|united states)[- ]remote\b",
        r"\bremote\s*[-(]\s*(us|usa|united states)\b",
        r"\bmust be based in the united states\b",
        r"\bmust reside in the united states\b",
        r"\bonly candidates located in the us\b",
    ]

    combined = location_lower + " " + description_lower

    return any(
        re.search(pattern, combined)
        for pattern in us_remote_patterns
    )


def filter_jobs(jobs: list[dict]) -> list[dict]:
    """Return jobs matching the target roles and US eligibility."""
    filtered = []

    for job in jobs:
        title = job.get("title") or job.get("job_title")

        if not is_target_role(title):
            continue

        if not is_us_eligible(job):
            continue

        filtered.append(job)

    return filtered
