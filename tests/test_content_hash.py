
from pipeline.content_hash import generate_content_hash


def sample_job():
    return {
        "company": "Google",
        "title": "Data Engineer",
        "location": "Hyderabad, India",
        "description": "<p>Python and SQL required</p>",
        "url": "https://example.com/job/123",
        "source": "greenhouse",
    }


def test_same_content_generates_same_hash():
    job1 = sample_job()
    job2 = sample_job()

    assert generate_content_hash(job1) == generate_content_hash(job2)


def test_changed_description_generates_different_hash():
    job1 = sample_job()
    job2 = sample_job()

    job2["description"] = "Python, SQL and Spark required"

    assert generate_content_hash(job1) != generate_content_hash(job2)


def test_html_and_plain_text_generate_same_hash():
    job1 = sample_job()
    job2 = sample_job()

    job2["description"] = "Python and SQL required"

    assert generate_content_hash(job1) == generate_content_hash(job2)


def test_changed_source_url_does_not_change_hash():
    job1 = sample_job()
    job2 = sample_job()

    job2["url"] = "https://another-source.com/job/456"

    assert generate_content_hash(job1) == generate_content_hash(job2)
