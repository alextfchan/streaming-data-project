import os
import logging
import json
import pytest
import boto3
from moto import mock_aws
from botocore.exceptions import ClientError
from input_tool.put_record_util import put_record

logger = logging.getLogger("TestUserInputTool")
logger.setLevel(logging.INFO)


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


class TestUserInputTool:
    @pytest.fixture
    def kinesis_fixture(self):
        with mock_aws():
            kinesis_client = boto3.client("kinesis", region_name="eu-west-2")
            data_stream_name = "streaming_data_project_input"
            kinesis_client.create_stream(
                StreamName=data_stream_name,
                ShardCount=1)
            yield kinesis_client, data_stream_name

    @pytest.fixture
    def bad_kinesis_fixture(self):
        with mock_aws():
            kinesis_client = boto3.client("kinesis", region_name="eu-west-2")
            data_stream_name = "bad_stream_name"
            kinesis_client.create_stream(
                StreamName=data_stream_name,
                ShardCount=1)
            yield kinesis_client, data_stream_name

    @pytest.fixture
    def data_input(self):
        data = {"search_term": "machine learning",
                "date_from": "2021-01-01",
                "reference": "guardian_content"}
        data = json.dumps(data).encode("utf-8")
        return data

    def test_put_record_works_correctly(self, kinesis_fixture, data_input):
        kinesis_client, data_stream_name = kinesis_fixture
        put_record(data_input)
        response = kinesis_client.describe_stream(StreamName=data_stream_name)

        assert response["StreamDescription"]["StreamName"] == data_stream_name
        assert response["StreamDescription"]["StreamStatus"] == "ACTIVE"
        assert (response["StreamDescription"]["Shards"]
                [0]["ShardId"] == "shardId-000000000000")
        assert (response["StreamDescription"]["Shards"]
                [0]["SequenceNumberRange"]["StartingSequenceNumber"] == "1")

    def test_put_record_fails_with_bad_data_type(self, kinesis_fixture):
        kinesis_client, data_stream_name = kinesis_fixture
        data = "bad data type - string"
        with pytest.raises(TypeError):
            put_record(data)

    def test(self, bad_kinesis_fixture, data_input):
        try:
            put_record(data_input)

        except ClientError as ce:
            assert ce.response["Error"]["Code"] == "ResourceNotFoundException"
            assert (ce.response["Error"]["Message"] == "Stream streaming_data_project_input under account 123456789012 not found.") # noqa E501
