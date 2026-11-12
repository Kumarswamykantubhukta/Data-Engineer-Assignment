
import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import hashlib

from pipeline.raw_cache import save_raw_response

import requests
from bs4 import BeautifulSoup

from pipeline.greenhouse import create_session


BASE_URL = "https://news.ycombinator.com"
USER_AGENT = "JobMarketIntelligence/1.0"

logger = logging.getLogger(__name__)


def get_page(session, url, robots):
    """Fetch one HTML page politely."""

    if urlparse(url).netloc != "news.ycombinator.com":
        raise ValueError("Unexpected domain")

    if not robots.can_fetch(USER_AGENT, url):
        raise PermissionError(
            f"robots.txt disallows: {url}"
        )

    response = session.get(url, timeout=30)
    response.raise_for_status()
    
    page_id = hashlib.sha256(
    url.encode()
    ).hexdigest()

    save_raw_response(
        source="hackernews",
        identifier=page_id,
        content=response.content,
        extension="html"
    )

    content_type = response.headers.get(
        "Content-Type", ""
    ).lower()

    if "text/html" not in content_type:
        raise ValueError("Expected HTML response")

    return BeautifulSoup(response.text, "html.parser")


def find_current_hiring_thread(session, robots):
    """Find this month's Who is Hiring thread."""

    url = f"{BASE_URL}/submitted?id=whoishiring"

    current_month = datetime.now(
        timezone.utc
    ).strftime("%B %Y")

    while url:

        soup = get_page(session, url, robots)

        for row in soup.select("tr.athing"):

            title_element = row.select_one(
                ".titleline a"
            )

            if not title_element:
                continue

            title = title_element.get_text(
                " ", strip=True
            )

            if (
                "Who is hiring?" in title
                and current_month in title
            ):
                return urljoin(
                    BASE_URL,
                    title_element["href"]
                )

        more = soup.select_one("a.morelink")

        if not more:
            break

        url = urljoin(BASE_URL, more["href"])
        time.sleep(1)

    raise ValueError(
        f"No hiring thread found for {current_month}"
    )


def parse_comments(soup):
    """Extract raw top-level hiring comments."""

    comments = []

    for row in soup.select("tr.athing.comtr"):

        # Ignore nested replies where possible.
        indent = row.select_one(".ind img")

        if indent and indent.get("width") != "0":
            continue

        comment_id = row.get("id")

        content = row.select_one(".commtext")

        if not comment_id or not content:
            continue

        comments.append({
            "company": None,
            "job_id": comment_id,
            "title": None,
            "location": None,
            "description": content.get_text(
                " ", strip=True
            ),
            "url": (
                f"{BASE_URL}/item?id={comment_id}"
            ),
            "updated_at": None,
            "source": "hackernews"
        })

    return comments


def scrape_hiring_thread(
    session,
    robots,
    thread_url
):
    """Scrape comments across all HTML pages."""

    all_comments = []
    seen_comments = set()
    visited_pages = set()

    url = thread_url

    while url and url not in visited_pages:

        visited_pages.add(url)

        soup = get_page(session, url, robots)

        comments = parse_comments(soup)

        for comment in comments:

            if comment["job_id"] in seen_comments:
                continue

            seen_comments.add(comment["job_id"])
            all_comments.append(comment)

        logger.info(
            "Scraped %d unique comments",
            len(all_comments)
        )

        more = soup.select_one("a.morelink")

        url = (
            urljoin(BASE_URL, more["href"])
            if more else None
        )

        if url:
            time.sleep(1)

    return all_comments


def fetch_hackernews_jobs():

    session = create_session()

    robots = RobotFileParser()
    robots.set_url(f"{BASE_URL}/robots.txt")

    try:
        robots.read()

        thread_url = find_current_hiring_thread(
            session, robots
        )

        logger.info(
            "Hiring thread: %s",
            thread_url
        )

        return scrape_hiring_thread(
            session,
            robots,
            thread_url
        )

    finally:
        session.close()


if __name__ == "__main__":

    jobs = fetch_hackernews_jobs()

    print("\nTotal comments:", len(jobs))

    for job in jobs[:3]:

        print("\n--------------------")
        print("Comment ID:", job["job_id"])
        print("URL:", job["url"])
        print(
            "Description:",
            job["description"][:300]
        )
