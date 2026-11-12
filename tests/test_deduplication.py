
from pipeline.deduplication import (
    normalize_text,
    jobs_are_duplicates,
    merge_duplicate_jobs,
)


def test_normalize_text():
    assert normalize_text("Data Engineer - Senior") == "data engineer senior"


def test_same_job_is_duplicate():
    first = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York, NY",
        "description": "Build data pipelines using Python and SQL.",
        "url": "https://stripe.com/jobs/123",
        "source": "greenhouse",
    }

    second = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York, NY",
        "description": "Build data pipelines using Python and SQL.",
        "url": "https://example.com/jobs/123",
        "source": "hackernews",
    }

    assert jobs_are_duplicates(first, second)


def test_different_companies_are_not_duplicates():
    first = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York, NY",
        "description": "Python and SQL.",
    }

    second = {
        "company": "Google",
        "title": "Data Engineer",
        "location": "New York, NY",
        "description": "Python and SQL.",
    }

    assert not jobs_are_duplicates(first, second)


def test_different_locations_are_not_duplicates():
    first = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "New York, NY",
        "description": "Python and SQL.",
    }

    second = {
        "company": "Stripe",
        "title": "Data Engineer",
        "location": "London, UK",
        "description": "Python and SQL.",
    }

    assert not jobs_are_duplicates(first, second)


def test_shared_hn_url_does_not_merge_different_roles():
    first = {
        "company": "Fly.io",
        "title": "Networking Engineer",
        "location": "Remote",
        "description": "Build networking infrastructure.",
        "url": "https://news.ycombinator.com/item?id=123",
        "source": "hackernews",
    }

    second = {
        "company": "Fly.io",
        "title": "Infrastructure Operations Engineer",
        "location": "Remote",
        "description": "Manage infrastructure operations.",
        "url": "https://news.ycombinator.com/item?id=123",
        "source": "hackernews",
    }

    assert not jobs_are_duplicates(first, second)


def test_merge_preserves_source_urls():
    jobs = [
        {
            "company": "Stripe",
            "title": "Data Engineer",
            "location": "New York, NY",
            "description": "Build data pipelines using Python and SQL.",
            "url": "https://stripe.com/jobs/123",
            "source": "greenhouse",
        },
        {
            "company": "Stripe",
            "title": "Data Engineer",
            "location": "New York, NY",
            "description": "Build data pipelines using Python and SQL.",
            "url": "https://example.com/jobs/123",
            "source": "hackernews",
        },
    ]

    result = merge_duplicate_jobs(jobs)

    assert len(result) == 1
    assert len(result[0]["source_urls"]) == 2
    assert set(result[0]["sources"]) == {"greenhouse", "hackernews"}
    assert len(result[0]["source_records"]) == 2


def test_unique_jobs_are_not_merged():
    jobs = [
        {
            "company": "Stripe",
            "title": "Data Engineer",
            "location": "New York, NY",
            "description": "Build data pipelines.",
            "url": "https://stripe.com/jobs/1",
            "source": "greenhouse",
        },
        {
            "company": "Google",
            "title": "Platform Engineer",
            "location": "California",
            "description": "Manage cloud infrastructure.",
            "url": "https://google.com/jobs/2",
            "source": "lever",
        },
    ]

    result = merge_duplicate_jobs(jobs)

    assert len(result) == 2
