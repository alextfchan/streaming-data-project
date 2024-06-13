import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("loading_lambda")
logger.setLevel(logging.INFO)


def read_transformed_s3_json(event):
    """
    Reads a JSON file from an S3 bucket (Transformed data from user input).
    This is invoked whenever there is a PutObject event.

    Parameters
    ----------
    event : dict
        A valid S3 PutObject event.
    context : object
        A valid AWS lambda Python context object.

    Raises
    ------
    ClientError
        If there is an issue with reading the object from the S3 bucket.
    InvalidFileTypeError
        If the file is not a JSON file.

    Returns
    -------
    bytes
        The contents of the JSON file in bytes format.
        Required for kinesis put_record.
    """
    try:
        s3_bucket_name, s3_object_name = get_object_path(event['Records'])

        if s3_object_name[-4:] != 'json':
            logger.error("File %s is not a valid JSON file", s3_object_name)
            raise InvalidFileTypeError

        s3 = boto3.client('s3')
        data = s3.get_object(Bucket=s3_bucket_name, Key=s3_object_name)
        contents = data['Body'].read()

        return contents

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
