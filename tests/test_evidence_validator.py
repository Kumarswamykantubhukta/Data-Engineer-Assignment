
from pipeline.schemas import ExtractedJob
from pipeline.evidence_validator import validate_evidence


def test_valid_evidence():
    job = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York",
        "description": "We require Python and SQL experience."
    }

    extracted = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        location="New York",
        required_skills=["Python", "SQL"],
        evidence={
            "company": "Stripe",
            "job_title": "Data Engineer",
            "location": "New York",
            "required_skills": "Python and SQL"
        }
    )

    result = validate_evidence(extracted, job)

    assert result["is_valid"] is True
    assert result["missing_evidence"] == []
    assert result["unsupported_fields"] == []


def test_missing_evidence():
    job = {
        "company": "Stripe",
        "title": "Data Engineer",
        "description": "Python required."
    }

    extracted = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        required_skills=["Python"],
        evidence={
            "company": "Stripe"
        }
    )

    result = validate_evidence(extracted, job)

    assert result["is_valid"] is False
    assert "job_title" in result["missing_evidence"]
    assert "required_skills" in result["missing_evidence"]


def test_unsupported_evidence():
    job = {
        "company": "Stripe",
        "title": "Data Engineer",
        "description": "Python required."
    }

    extracted = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        required_skills=["Java"],
        evidence={
            "company": "Stripe",
            "job_title": "Data Engineer",
            "required_skills": "Java is mandatory"
        }
    )

    result = validate_evidence(extracted, job)

    assert result["is_valid"] is False
    assert "required_skills" in result["unsupported_fields"]
