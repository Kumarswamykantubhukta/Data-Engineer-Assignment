
from pipeline.hackernews_parser import (
    split_comment_into_sections,
    split_hackernews_comment,
)


def test_split_numbered_roles():
    description = """
Company: Fly.io

1. Networking Engineer
Build networking infrastructure.

2. Infrastructure Operations Engineer
Manage infrastructure operations.

3. Software Engineer
Build backend services.
"""

    sections = split_comment_into_sections(description)

    assert len(sections) == 3


def test_split_comment_preserves_source_url():
    comment = {
        "job_id": "12345",
        "company": None,
        "title": None,
        "location": None,
        "description": """
1. Networking Engineer
Build networking infrastructure.

2. Infrastructure Operations Engineer
Manage infrastructure operations.
""",
        "url": "https://news.ycombinator.com/item?id=12345",
        "source": "hackernews",
    }

    jobs = split_hackernews_comment(comment)

    assert len(jobs) == 2
    assert jobs[0]["job_title"] == "Networking Engineer"
    assert jobs[1]["job_title"] == "Infrastructure Operations Engineer"
    assert jobs[0]["url"] == comment["url"]
    assert jobs[1]["url"] == comment["url"]
    assert jobs[0]["original_comment_id"] == "12345"
    assert jobs[0]["job_id"] != jobs[1]["job_id"]


def test_single_role_comment_is_preserved():
    comment = {
        "job_id": "67890",
        "title": None,
        "description": "We are hiring a Data Engineer.",
        "url": "https://news.ycombinator.com/item?id=67890",
        "source": "hackernews",
    }

    jobs = split_hackernews_comment(comment)

    assert len(jobs) == 1
    assert jobs[0]["description"] == comment["description"]
    assert jobs[0]["original_comment_id"] == "67890"


def test_explicit_role_labels():
    description = """
Role: Data Engineer
Build pipelines.

Position: Platform Engineer
Manage cloud infrastructure.
"""

    sections = split_comment_into_sections(description)

    assert len(sections) == 2
