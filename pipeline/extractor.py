
import html
import logging

from bs4 import BeautifulSoup
from google import genai
from google.genai import types

from pipeline.config import GEMINI_API_KEY, GEMINI_MODEL
from pipeline.schemas import ExtractedJob

logger = logging.getLogger(__name__)


def clean_description(description: str | None) -> str:
    """Convert an HTML job description into readable plain text."""
    if not description:
        return ""

    decoded_html = html.unescape(description)
    soup = BeautifulSoup(decoded_html, "html.parser")

    return soup.get_text(separator=" ", strip=True)


def build_extraction_prompt(job: dict) -> str:
    """Build the prompt using the normalized job record."""

    description = clean_description(job.get("description"))

    return f"""
You are an expert job-market data extraction assistant.

Extract structured information from the job posting below.

Rules:
1. Extract only information explicitly supported by the posting.
2. Do not guess or invent missing information.
3. Use null when a field is unavailable.
4. Separate required skills from preferred skills.
5. For every non-null extracted field, provide an evidence snippet.
6. Evidence must be a short, exact quotation from the supplied job information.
7. If a field is unavailable, its evidence value must be null.
8. If multiple locations or roles are mentioned, do not arbitrarily
   choose one. Use the most relevant information for this posting.

SOURCE METADATA:
Company: {job.get("company")}
Title: {job.get("title")}
Location: {job.get("location")}
Source: {job.get("source")}
Job URL: {job.get("url")}

JOB DESCRIPTION:
{description}
"""


def extract_job(job: dict, client=None) -> ExtractedJob:
    """
    Extract structured job information.

    If no client is supplied, a Gemini client is created.
    This function makes a live API request only when called.
    """

    if client is None:
        client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = build_extraction_prompt(job)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedJob,
            temperature=0.1,
        ),
    )

    if response.parsed is None:
        raise ValueError("Gemini did not return a valid structured response.")

    if isinstance(response.parsed, ExtractedJob):
        extracted = response.parsed
    else:
        extracted = ExtractedJob.model_validate(response.parsed)

    logger.info(
        "Successfully extracted job: %s",
        extracted.job_title
    )

    return extracted
