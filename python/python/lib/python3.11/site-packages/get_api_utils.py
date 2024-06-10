import logging
import json
from botocore.exceptions import ClientError
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_api_key(secret_name) -> str:
    """
    Gets the Guardian API key from AWS Secrets Manager.

    Parameters
    ----------
    secret_name : str (required)
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
        # print("API Key successfully returned.")
        return api_key["api_key"]

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error(
                "Secret '%s' does not exist.",
                secret_name)
        else:
            logger.error(
                "An error occurred accessing secret %s: %s.",
                secret_name, e)
    except KeyError as e:
        logger.error(
            "Incorrect key stored in secrets manager. Secret: %s, should have key: %s.",
            secret_name, e)


def get_api_link(api_key: str, search_terms: dict) -> str:
    """
    This generates the API link for the Guardian API.

    Parameters
    ----------
    api_key : str (required)
        The Guardian API key.
        Function get_api_key will provide the correct key.
    search_terms : dict (required)
        The search terms to be used in the API link.
        Function read_s3_json will provide the correct search terms.

    Raises
    ------
    None

    Returns
    -------
    api_link : str
        The API link for the Guardian API.
    """

    return f"https://content.guardianapis.com/search?q={search_terms['search_term']}&{search_terms['date_from']}&api-key={api_key}"
