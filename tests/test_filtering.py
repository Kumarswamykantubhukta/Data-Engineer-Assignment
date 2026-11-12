
from pipeline.filtering import (
    is_target_role,
    is_us_eligible,
    filter_jobs,
)


def test_target_role():
    assert is_target_role("Senior Data Engineer")
    assert is_target_role("Machine Learning Engineer")
    assert is_target_role("Analytics Engineer")
    assert is_target_role("Platform Engineer")


def test_irrelevant_role():
    assert not is_target_role("Account Executive")
    assert not is_target_role("Software Engineer")


def test_us_city_and_state():
    job = {
        "location": "New York, NY",
        "description": ""
    }

    assert is_us_eligible(job)


def test_us_remote():
    job = {
        "location": "Remote",
        "description": "This position is remote within the United States."
    }

    assert is_us_eligible(job)


def test_generic_remote_is_not_enough():
    job = {
        "location": "Remote",
        "description": "This position can be performed remotely."
    }

    assert not is_us_eligible(job)


def test_non_us_location():
    job = {
        "location": "London, United Kingdom",
        "description": ""
    }

    assert not is_us_eligible(job)


def test_filter_jobs():
    jobs = [
        {
            "company": "Stripe",
            "title": "Data Engineer",
            "location": "New York, NY",
            "description": "Python and SQL required."
        },
        {
            "company": "Example",
            "title": "Account Executive",
            "location": "New York, NY",
            "description": ""
        },
        {
            "company": "Other",
            "title": "Platform Engineer",
            "location": "London, UK",
            "description": ""
        },
    ]

    result = filter_jobs(jobs)

    assert len(result) == 1
    assert result[0]["company"] == "Stripe"
