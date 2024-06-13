import logging
import boto3
from botocore.exceptions import ClientError
from read_transformed_s3_json import read_transformed_s3_json

logger = logging.getLogger("loading_lambda")
logger.setLevel(logging.INFO)


def loading_handler(event, context):
    """
    This function is used to load data from an S3 bucket to a Kinesis stream.
    This is invoked whenever there is a PutObject event
    in the transformed S3 bucket.

    Parameters
    ----------
    event : dict
        A valid S3 PutObject event.
    context : object
        A valid AWS lambda Python context object.

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
        kinesis_client = boto3.client("kinesis", region_name="eu-west-2")

        content = read_transformed_s3_json(event)

        logger.info("Content has been successfully read.")

        kinesis_client.put_record(
            StreamName="streaming_data_project_output",
            Data=content,
            PartitionKey="0"
        )

        logger.info("Content has been successfully written to Kinesis.")

    except ClientError as ce:
        logger.error("Error: %s", ce.response["Error"]["Message"])
        logger.error("Error: %s", ce.response["Error"]['Code'])
        raise ce
    except Exception as e:
        logger.error("Error whilst processing loading_handler: %s", e)
