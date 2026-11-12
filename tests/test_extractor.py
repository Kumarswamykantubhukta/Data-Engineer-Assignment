
from types import SimpleNamespace
from unittest.mock import MagicMock

from pipeline.extractor import (
    clean_description,
    build_extraction_prompt,
    extract_job,
)
from pipeline.schemas import ExtractedJob


def test_clean_description():
    description = "&lt;h2&gt;Python Developer&lt;/h2&gt;<p>SQL required</p>"

    result = clean_description(description)

    assert "Python Developer" in result
    assert "SQL required" in result
    assert "<h2>" not in result


def test_build_extraction_prompt():
    job = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York",
        "source": "greenhouse",
        "url": "https://example.com/job/123",
        "description": "<p>Python and SQL required.</p>",
    }

    prompt = build_extraction_prompt(job)

    assert "Stripe" in prompt
    assert "Data Engineer" in prompt
    assert "Python and SQL required." in prompt
    assert "Do not guess" in prompt


def test_extract_job_with_mocked_gemini():
    expected_job = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        location="New York",
        required_skills=["Python", "SQL"],
        evidence={
            "company": "Company: Stripe",
            "job_title": "Data Engineer",
            "required_skills": "Python and SQL required",
        },
    )

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = SimpleNamespace(
        parsed=expected_job
    )

    input_job = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York",
        "source": "greenhouse",
        "url": "https://example.com/job/123",
        "description": "Python and SQL required.",
    }

    result = extract_job(input_job, client=mock_client)

    assert result.company == "Stripe"
    assert result.job_title == "Data Engineer"
    assert result.required_skills == ["Python", "SQL"]

    # Verify that the mocked Gemini client was called once.
    mock_client.models.generate_content.assert_called_once()
