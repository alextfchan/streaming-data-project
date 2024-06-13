import boto3
from botocore.exceptions import ClientError


def put_record(data):
    """
    Writes a single data record into the Amazon Kinesis data stream.

    Parameters
    ----------
    data : bytes
        The data record to be written into the stream.

    Raises
    ------
    TypeError
        If the data is not correctly formatted to bytes.
    ClientError
        If the request fails.

    Returns
    -------
    None
    """

    if not isinstance(data, bytes):
        raise TypeError("Data must be the correct type: bytes.")

    kinesis_client = boto3.client("kinesis", region_name="eu-west-2")

    try:
        kinesis_client.put_record(
            StreamName="streaming_data_project_input",
            Data=data,
            PartitionKey="0")

    except ClientError as ce:
        print("Error: %s", ce.response["Error"]["Message"])
        raise ce
    except Exception as e:
        print("Error: %s", e)
        raise e
