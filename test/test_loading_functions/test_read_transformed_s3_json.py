import os
import logging
from moto import mock_aws
import boto3
import pytest
from transformation_lambda.read_s3_json import read_s3_json

logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


class TestReadTransformedS3Json:
    @mock_aws
    def test_read_s3_json(self):
        s3 = boto3.client("s3")
        s3.create_bucket(
            Bucket="test_bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3.put_object(
            Bucket="test_bucket",
            Key="test.json",
            Body=b'{"key": "value"}')

        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test_bucket"},
                        "object": {"key": "test.json"},
                    }
                }
            ]
        }

        result = read_s3_json(event)
        assert result == {"key": "value"}

    @mock_aws
    def test_read_s3_json_wrong_file_type(self, caplog):
        with caplog.at_level(logging.ERROR):

            s3 = boto3.client("s3")
            s3.create_bucket(
                Bucket="test_bucket",
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            s3.put_object(
                Bucket="test_bucket",
                Key="test.txt",
                Body=b'{"key": "value"}')

            event = {
                "Records": [
                    {
                        "s3": {
                            "bucket": {"name": "test_bucket"},
                            "object": {"key": "test.txt"},
                        }
                    }
                ]
            }

            read_s3_json(event)
            assert "File test.txt is not a valid text file" in caplog.text

    @mock_aws
    def test_read_s3_json_no_bucket(self, caplog):
        with caplog.at_level(logging.ERROR):
            event = {
                "Records": [
                    {
                        "s3": {
                            "bucket": {"name": "test_bucket"},
                            "object": {"key": "test.json"},
                        }
                    }
                ]
            }

            read_s3_json(event)
            assert "No such bucket - test_bucket" in caplog.text
