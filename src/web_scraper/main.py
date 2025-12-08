import json
import time
import boto3
import logging

from scraper import Scraper

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# client AWS S3
s3 = boto3.client('s3')

def upload_data_to_s3(data, bucket, key):
    s3.put_object(
        Body=json.dumps(data).encode('utf-8'),
        Bucket=bucket,
        Key=key
    )

def lambda_handler(event, context):
    max_retries = 0

    url = event.get("url", "")
    bucket = event.get("bucket", "")
    prefix=event.get("prefix", "")

    udemy = Scraper(url)
    udemy.parse_webpage()
    logger.info(f"start parsing: {url}")
    data = {
        "url": url,
        "slug": udemy.get_slug(),
        "title": udemy.scrape_content("h1", {"class":"clp-lead__title"}),
        "headline": udemy.scrape_content("div", {"class": "clp-lead__headline"}),
        "instructors": udemy.scrape_content_list("a", {"class": "ud-instructor-links"}),
        "topics": udemy.scrape_content_list("a", {"class": "ud-heading-sm"}),
        "students_num": udemy.scrape_content("span", {"class": "ud-heading-sm"}),
        "rating": udemy.scrape_content("span", {"class": "ud-heading-xl"}),
        "language": udemy.scrape_content("div", {"data-purpose": "lead-course-locale"}),
        "created": str( time.strftime("%Y-%m-%d") ),
    }
    logger.info(f"Parsed data: {data}")

    filename = f'udemy_{data["slug"]}_{data["created"]}.json'
    key =  prefix + filename
    upload_data_to_s3(data, bucket, key)
    logger.info(f'File uploaded to S3: {bucket + "/" + key}')
