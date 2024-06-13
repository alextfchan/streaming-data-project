import os
import logging
import json
import pytest
import boto3
from moto import mock_aws
from transformation_lambda.get_api_utils import get_api_key

logger = logging.getLogger()


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@mock_aws
class TestGetApiKey:
    def test_ClientError_secret_that_does_not_exist(self, caplog):
        secret_name = "fake_secret_name"
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(
            Name=secret_name,
            SecretString=json.dumps({"incorrect_key": "test_value"}))

        with caplog.at_level(logging.ERROR):
            get_api_key("fake_secret")
            assert "Secret 'fake_secret' does not exist." in caplog.text

    def test_KeyError_incorrect_key_in_secret(self, caplog):
        secret_name = "fake_secret_name"
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(
            Name=secret_name,
            SecretString=json.dumps({"incorrect_key": "test_value"}))

        with caplog.at_level(logging.ERROR):
            get_api_key("fake_secret_name")

            assert "Incorrect key stored in secrets manager. Secret: fake_secret_name, should have key: 'api_key'." in caplog.text  # noqa: E501

    def test_connection_params_look_like_expected(self):
        secret_string = {"api_key": "mock real key"}
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(
            Name="Mock",
            SecretString=json.dumps(secret_string))

        assert get_api_key("Mock") == "mock real key"
