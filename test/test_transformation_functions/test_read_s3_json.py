import logging
import pytest
import boto3
from moto import mock_aws
from transformation_lambda.read_s3_json import (
    read_s3_json,
    get_object_path,
)

logger = logging.getLogger("TestTransformationLogger")
logger.setLevel(logging.INFO)

test_event = {
    "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "eu-west-2",
            "eventTime": "2023-11-03T11:11:19.251Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {"principalId": "testId"},
            "requestParameters": {"sourceIPAddress": "test_ip"},
            "responseElements": {
                "x-amz-request-id": "test_id",
                "x-amz-id-2": "test_id",
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "bucket_upload_something",
                "bucket": {
                    "name": "test_bucket_name",
                    "ownerIdentity": {"principalId": "testId"},
                    "arn": "test_arn",
                },
                "object": {
                    "key": "test_file.json",
                    "size": 0,
                    "eTag": "test_eTag",
                    "sequencer": "test_sequencer",
                },
            },
        }
    ]
}


class TestReadS3Json:
    @pytest.fixture
    def test_get_object_path_function_output_correctly(self):
        bucket_name, file_name = get_object_path(test_event["Records"])
        assert bucket_name == "test_bucket_name"
        assert file_name == "test_file.json"

    @mock_aws
    def test_read_s3_json_get_correct_content_log_message(self, caplog):
        client = boto3.client("s3", region_name="eu-west-2")
        example_dict = '{"c1": 1, "c2": 2}'
        coded_dict = example_dict.encode("utf-8")
        client.create_bucket(
            Bucket="test_bucket_name",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

        client.put_object(
            Body=coded_dict, Bucket="test_bucket_name", Key="test_file.json"
        )
        read_s3_json(test_event)

        with caplog.at_level(logging.INFO):
            assert "Data has been successfully read from S3 bucket." in caplog.text # noqa 501

    @mock_aws
    def test_read_s3_json_get_correct_content(self):
        client = boto3.client("s3", region_name="eu-west-2")
        example_dict = '{"c1": 1, "c2": 2}'
        coded_dict = example_dict.encode("utf-8")
        client.create_bucket(
            Bucket="test_bucket_name",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

        client.put_object(
            Body=coded_dict, Bucket="test_bucket_name", Key="test_file.json"
        )
        result_content = read_s3_json(test_event)

        assert result_content == {"c1": 1, "c2": 2}

    @mock_aws
    def test_read_s3_json_no_bucket(self, caplog):
        with caplog.at_level(logging.ERROR):
            read_s3_json(test_event)
            assert "No such bucket - test_bucket_name" in caplog.text
