"""
AWS Lambda function for scraping Udemy course metadata and persisting it to S3.

This module implements a functional-style pipeline:

1. Fetch HTML content from a course URL.
2. Parse selected fields using BeautifulSoup and regex-based selectors.
3. Build a normalized payload.
4. Upload the payload as JSON to S3.
"""

import json
import time
import re
import logging
from typing import Callable, TypedDict

import requests
import boto3
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

HEADERS = { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36", "Accept-Language": "en-US, en;q=0.5" }
SCRAPE_SPEC = {
    "title": ("h1", "class", r".*course.*title.*"),
    "headline": ("div", "class", r".*course.*headline.*"),
    "instructors": ("span", "class", r".*instructor.*"),
    "topics": ("div", "class", r".*breadcrumb.*"),
    "rating": ("span", "class", r".*ud-heading-sm.*"),
}


class CoursePayload(TypedDict):
    certificate_id: str
    url: str
    slug: str
    title: str | None
    headline: str | None
    instructors: str | None
    topics: str | None
    rating: str | None
    created: str


class LambdaEvent(TypedDict):
    """
    Schema for incoming Lambda events.

    Attributes:
        url: Public Udemy course URL to scrape.
        certificate_id: External certificate identifier associated with the course.
        bucket_name: Target S3 bucket for storing results.
        upstream_prefix: S3 key prefix (folder path).
    """
    url: str
    certificate_id: str
    bucket_name: str
    upstream_prefix: str


def get_slug(url: str) -> str:
    """
    Extract the course slug from a Udemy URL.

    Args:
        url: Full course URL.

    Returns:
        Last path segment of the URL, stripped of trailing slashes.
    """
    return url.rstrip("/").split("/")[-1]


def today() -> str:
    """
    Return the current date in ISO format (YYYY-MM-DD).

    Returns:
        Current UTC date as a string.
    """
    return time.strftime("%Y-%m-%d")


def extract_text(
    soup: BeautifulSoup,
    element: str,
    attribute: str,
    pattern: str,
) -> str | None:
    """
    Extract and normalize text from the first matching HTML element.

    Matching is performed using a regex applied to the given attribute.

    Args:
        soup: Parsed BeautifulSoup document.
        element: HTML tag name to search for.
        attribute: Attribute name to match against (e.g. "class").
        pattern: Regex pattern applied to the attribute value.

    Returns:
        Stripped text content if found, otherwise None.
    """
    tag = soup.find(element, attrs={attribute: re.compile(pattern)})
    if tag:
        return tag.text.strip()
    return None


def scrape_fields(
    soup: BeautifulSoup,
    extractor: Callable[..., str | None],
) -> dict[str, str | None]:
    """
    Scrape all configured fields from the HTML document.

    Field definitions are driven by SCRAPE_SPEC.

    Args:
        soup: Parsed BeautifulSoup document.
        extractor: Callable responsible for extracting a single field.

    Returns:
        Mapping of field names to extracted values.
    """
    return {
        key: extractor(soup, *spec)
        for key, spec in SCRAPE_SPEC.items()
    }


def build_payload(url: str, certificate_id: str, soup: BeautifulSoup) -> CoursePayload:
    """
    Build the normalized course payload.

    Combines static metadata with scraped HTML fields.

    Args:
        certificate_id: External certificate identifier.
        url: Course URL.
        soup: Parsed BeautifulSoup document.

    Returns:
        Dictionary containing all extracted and derived fields.
    """
    scraped = scrape_fields(soup, extract_text)

    return CoursePayload(
        certificate_id=certificate_id,
        url=url,
        slug=get_slug(url),
        title=scraped["title"],
        headline=scraped["headline"],
        instructors=scraped["instructors"],
        topics=scraped["topics"],
        rating=scraped["rating"],
        created=today(),
    )


def make_s3_key(payload: CoursePayload, prefix: str) -> str:
    """
    Generate the S3 object key for the payload.

    Format:
        {prefix}/udemy_{slug}_{created}.json

    Args:
        payload: Course payload dictionary.
        prefix: S3 prefix (folder path).

    Returns:
        Fully qualified S3 object key.
    """
    return f'{prefix}udemy_{payload["slug"]}_{payload["created"]}.json'


# side effects
def fetch_html(url: str) -> BeautifulSoup:
    """
    Fetch and parse HTML content from the provided URL.

    Performs an HTTP GET request using predefined headers and timeout.

    Args:
        url: Target URL.

    Returns:
        BeautifulSoup representation of the response body.

    Raises:
        requests.RequestException: On HTTP or connection errors.
    """
    response = requests.get(url, headers=HEADERS)
    #response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def upload_to_s3(bucket: str, key: str, payload: CoursePayload) -> None:
    """
    Upload payload as JSON to S3.

    Args:
        bucket: Target S3 bucket.
        key: Object key within the bucket.
        payload: Serialized course payload.

    Raises:
        ClientError: If S3 upload fails.
    """
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload).encode(),
    )


def lambda_handler(event: LambdaEvent, context: object):
    """
    AWS Lambda entry point.

    Orchestrates the full scraping pipeline:
        - Fetch HTML
        - Parse fields
        - Build payload
        - Upload to S3

    Args:
        event: LambdaEvent containing input parameters.
        context: AWS Lambda runtime context.

    Raises:
        requests.RequestException: On HTTP failures.
        ClientError: On S3 upload failures.
    """
    request_id = getattr(context, "aws_request_id", "local")
    logger.info("#" * 80)
    logger.info("Start lambda: %s", request_id)

    url = event["url"]
    certificate_id = event["certificate_id"]
    bucket = event["bucket_name"]
    prefix = event["upstream_prefix"]

    try:
        soup = fetch_html(url)
        payload = build_payload(url, certificate_id, soup)
        key = make_s3_key(payload, prefix)
        upload_to_s3(bucket, key, payload)

        logger.info("Parsed payload: %s", payload)
        logger.info("Uploaded to s3://%s/%s", bucket, key)

    except (requests.RequestException, ClientError) as exc:
        logger.exception("Processing failed")
        raise exc

    finally:
        logger.info("Stop lambda")
        logger.info("#" * 80)
