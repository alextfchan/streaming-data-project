import base64
import logging
from datetime import datetime as dt
import boto3
from botocore.exceptions import ClientError

logging.basicConfig()
logger = logging.getLogger("ingestion_lambda")
logger.setLevel(logging.INFO)


def ingestion_handler(event, context):
    """
    This function is used to ingest data from the Kinesis stream
    and save it to an S3 bucket.
    It does this using event source mapping.

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

    client = boto3.client("s3")
    bucket_name = "streaming-data-ingested-data-bucket"

    date = dt.now()
    year = date.year
    month = date.month
    day = date.day
    time = date.strftime("%H%M%S")
    file_name = f"{year}-{month}-{day}-{time}-search-terms.json"

    for record in event['Records']:
        try:
            logger.info("Processed Kinesis Event - EventID: {%s['eventID']}",
                        record)
            data = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            logger.info("Record Data: %s", data)
            response = client.put_object(
                Body=data,
                Bucket=bucket_name,
                Key=file_name
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("Success. File %s saved, in bucket: %s.",
                            file_name, bucket_name)

        except ClientError as ce:
            logger.error("Error: %s", ce.response["Error"]["Message"])
            raise ce
        except Exception as e:
            logger.error("An error occurred %s", e)
            raise e

    logger.info("Successfully processed %s records.", len(event['Records']))
