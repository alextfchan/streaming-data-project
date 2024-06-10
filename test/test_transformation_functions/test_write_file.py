import os
from datetime import datetime as dt
import logging
import pytest
import time_machine
import boto3
from moto import mock_aws
from transformation_lambda.write_file import write_file_to_s3

logger = logging.getLogger("MyLogger")
logger.setLevel(logging.INFO)


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

@mock_aws
class TestWriteFile:
    def test_write_file(self):
        search_terms = '{"search_term": "machine learning", "date_from": "date_from=2023-01-01", "reference": "Guardian_content"}' # noqa 501
        s3 = boto3.client("s3")
        s3.create_bucket(
            Bucket="streaming-data-transformed-data-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        write_file_to_s3(search_terms)
        response = s3.list_objects(Bucket="streaming-data-transformed-data-bucket") # noqa 501
        assert len(response["Contents"]) == 1

    @time_machine.travel(dt(2020, 1, 1, 17, 30, 19))
    def test_check_correct_file_name_to_bucket(self):
        search_terms = '{"search_term": "machine learning", "date_from": "date_from=2019-01-01", "reference": "Guardian_content"}' # noqa 501
        s3 = boto3.client("s3")
        s3.create_bucket(
            Bucket="streaming-data-transformed-data-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        write_file_to_s3(search_terms)
        response = s3.list_objects(Bucket="streaming-data-transformed-data-bucket") # noqa 501
        assert response["Contents"][0]["Key"] == "2020-1-1-173019-transformed-content.json" # noqa 501

    @time_machine.travel(dt(2020, 1, 1, 17, 30, 19))
    def test_check_successful_log_output(self, caplog):
        search_terms = '{"search_term": "machine learning", "date_from": "date_from=2019-01-01", "reference": "Guardian_content"}' # noqa 501
        s3 = boto3.client("s3")
        s3.create_bucket(
            Bucket="streaming-data-transformed-data-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        write_file_to_s3(search_terms)
        assert (
             "Success. File 2020-1-1-173019-transformed-content.json saved."
             in caplog.text
        )

    def test_raises_client_error_if_empty_json(self, caplog):
        with caplog.at_level(logging.ERROR):
            s3 = boto3.client("s3")
            s3.create_bucket(
                Bucket="streaming-data-transformed-data-bucket",
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            search_terms = None
            with pytest.raises(Exception) as message:
                write_file_to_s3(search_terms)

            assert "No search terms provided." in str(message.value)
            assert "No search terms provided." in caplog.text
