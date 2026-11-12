
from pipeline.lever import normalize_job


def test_normalize_lever_job():

    raw_job = {
        "id": "abc123",
        "text": "Senior Data Engineer",
        "categories": {
            "location": "New York"
        },
        "descriptionPlain": "Python and Spark required",
        "hostedUrl": "https://example.com/job"
    }

    result = normalize_job(raw_job, "palantir")

    assert result["company"] == "Palantir"
    assert result["job_id"] == "abc123"
    assert result["title"] == "Senior Data Engineer"
    assert result["location"] == "New York"
    assert result["source"] == "lever"


def test_missing_lever_location():

    raw_job = {
        "id": "abc124",
        "text": "ML Engineer"
    }

    result = normalize_job(raw_job, "plaid")

    assert result["location"] is None
