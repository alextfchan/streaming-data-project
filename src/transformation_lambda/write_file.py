from datetime import datetime as dt
import logging
import json
import boto3
from botocore.exceptions import ClientError

logging.basicConfig()
logger = logging.getLogger("transformation_lambda")
logger.setLevel(logging.INFO)


def write_file_to_s3(content):
    """
    Gets the content from the API, and stores it in the s3 bucket.

    Parameters
    ----------
    content : dict (required)
        The content to be stored in the S3 bucket.

    Raises
    -------
    ClientError
        If there is an issue with putting the object into the S3 bucket.

    Returns
    -------
    None
    """

    client = boto3.client("s3")
    date = dt.now()
    year = date.year
    month = date.month
    day = date.day
    time = date.strftime("%H%M%S")

    file_name = f"{year}-{month}-{day}-{time}-transformed-content.json"

    try:
        if content is None:
            logging.error("No search terms provided.")
            raise Exception("No search terms provided.")

        else:
            response = client.put_object(
                # JSON content must be converted to bytes.
                Body=json.dumps(content,
                                indent=4,
                                ensure_ascii=False
                                ).encode("utf-8"),
                Bucket="streaming-data-transformed-data-bucket",
                Key=file_name
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("Success. File %s saved.", file_name)

    except ClientError as e:
        logger.error(e)
        raise e
