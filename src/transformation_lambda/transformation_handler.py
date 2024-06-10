import os
import logging
import json
import boto3
from botocore.exceptions import ClientError
from get_api_utils import get_api_key, get_api_link
from get_content import get_content, get_content_preview
from read_s3_json import read_s3_json, get_object_path
from write_file import write_file_to_s3


logging.basicConfig()
logger = logging.getLogger("transformation_lambda")
logger.setLevel(logging.INFO)


def transformation_handler(event, context):
    """
    Transforms the search terms from the S3 bucket with raw data,
    transforms them into news results.

    Parameters
    ----------
    event : dict
        The event triggering the Lambda function.
    context : LambdaContext
        The runtime information of the Lambda function.

    Returns
    -------
    None

    Raises
    ------
    Exception
        If there is an error during the processing of the event.
    """

    try:
        search_terms = read_s3_json(event)
        logger.info("Reading JSON file from S3 bucket: %s", search_terms)

        api_key = get_api_key("guardian_api_key")
        logger.info("Getting API key from AWS Secrets Manager: %s", api_key)

        api_link = get_api_link(api_key, search_terms)
        logger.info("Getting API link: %s", api_link)

        content = get_content(api_link, api_key)
        logger.info("Getting content: %s", content)

        write_file_to_s3(content)

    except Exception as e:
        logger.error("Error whilst processing JSON file: %s", e)
