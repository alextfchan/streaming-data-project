import logging
from botocore.exceptions import ClientError
from transformation_lambda.get_api_utils import get_api_key, get_api_link
from transformation_lambda.get_content import get_content
from transformation_lambda.read_s3_json import read_s3_json
from transformation_lambda.write_file import write_file_to_s3


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
    ClientError
        If there is an error with the boto3 client connection.
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
        logger.info("Before get_content")
        content = get_content(api_link, api_key)
        logger.info("Getting content: %s", content)
        logger.info("Content type: %s", type(content))

        write_file_to_s3(content)
        logger.info("Content written to S3 bucket.")

    except ClientError as ce:
        logger.error("Error: %s", ce.response["Error"]["Message"])
        raise ce
    except Exception as e:
        logger.error("Error whilst processing JSON file: %s", e)
