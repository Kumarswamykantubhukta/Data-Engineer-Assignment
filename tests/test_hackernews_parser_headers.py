
from pipeline.hackernews_parser import split_hackernews_comment


def make_comment(description):
    return {
        "company": None,
        "job_id": 12345,
        "title": None,
        "location": None,
        "description": description,
        "url": "https://news.ycombinator.com/item?id=12345",
        "source": "hackernews",
    }


def test_extract_single_data_engineer():
    comment = make_comment(
        "Acme | Data Engineer | NYC, Hybrid | Full-Time\n"
        "Python, SQL and Spark required."
    )

    jobs = split_hackernews_comment(comment)

    assert len(jobs) == 1
    assert jobs[0]["company"] == "Acme"
    assert jobs[0]["job_title"] == "Data Engineer"
    assert jobs[0]["location"] == "NYC, Hybrid"


def test_extract_multiple_target_roles():
    comment = make_comment(
        "Acme | REMOTE US | Full time\n"
        "We are hiring:\n"
        "* Data Engineer\n"
        "* Analytics Engineer\n"
        "* Frontend Developer"
    )

    jobs = split_hackernews_comment(comment)

    assert len(jobs) == 2
    assert jobs[0]["job_title"] == "Data Engineer"
    assert jobs[1]["job_title"] == "Analytics Engineer"


def test_preserve_original_comment_information():
    comment = make_comment(
        "Acme | Data Engineer | Austin, TX | Full-Time\n"
        "Python and SQL required."
    )

    jobs = split_hackernews_comment(comment)

    assert jobs[0]["original_comment_id"] == 12345
    assert jobs[0]["url"] == comment["url"]
    assert jobs[0]["source"] == "hackernews"
    assert jobs[0]["job_id"] == "12345_1"


def test_ignore_non_target_roles():
    comment = make_comment(
        "Acme | Backend Developer | NYC | Full-Time\n"
        "Java and Spring Boot."
    )

    jobs = split_hackernews_comment(comment)

    assert len(jobs) == 1
    assert jobs[0]["job_title"] == "Backend Developer"
