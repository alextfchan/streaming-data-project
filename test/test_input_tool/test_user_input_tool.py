import os
from unittest import mock
import pytest
import boto3
from botocore.exceptions import ClientError
from moto import mock_aws
from input_tool.user_input_tool import user_input_tool


class TestUserInputTool:
    @pytest.fixture(scope="function")
    def aws_credentials(self):
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

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

    def test_input_tool_works_correctly(self, kinesis_fixture):
        with mock.patch('builtins.input',
                        side_effect=['machine learning',
                                     '2021-01-01',
                                     'guardian_content']):
            kinesis_client, data_stream_name = kinesis_fixture

            user_input_tool()

            response = kinesis_client.describe_stream(
                StreamName=data_stream_name)

            assert (response["StreamDescription"]
                    ["StreamName"] == data_stream_name)
            assert response["StreamDescription"]["StreamStatus"] == "ACTIVE"
            assert (response["StreamDescription"]["Shards"]
                    [0]["ShardId"] == "shardId-000000000000")
            assert (response["StreamDescription"]["Shards"][0]
                    ["SequenceNumberRange"]["StartingSequenceNumber"] == "1")

    def test_input_tool_with_no_stream(self, bad_kinesis_fixture):
        with mock.patch('builtins.input',
                        side_effect=['machine learning',
                                     '2021-01-01',
                                     'guardian_content']):
            try:
                user_input_tool()
            except ClientError as ce:
                assert (ce.response["Error"]
                        ["Code"] == "ResourceNotFoundException")
                assert ce.response["Error"]["Message"] == "Stream streaming_data_project_input under account 123456789012 not found." # noqa E501

    def test_input_tool_with_bad_search_term(self, kinesis_fixture):
        with mock.patch('builtins.input',
                        side_effect=['     machine learning      ',
                                     '2021-01-01',
                                     'guardian_content']):
            kinesis_client, data_stream_name = kinesis_fixture
            info = kinesis_client.describe_stream(
                StreamName=data_stream_name)

            user_input_tool()

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

            assert '{"search_term": "machine learning", "date_from": "2021-01-01", "reference": "guardian_content"}' == result # noqa E501

    def test_input_tool_with_bad_date_format(self, kinesis_fixture, capsys):
        with mock.patch('builtins.input',
                        side_effect=['machine learning',
                                     '19-1-1',
                                     "2021-01-01",
                                     "guardian_content"]):

            user_input_tool()
            captured = capsys.readouterr()
            error_message = captured.out.split('\n')[0]

            assert "Invalid date format. Please enter a date in the format YYYY-MM-DD." == error_message  # noqa E501

    def test_input_tool_with_default_values(self, kinesis_fixture):
        with mock.patch('builtins.input', side_effect=["", "", ""]):
            kinesis_client, data_stream_name = kinesis_fixture
            info = kinesis_client.describe_stream(
                StreamName=data_stream_name)

            user_input_tool()

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

            assert '{"search_term": "machine learning", "date_from": "2021-01-01", "reference": "guardian_content"}' == result # noqa E501
