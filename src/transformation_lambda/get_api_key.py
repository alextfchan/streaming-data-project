import logging
import json
from botocore.exceptions import ClientError
import boto3

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def get_api_key(secret_name):
    """
    Gets the Guardian API key from AWS Secrets Manager.

    Parameters
    ----------
    sectret_name : str (required)
        The name of the secret in AWS Secrets Manager.

    Raises
    ------
    ClientError
        If the secret does not exist or there is an error accessing the secret.

    Returns
    -------
    str
        The Guardian API key.
    """
    try:
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])

        api_key = {"api_key": secret["api_key"]}

        logger.info("API Key successfully returned.")
        return api_key["api_key"]

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Secret %s does not exist.", secret_name)
        else:
            logger.error("An error occurred accessing secret %s: %s.", secret_name, e)
    except KeyError as e:
        logger.error(
            "Incorrect key stored in secrets manager. Secret: %s, should have key: %s.",
            secret_name, e)
