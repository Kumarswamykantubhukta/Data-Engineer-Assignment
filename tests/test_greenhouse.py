
from pipeline.greenhouse import normalize_job


def test_normalize_job():

    raw_job = {
        "id": 12345,
        "title": "Data Engineer",
        "location": {
            "name": "New York, NY"
        },
        "content": "<p>Python and SQL</p>",
        "absolute_url": "https://example.com/job",
        "updated_at": "2026-11-12T10:00:00-05:00"
    }

    result = normalize_job(raw_job, "stripe")

    assert result["company"] == "Stripe"
    assert result["job_id"] == "12345"
    assert result["title"] == "Data Engineer"
    assert result["location"] == "New York, NY"
    assert result["source"] == "greenhouse"


def test_missing_location():

    raw_job = {
        "id": 12346,
        "title": "ML Engineer"
    }

    result = normalize_job(raw_job, "airbnb")

    assert result["location"] is None
