"""
AWS Lambda function to request the Udemy API for course data and persist it to S3
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, TypedDict, Callable

import requests
import boto3
from botocore.exceptions import ClientError


BASE_URL = "https://www.udemy.com/api-2.0"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 10

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

s3 = boto3.client("s3")


class LambdaEvent(TypedDict):
    """
    Schema for incoming Lambda events.

    Attributes:
        COURSE_SLUG: course identifier
        CERTIFICATE_ID: certificate identifier
        BUCKET_NAME: Target S3 bucket name for storing results.
        PREFIX_UPSTREAM_API: S3 key (folder path).
    """
    COURSE_SLUG: str
    CERTIFICATE_ID: str
    BUCKET_NAME: str
    PREFIX_UPSTREAM_API: str


def make_s3_key(prefix_upstream_api: str, course_id: str) -> str:
    """
    Generate the S3 object key for the payload.

    Format:
        {prefix_upstream_api}/api_{course_id}.json

    Args:
        prefix_upstream_api: S3 prefix (folder path).
        course_id: Course Identifier

    Returns:
        Fully qualified S3 object key.
    """
    return f'{prefix_upstream_api}/api_{course_id}.json'


# side effect
def fetch_api(url: str) -> dict[str, Any]:
    """
    Fetch data from the API.

    Args:
        url: URL of the resource

    Returns:
        data dict
    """
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def validate_response_data(
    data: dict[str, Any], schema: dict[str, Callable[..., Any]]
) -> None:
    """
    Validates data from the API response.

    Args:
        data: response dict
        schema: validation dict
    """
    for key, validator_func in schema.items():
        if key not in data:
            raise KeyError(f"{key} is required")

        if not validator_func(data[key]):
            raise ValueError(f"{data[key]} is not valid")


def get_response_schema() -> dict[str, Callable[..., Any]]:
    return {
        "title": lambda value: isinstance(value, str) and len(value) > 0,
        "published_title": lambda value: isinstance(value, str) and len(value) > 0,
        "url": lambda value: isinstance(value, str) and len(value) > 0,
    }

def upload_to_s3(bucket_name: str, key: str, payload: dict[str, Any]) -> None:
    """
    Upload payload as JSON to S3.

    Args:
        bucket_name: Target S3 bucket_name.
        key: Object key within the bucket_name.
        payload: Serialized course payload.

    Raises:
        ClientError: If S3 upload fails.
    """
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(payload).encode(),
    )


def lambda_handler(event: LambdaEvent, context: object) -> None:
    """
    AWS Lambda entry point.

    Orchestrates the full scraping pipeline:
        - Fetch API
        - Upload to S3

    Args:
        event: LambdaEvent containing input parameters.
        context: AWS Lambda runtime context.

    Raises:
        requests.RequestException: On HTTP failures.
        ClientError: On S3 upload failures.
    """
    logger.info("Start lambda")

    COURSE_SLUG = event["COURSE_SLUG"]
    CERTIFICATE_ID = event["CERTIFICATE_ID"]
    BUCKET_NAME = event["BUCKET_NAME"]
    PREFIX_UPSTREAM_API = event["PREFIX_UPSTREAM_API"]

    try:
        url = f"{BASE_URL}/courses/{COURSE_SLUG}/"
        data = fetch_api(url)
        response_schema = get_response_schema()
        validate_response_data(data, response_schema)
        data["certificate_id"] = CERTIFICATE_ID
        data["source_system"] = "lambda_api"
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        key = make_s3_key(PREFIX_UPSTREAM_API, COURSE_SLUG)
        upload_to_s3(BUCKET_NAME, key, data)

        logger.info("Fetch data: %s", data)
        logger.info("Uploaded to s3://%s/%s", BUCKET_NAME, key)

    except (requests.RequestException, ClientError, KeyError, ValueError) as error:
        logger.error("Processing failed: %s", error)
        raise error

    finally:
        logger.info("Stop lambda")
        logger.info("#" * 80)
