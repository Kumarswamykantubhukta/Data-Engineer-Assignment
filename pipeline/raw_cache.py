
import hashlib
import json
import logging
import re

from datetime import datetime, timezone
from pathlib import Path


RAW_DIR = Path("data/raw")

logger = logging.getLogger(__name__)


def calculate_hash(content: bytes) -> str:
    """Generate SHA256 hash of raw content."""

    return hashlib.sha256(content).hexdigest()


def save_raw_response(
    source: str,
    identifier: str,
    content: bytes,
    extension: str
) -> dict:

    content_hash = calculate_hash(content)

    # Make the identifier filesystem-safe.
    safe_identifier = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        identifier
    )

    directory = RAW_DIR / source / safe_identifier

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = f"{content_hash}.{extension}"

    filepath = directory / filename

    # Content-addressed storage:
    # identical content is not written twice.
    if not filepath.exists():

        filepath.write_bytes(content)

        logger.info(
            "Saved raw response: %s",
            filepath
        )

    else:

        logger.info(
            "Unchanged content already cached: %s",
            identifier
        )

    metadata = {
        "source": source,
        "identifier": identifier,
        "content_hash": content_hash,
        "filepath": str(filepath),
        "fetched_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    # Append fetch metadata for every observation.
    manifest = RAW_DIR / "manifest.jsonl"

    with manifest.open(
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(metadata) + "\n"
        )

    return metadata
