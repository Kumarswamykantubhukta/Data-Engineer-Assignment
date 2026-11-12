
import hashlib
import json
import re
from html import unescape

from bs4 import BeautifulSoup


def normalize_description(description):
    """Convert HTML descriptions into consistent plain text."""
    if not description:
        return ""

    text = BeautifulSoup(description, "html.parser").get_text(" ")
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def generate_content_hash(job):
    """
    Generate a SHA-256 hash using the important job content.

    Source URL and source name are excluded because they
    don't necessarily represent changes to the actual job.
    """
    content = {
        "company": (job.get("company") or "").strip().lower(),
        "title": (
            job.get("job_title") or job.get("title") or ""
        ).strip().lower(),
        "location": (job.get("location") or "").strip().lower(),
        "description": normalize_description(
            job.get("description") or ""
        ),
    }

    serialized_content = json.dumps(
        content,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(
        serialized_content.encode("utf-8")
    ).hexdigest()
