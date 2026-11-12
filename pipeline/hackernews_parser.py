
import re
from copy import deepcopy

from pipeline.filtering import is_target_role


SECTION_START = re.compile(
    r"^\s*(?:\d{1,2}[.)]\s+|[-*•]\s+|"
    r"(?:role|position|job title)\s*:\s*)",
    re.IGNORECASE,
)

METADATA_PATTERN = re.compile(
    r"\b(remote|onsite|on-site|hybrid|full[\s-]?time|"
    r"part[\s-]?time|contract|internship|salary|equity|"
    r"\$[\d,]+)\b",
    re.IGNORECASE,
)


def split_comment_into_sections(description: str) -> list[str]:
    """Split at role boundaries while retaining introductory context."""

    lines = description.splitlines()
    sections = []
    preamble = []
    current_section = None

    for line in lines:
        if SECTION_START.match(line):
            if current_section is not None:
                sections.append("\n".join(current_section).strip())
                current_section = [line]
            else:
                current_section = preamble + [line]
                preamble = []

        elif current_section is None:
            preamble.append(line)
        else:
            current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section).strip())
    elif preamble:
        sections.append("\n".join(preamble).strip())

    return [section for section in sections if section]


def extract_title(section: str) -> str | None:
    """Extract a title from a numbered, bulleted, or labelled line."""

    for line in section.splitlines():
        line = line.strip()

        if not SECTION_START.match(line):
            continue

        title = re.sub(
            r"^\s*(?:\d{1,2}[.)]\s+|[-*•]\s+)",
            "",
            line,
        )

        match = re.match(
            r"^(?:role|position|job title)\s*:\s*(.+)$",
            title,
            re.IGNORECASE,
        )

        title = match.group(1).strip() if match else title.strip()

        # Remove trailing job URL.
        title = re.sub(r"\s+-\s+https?://\S+.*$", "", title)

        return title or None

    return None



def parse_header(description: str) -> dict:
    """Parse company, role title and location from a pipe-separated header."""

    lines = [
        line.strip()
        for line in description.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "company": None,
            "header_title": None,
            "location": None,
        }

    parts = [part.strip() for part in lines[0].split("|")]

    company = parts[0] if len(parts) >= 2 else None
    header_title = None
    location = None

    if len(parts) >= 2:
        second = parts[1]

        if not METADATA_PATTERN.search(second):
            header_title = second

    # Search remaining fields for location.
    for part in parts[2:]:
        if not part:
            continue

        # Skip employment type, salary and other metadata.
        if re.fullmatch(
            r"(?:full[\s-]?time|part[\s-]?time|"
            r"contract|internship|temporary)",
            part,
            re.IGNORECASE,
        ):
            continue

        if re.search(
            r"\$[\d,]+|\b\d+k\b|\bequity\b",
            part,
            re.IGNORECASE,
        ):
            continue

        location = part
        break

    # Handle headers where location and arrangement are in field two.
    if not location and len(parts) >= 2:
        second = parts[1]

        if re.search(
            r"\b(remote|onsite|on-site|hybrid)\b",
            second,
            re.IGNORECASE,
        ):
            location = second

    return {
        "company": company,
        "header_title": header_title,
        "location": location,
    }


def split_hackernews_comment(comment: dict) -> list[dict]:
    """
    Convert a Hacker News comment into individual role records.

    Supports pipe-separated headers and numbered/bulleted roles.
    """

    description = comment.get("description") or ""
    header = parse_header(description)

    company = comment.get("company") or header["company"]
    location = comment.get("location") or header["location"]

    # Preserve original splitting behavior.
    sections = split_comment_into_sections(description)

    # A comment containing multiple explicit role sections.
    if len(sections) > 1:
        results = []

        for index, section in enumerate(sections, start=1):
            result = deepcopy(comment)

            result["company"] = company
            result["location"] = location
            result["description"] = section

            section_title = extract_title(section)

            result["job_title"] = section_title
            result["title"] = section_title
            result["original_comment_id"] = comment.get("job_id")
            result["role_index"] = index
            result["job_id"] = (
                f"{comment.get('job_id', 'unknown')}_{index}"
            )

            results.append(result)

        return results

    # A single target role from the header.
    header_title = header.get("header_title")

    if header_title and is_target_role(header_title):
        result = deepcopy(comment)

        result["company"] = company
        result["job_title"] = header_title
        result["title"] = header_title
        result["location"] = location
        result["original_comment_id"] = comment.get("job_id")
        result["role_index"] = 1
        result["job_id"] = (
            f"{comment.get('job_id', 'unknown')}_1"
        )

        return [result]

    # Preserve the original comment if no role split is possible.
    result = deepcopy(comment)
    result["company"] = company
    result["job_title"] = header_title
    result["location"] = location
    result["original_comment_id"] = comment.get("job_id")
    result["role_index"] = 1

    return [result]



def extract_bullet_roles(description: str) -> list[str]:
    """
    Extract target engineering roles from bullet or numbered lines.

    Generic bullets are ignored.
    """

    roles = []

    for line in description.splitlines():
        line = line.strip()

        if not SECTION_START.match(line):
            continue

        title = extract_title(line)

        if not title:
            continue

        # A colon may separate a role name from its description.
        # Preserve the full title unless it is clearly a description.
        title = re.split(r"\s+-\s+https?://", title)[0].strip()

        if is_target_role(title) and title not in roles:
            roles.append(title)

    return roles


def split_hackernews_comment(comment: dict) -> list[dict]:
    """
    Convert one Hacker News comment into target job records.

    Supports pipe-separated headers and multiple target roles.
    Retains original comment ID and URL.
    """

    description = comment.get("description") or ""
    header = parse_header(description)

    company = comment.get("company") or header["company"]
    location = comment.get("location") or header["location"]

    bullet_roles = extract_bullet_roles(description)

    # Multiple target roles in one comment.
    if bullet_roles:
        results = []

        for index, role in enumerate(bullet_roles, start=1):
            result = deepcopy(comment)

            result["company"] = company
            result["job_title"] = role
            result["title"] = role
            result["location"] = location
            result["original_comment_id"] = comment.get("job_id")
            result["role_index"] = index
            result["job_id"] = (
                f"{comment.get('job_id', 'unknown')}_{index}"
            )

            results.append(result)

        return results

    # Single target role from the header.
    header_title = header.get("header_title")

    if header_title and is_target_role(header_title):
        result = deepcopy(comment)

        result["company"] = company
        result["job_title"] = header_title
        result["title"] = header_title
        result["location"] = location
        result["original_comment_id"] = comment.get("job_id")
        result["role_index"] = 1
        result["job_id"] = (
            f"{comment.get('job_id', 'unknown')}_1"
        )

        return [result]

    # Preserve non-target comments for traceability.
    result = deepcopy(comment)
    result["company"] = company
    result["job_title"] = header_title
    result["location"] = location
    result["original_comment_id"] = comment.get("job_id")
    result["role_index"] = 1

    return [result]
