import os
import logging
import json
import pytest
from moto import mock_aws
import boto3
from transformation_handler import transformation_handler  # noqa 501
from get_api_utils import get_api_key, get_api_link
from get_content import get_content
from read_s3_json import read_s3_json
from write_file import write_file_to_s3

logger = logging.getLogger("TestTransformationLogger")
logger.setLevel(logging.INFO)


test_event = {
                "Records": [
                    {
                        "s3": {
                            "bucket": {
                                "name": "streaming-data-ingested-data-bucket"
                            },
                            "object": {
                                "key": "test_file.json"
                            }
                        }
                    }
                ]
            }


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


class TestTransformationHandler:
    @pytest.fixture
    def s3_fixture(self):
        with mock_aws():
            s3 = boto3.client("s3", region_name="eu-west-2")
            s3_ingested = "streaming-data-ingested-data-bucket"
            s3_transformed = "streaming-data-transformed-data-bucket"

            s3.create_bucket(
                Bucket=s3_ingested,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
            )
            s3.create_bucket(
                Bucket=s3_transformed,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
            )
            yield s3, s3_ingested, s3_transformed

    @pytest.fixture
    def secrets_fixture(self):
        with mock_aws():
            secret_name = "guardian_api_key"
            secrets_client = boto3.client("secretsmanager",
                                          region_name="eu-west-2")
            secrets_client.create_secret(
                Name=secret_name,
                SecretString=json.dumps({"api_key": "test"}))
            yield secrets_client

    @mock_aws
    def test_transformation_handler_works(self,
                                          s3_fixture,
                                          secrets_fixture,
                                          caplog):

        s3, s3_ingested, s3_transformed = s3_fixture
        search_terms = '{"search_term": "machine learning", "date_from": "2023-01-01", "reference": "guardian_content"}' # noqa E501

        s3.put_object(
            Bucket=s3_ingested,
            Key="test_file.json",
            Body=search_terms.encode("utf-8")) # noqa E501

        transformation_handler(test_event, "content")

        with caplog.at_level(logging.INFO):
            assert "Content written to S3 bucket." in caplog.text

    @mock_aws
    def test_transformation_handler_no_bucket(self, secrets_fixture, caplog):
        with caplog.at_level(logging.ERROR):
            transformation_handler(test_event, "content")
            assert ("No such bucket - streaming-data-ingested-data-bucket"
                    in caplog.text)

    def test_transformation_handler_no_secret(self, s3_fixture, caplog):
        with caplog.at_level(logging.ERROR):
            transformation_handler(test_event, "content")
            assert ("Secret 'guardian_api_key' does not exist." in caplog.text)
