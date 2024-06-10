import logging
import json
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)


def read_s3_json(event):
    """
    Reads a JSON file from an S3 bucket (Raw data from user input).
    This is invoked whenever there is a PutObject event.

    Parameters
    ----------
    event : dict
        A valid S3 PutObject event.
    context : object
        A valid AWS lambda Python context object.
        https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Raises
    ------
    ClientError
        If there is an issue with reading the object from the S3 bucket.

    Returns
    -------
    dict
        The JSON file from the S3 bucket in dictionary type.
    """

    try:
        s3_bucket_name, s3_object_name = get_object_path(event['Records'])
        logger.info("Bucket is %s", s3_bucket_name)
        logger.info("Object key is %s", s3_object_name)

        if s3_object_name[-4:] != 'json':
            raise InvalidFileTypeError
        logger.info("File is a valid json file")

        s3 = boto3.client('s3')
        data = s3.get_object(Bucket=s3_bucket_name, Key=s3_object_name)
        decoded_data = data['Body'].read().decode('utf-8')
        json_data = json.loads(decoded_data)
        logger.info("Data has been successfully read from S3 bucket.")
        return json_data

    except KeyError as k:
        logger.error("Error retrieving data, %s", k)
    except ClientError as c:
        if c.response['Error']['Code'] == 'NoSuchKey':
            logger.error("No object found - %s", s3_object_name)
        elif c.response['Error']['Code'] == 'NoSuchBucket':
            logger.error("No such bucket - %s", s3_bucket_name)
        else:
            raise
    except UnicodeError:
        logger.error("File %s is not a valid text file", s3_object_name)
    except InvalidFileTypeError:
        logger.error("File %s is not a valid text file", s3_object_name)
    except Exception as e:
        logger.error(e)
        raise RuntimeError from e


def get_object_path(records):
    """Extracts bucket and object references from Records field of event."""
    return records[0]['s3']['bucket']['name'], \
        records[0]['s3']['object']['key']


class InvalidFileTypeError(Exception):
    """Traps error where file type is not json."""
    pass
