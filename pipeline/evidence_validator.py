
import html

from bs4 import BeautifulSoup
from pipeline.schemas import ExtractedJob


def validate_evidence(extracted: ExtractedJob, original_job: dict) -> dict:
    description = html.unescape(
        original_job.get("description") or ""
    )
    description = BeautifulSoup(
        description, "html.parser"
    ).get_text(separator=" ", strip=True)

    source_text = " ".join([
        str(original_job.get("company") or ""),
        str(original_job.get("title") or ""),
        str(original_job.get("location") or ""),
        description,
    ]).casefold()

    missing_evidence = []
    unsupported_fields = []

    values = extracted.model_dump(exclude={"evidence"})

    for field, value in values.items():
        if value is None or value == []:
            continue

        evidence = extracted.evidence.get(field)

        if not evidence:
            missing_evidence.append(field)
            continue

        evidence_lower = evidence.casefold()

        if evidence_lower not in source_text:
            unsupported_fields.append(field)
            continue

        if isinstance(value, list):
            supported = all(
                item.casefold() in evidence_lower
                for item in value
            )
        else:
            supported = str(value).casefold() in evidence_lower

        if not supported:
            unsupported_fields.append(field)

    return {
        "is_valid": not missing_evidence and not unsupported_fields,
        "missing_evidence": missing_evidence,
        "unsupported_fields": unsupported_fields,
    }
