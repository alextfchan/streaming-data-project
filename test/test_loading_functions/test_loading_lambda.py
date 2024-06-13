import os
import logging
import pytest
from moto import mock_aws
from botocore.exceptions import ClientError
import boto3
from loading_lambda.loading_handler import loading_handler


logger = logging.getLogger("TestLoadingLogger")
logger.setLevel(logging.INFO)


test_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "streaming-data-transformed-data-bucket"},
                "object": {"key": "2024-6-10-103825-transformed-content.json"},
            }
        }
    ]
}

test_content = '{"search_term": "machine learning", "date_from": "date_from=2023-01-01", "reference": "guardian_content"}' # noqa E501


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


class TestLoadingHandler:
    @pytest.fixture
    def s3_fixture(self):
        with mock_aws():
            s3 = boto3.client("s3", region_name="eu-west-2")
            s3_transformed = "streaming-data-transformed-data-bucket"

            s3.create_bucket(
                Bucket=s3_transformed,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"}
            )
            yield s3, s3_transformed

    @pytest.fixture
    def kinesis_fixture(self):
        with mock_aws():
            kinesis_client = boto3.client("kinesis", region_name="eu-west-2")
            data_stream_name = "streaming_data_project_output"
            kinesis_client.create_stream(
                StreamName=data_stream_name, ShardCount=1)
            yield kinesis_client, data_stream_name

    @mock_aws
    def test_loading_lambda_works_correctly(self,
                                            s3_fixture,
                                            kinesis_fixture,
                                            caplog):
        s3, s3_transformed = s3_fixture
        kinesis_client, data_stream_name = kinesis_fixture

        s3.put_object(Bucket=s3_transformed,
                      Key="2024-6-10-103825-transformed-content.json",
                      Body=test_content.encode("utf-8"))

        with caplog.at_level(logging.INFO):
            loading_handler(test_event, "content")
            assert ("Content has been successfully written to Kinesis."
                    in caplog.text)

            response = (kinesis_client.describe_stream(
                StreamName=data_stream_name))
            assert (response["StreamDescription"]["Shards"][0]
                    ["SequenceNumberRange"]["StartingSequenceNumber"] == "1")

    @mock_aws
    def test_loading_lambda_is_visible_in_kinesis(self,
                                                  s3_fixture,
                                                  kinesis_fixture):
        s3, s3_transformed = s3_fixture
        kinesis_client, data_stream_name = kinesis_fixture
        info = kinesis_client.describe_stream(
            StreamName=data_stream_name)

        s3.put_object(Bucket=s3_transformed,
                      Key="2024-6-10-103825-transformed-content.json",
                      Body=test_content.encode("utf-8"))
        loading_handler(test_event, "content")

        shard_iterator = kinesis_client.get_shard_iterator(
            StreamName=data_stream_name,
            ShardId=info["StreamDescription"]["Shards"][0]["ShardId"],
            ShardIteratorType="TRIM_HORIZON"
        )

        response = kinesis_client.get_records(
            ShardIterator=shard_iterator["ShardIterator"],
            Limit=1,
            StreamARN=info["StreamDescription"]["StreamARN"])
        result = response["Records"][0]["Data"].decode("utf-8")

        assert '{"search_term": "machine learning", "date_from": "date_from=2023-01-01", "reference": "guardian_content"}' == result # noqa E501

    @mock_aws
    def test_loading_lambda_no_bucket(self, caplog):
        with caplog.at_level(logging.ERROR):
            loading_handler(test_event, "content")
            assert ("No such bucket - streaming-data-transformed-data-bucket"
                    in caplog.text)

    @mock_aws
    def test_loading_lambda_no_kinesis_stream(self,
                                              s3_fixture,
                                              caplog):
        s3, s3_transformed = s3_fixture
        try:
            s3.put_object(Bucket=s3_transformed,
                          Key="2024-6-10-103825-transformed-content.json",
                          Body='{"test_content": "content"}'.encode("utf-8"))
            loading_handler(test_event, "content")
        except ClientError as ce:
            assert (ce.response["Error"]
                    ["Code"] == "ResourceNotFoundException")
            assert ce.response["Error"]["Message"] == "Stream streaming_data_project_output under account 123456789012 not found." # noqa E501
        with caplog.at_level(logging.ERROR):
            assert "Error: ResourceNotFoundException" in caplog.text
            assert "Error: Stream streaming_data_project_output under account 123456789012 not found." in caplog.text # noqa E501
