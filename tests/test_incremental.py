
from pipeline.incremental import process_job
from pipeline.content_hash import generate_content_hash


def sample_job():
    return {
        "company": "Google",
        "title": "Data Engineer",
        "location": "Hyderabad, India",
        "description": "Python and SQL required",
        "url": "https://example.com/job/123",
        "source": "greenhouse",
        "job_id": "123",
    }


def mock_extractor(job):
    return {
        "company": job["company"],
        "job_title": job["title"],
        "location": job["location"],
        "country": "India",
        "work_arrangement": "On-site",
        "employment_type": "Full-time",
        "experience_required": None,
        "salary": None,
        "required_skills": ["Python", "SQL"],
        "preferred_skills": [],
        "evidence": {
            "company": "Google",
            "job_title": "Data Engineer",
            "location": "Hyderabad, India",
            "required_skills": "Python and SQL required",
        },
    }


def mock_validator(job, extracted):
    return {"is_valid": True}


def test_new_job_is_inserted(monkeypatch):
    import pipeline.incremental as incremental

    inserted = []
    sources = []

    monkeypatch.setattr(incremental, "insert_job", lambda job: 101)
    monkeypatch.setattr(
        incremental,
        "add_job_source",
        lambda **kwargs: sources.append(kwargs),
    )

    result = process_job(
        sample_job(),
        [],
        mock_extractor,
        mock_validator,
    )

    assert result == "inserted"
    assert len(sources) == 1


def test_unchanged_job_skips_extraction(monkeypatch):
    import pipeline.incremental as incremental

    job = sample_job()
    existing = {
        **mock_extractor(job),
        "id": 101,
        "description": job["description"],
        "content_hash": generate_content_hash(job),
    }

    monkeypatch.setattr(
        incremental,
        "add_job_source",
        lambda **kwargs: None,
    )

    def extractor_must_not_run(job):
        raise AssertionError("Extractor should not run")

    result = process_job(
        job,
        [existing],
        extractor_must_not_run,
        mock_validator,
    )

    assert result == "unchanged"
