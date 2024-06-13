import os
import logging
from datetime import datetime as dt
import pytest
import time_machine
import boto3
from moto import mock_aws
from ingestion_handler import ingestion_handler


logger = logging.getLogger("TestIngestionLogger")
logger.setLevel(logging.INFO)


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


class TestIngestionHandler:
    @pytest.fixture
    def kinesis_fixture(self):
        with mock_aws():
            kinesis_client = boto3.client("kinesis", region_name="eu-west-2")
            data_stream_name = "test_mock_stream_get_data"
            kinesis_client.create_stream(
                StreamName=data_stream_name, ShardCount=1)
            yield kinesis_client, data_stream_name

    @pytest.fixture
    def s3_fixture(self):
        with mock_aws():
            s3_client = boto3.client("s3", region_name="eu-west-2")
            bucket_name = "streaming-data-ingested-data-bucket"
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            yield s3_client, bucket_name

    def test_lambda_returns_correct_number_of_records(
            self,
            kinesis_fixture,
            s3_fixture,
            caplog):

        mock_event = {
            'Records': [
                {
                    'kinesis': {
                        'partitionKey': 'partitionKey-03',
                        'kinesisSchemaVersion': '1.0',
                        'data': 'SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=',
                        'sequenceNumber': '49545115243490985018280067714973144582180062593244200961',  # noqa E501
                        'approximateArrivalTimestamp': 1428537600
                    },
                    'eventSource': 'aws:kinesis',
                    'eventID': 'shardId-000000000000:49545115243490985018280067714973144582180062593244200961',  # noqa E501
                    'invokeIdentityArn': 'arn:aws:iam::EXAMPLE',
                    'eventVersion': '1.0',
                    'eventName': 'aws:kinesis:record',
                    'eventSourceARN': 'arn:aws:kinesis:EXAMPLE',
                    'awsRegion': 'eu-west-2'
                }
            ]
        }

        with caplog.at_level(logging.INFO):
            ingestion_handler(event=mock_event, context=None)
            assert "Successfully processed 1 records." in caplog.text

    @time_machine.travel(dt(2023, 1, 1, 17, 30, 19))
    def test_lambda_returns_correct_file_name(
            self, kinesis_fixture, s3_fixture, caplog):

        mock_event = {
            'Records': [
                {
                    'kinesis': {
                        'partitionKey': 'partitionKey-03',
                        'kinesisSchemaVersion': '1.0',
                        'data': 'SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=',
                        'sequenceNumber': '49545115243490985018280067714973144582180062593244200961',  # noqa E501
                        'approximateArrivalTimestamp': 1428537600
                    },
                    'eventSource': 'aws:kinesis',
                    'eventID': 'shardId-000000000000:49545115243490985018280067714973144582180062593244200961',  # noqa E501
                    'invokeIdentityArn': 'arn:aws:iam::EXAMPLE',
                    'eventVersion': '1.0',
                    'eventName': 'aws:kinesis:record',
                    'eventSourceARN': 'arn:aws:kinesis:EXAMPLE',
                    'awsRegion': 'eu-west-2'
                }
            ]
        }

        with caplog.at_level(logging.INFO):
            ingestion_handler(event=mock_event, context=None)
            assert "Success. File 2023-1-1-173019-search-terms.json saved, in bucket: streaming-data-ingested-data-bucket." in caplog.text  # noqa E501

    def test_lambda_returns_correct_test_data(
            self,
            kinesis_fixture,
            s3_fixture,
            caplog):

        mock_event = {
            'Records': [
                {
                    'kinesis': {
                        'partitionKey': 'partitionKey-03',
                        'kinesisSchemaVersion': '1.0',
                        'data': 'SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4=',
                        'sequenceNumber': '49545115243490985018280067714973144582180062593244200961',  # noqa E501
                        'approximateArrivalTimestamp': 1428537600
                    },
                    'eventSource': 'aws:kinesis',
                    'eventID': 'shardId-000000000000:49545115243490985018280067714973144582180062593244200961',  # noqa E501
                    'invokeIdentityArn': 'arn:aws:iam::EXAMPLE',
                    'eventVersion': '1.0',
                    'eventName': 'aws:kinesis:record',
                    'eventSourceARN': 'arn:aws:kinesis:EXAMPLE',
                    'awsRegion': 'eu-west-2'
                }
            ]
        }

        with caplog.at_level(logging.INFO):
            ingestion_handler(event=mock_event, context=None)
            assert "Record Data: Hello, this is a test 123." in caplog.text
