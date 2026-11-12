
from pipeline.schemas import ExtractedJob


def test_valid_job():
    job = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        location="New York",
        required_skills=["Python", "SQL"],
        salary=None
    )

    assert job.company == "Stripe"
    assert job.job_title == "Data Engineer"
    assert job.salary is None
    assert "Python" in job.required_skills


def test_missing_fields_default_to_none():
    job = ExtractedJob(company="Stripe")

    assert job.job_title is None
    assert job.location is None
    assert job.salary is None
    assert job.required_skills == []
    assert job.preferred_skills == []


def test_evidence_field():
    job = ExtractedJob(
        company="Stripe",
        job_title="Data Engineer",
        evidence={
            "company": "About Stripe",
            "job_title": "We are hiring a Data Engineer"
        }
    )

    assert job.evidence["company"] == "About Stripe"
