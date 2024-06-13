# streaming-data-project

## Installation and Initial Setup

Fork and Clone Repository:

Clone the main branch of the repository:

```sh
git clone https://github.com/alextfchan/streaming-data-project.git
```
<br/>
Install Required Modules:

Run the following command in the terminal:

```sh
make requirements
```

To ensure everything is setup correctly, execute the following command in the terminal:

```sh
make run-checks
```
<br/>
Other Requirements:

Guardian API Key (required). 
This can be acquired by visiting:

```sh
https://open-platform.theguardian.com/access/
```


## Secrets
This pipeline relies on AWS Secrets Manager and GitHub secrets to secure credentials. No setup is required if working within this repository and project. For other databases or projects, set up secrets with appropriate credentials (variable naming, and secret naming is below).
<br/>
#### GitHub Secrets
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
<br/>
#### AWS Secrets
Secret name: guardian_api_key

You are now set up and ready to use this pipeline.

## Project Description:

### Overview
This streaming data project takes a user's search terms, and searches for relevant articles from the Guardian API. It will then publish the results to AWS Kinesis, a message broker, available for further analysis and consumption.

Using GitHub and AWS services, this ETL pipeline provides a scalable solution to ensure efficient extraction, transformation, and loading process to provide the requested content.

### Architecture
#### AWS Services

- **Amazon S3**: Serves as the central storage for both raw and processed data, providing a scalable and durable solution for storing large datasets.

- **AWS Lambda**: Handles the ETL processes, with functions triggered by event-based actions. Extraction is triggered by event source mapping, a Lambda resource, invoked whenever there is a new requested search. Transformation and loading are triggered by S3 put events in their respective buckets.

- **AWS Kinesis**: This is a message broker which allows efficient collection and processing of data streams. There are streams for both user input searches, as well as the published results.

- **CloudWatch**: Monitors the pipeline for errors and warnings, providing real-time insights into the health and performance of the ETL processes.

- **Secrets Manager**: Safeguards AWS and database credentials, ensuring secure access to sensitive information during the execution of ETL processes.

- **GitHub Actions**: Manages secrets related to the pipeline, providing a secure and automated way to protect sensitive information within the development and deployment workflows.


#### Workflow

![pipeline-diagram](./docs/aws-infra-diagram.svg)

1. Extraction: The extraction process is triggered through a lambda resource (event source mapping) which, on the event of a new requested search (put_record) in AWS Kinesis, will automatically trigger the ingestion lambda. This will be extracted to the ingested S3 data bucket.

2. Transformation: Upon the event of a new object in the ingested S3 data bucket, the transformation lamba will:
    a: Read the ingested data within the bucket.
    b: Retrieve the API key from Secrets Manager.
    c: Provide the correct API link.
    d: Retrieve the content.
    e: Write the content into the transformed S3 data bucket.

3. Loading: Triggered upon the event of a new object in transformed S3 data bucket, this lambda function will read the data, then put the contents into the AWS Kinesis data stream.

4. Monitoring: CloudWatch monitors the pipeline for errors and warnings.

5. Security: AWS Secrets Manager and GitHub Actions secrets are employed to safeguard credentials, ensuring secure access to AWS services and databases.

#### Benefits
- Scalability: Leveraging AWS services allows the pipeline to scale effortlessly with growing data volumes, ensuring consistent performance.

- Timely Updates: Event-driven scheduling ensures timely updates from the user's search terms, providing speedy data, ready for analytics.

- Security: Robust security measures, including Secrets Manager and GitHub Actions secrets, protect sensitive credentials and information throughout the pipeline.

- Reliability: CloudWatch monitoring contribute to a reliable and resilient pipeline, allowing for rapid issue resolution.

#### Future Enhancements
This streaming data pipeline has been designed with scalability in mind, and future enhancements may focus on providing additional ways to request content when providing search terms, such as integration with Slack, or other applications. 

There is also potential to provide more specific data based on user requirements, for example, being able to search different news content from other websites.

Monitoring and Alerting could also be added on, using services such as AWS SNS Email notifications to help alert errors if anything comes up as the data is processed by the pipeline.

## How to use this project:

### User Input Tool
Currently, the only way to upload data for processing, is using the user_input_tool. This can be invoked using this command within the terminal:

```sh
make create-new-search
```

Once invoked, the CLI will ask for 3 conditions:
1. Search Terms: The search terms of the content you would like to see.
2. Date From: The date from which you would like your results to be from. This requires a specific format of (YYYY-MM-DD), otherwise an error message will appear, and prompt you for a new input.
3. Reference: As of now, there is no functionality for other references. The default value is "guardian_content". Currently, "guardian_content" is required for the process to run sucessfully.

Once the three requested inputs are complete. You will receive a confirmation message that the script has been successful.
##

### Ingestion Lambda

Overview:
This AWS Lambda function processes incoming events, retrieves the latest records (search terms) from AWS Kinesis, and stores this formatted data into an S3 bucket.

Parameters:
- `event (dict)`: The event triggering the Lambda function.
- `context (LambdaContext)`: The runtime information of the Lambda function.

Returns:

- `None`

Raises:

- `ClientError`: If there is an error with the boto3 client connection.
- `Exception`: If there is an error during the processing of the event.

Configuration:

    S3 Bucket:
    Ensure that the S3 bucket specified in the bucket_name variable exists and has the necessary permissions for the Lambda function to read and write data.

Dependencies:

    AWS Lambda
    AWS Kinesis
    boto3: The AWS SDK for Python, used for interacting with S3.
    AWS S3
##

### Transformation Lambda

Overview:
This AWS Lambda function processes incoming events from the ingested S3 data bucket. Upon that event, it will:

    1: Decode and read the ingested data within the bucket.
    2: Retrieve the API key from Secrets Manager.
    3: Provide the correct API link.
    4: Retrieve the content.
    5: Write the content into the transformed S3 data bucket.

Parameters:
- `event (dict)`: The event triggering the Lambda function.
- `context (LambdaContext)`: The runtime information of the Lambda function.

Returns:

- `None`

Raises:

- `ClientError`: If there is an error with the boto3 client connection.
- `Exception`: If there is an error during the processing of the event.

Configuration:

    S3 Bucket:
    Ensure that the S3 bucket specified in the bucket_name variable exists and has the necessary permissions for the Lambda function to read and write data.

    Secrets Manager:
    Set the secret_name variable to the correct name ("guardian_api_key") of the AWS Secrets Manager secret containing the database credentials.

Dependencies:

    AWS Lambda
    AWS Secrets Manager
    AWS S3
    boto3: The AWS SDK for Python, used for interacting with S3.
    Guardian API Key

Functionality:

    Read S3 JSON:
    Function: read_s3_json(event)
    Retrieves the JSON file from the S3 bucket.

    Get API Key:
    Function: get_api_key("guardian_api_key")
    Retrieves the API key from AWS Secrets Manager

    Get API Link:
    Function: get_api_link(api_key, search_terms)
    Provides the correctly formatted API link using the API key, and search terms.

    Get Content:
    Function: get_content(api_link, api_key)
    Provides the result in dict format.

    Write Data to S3:
    Function: write_file_to_s3(content)
    Handles the creation of a new data file in the specified S3 bucket, organizing the structure by timestamp.
##

### Loading Lambda

Overview:
This AWS Lambda function processes incoming events from the transformed S3 data bucket. Upon the event of a new object in the data bucket, it will then read the data, then format the data to ensure compatability with AWS Kinesis data requirements. Then writes the data into the AWS Kinesis data stream.

Parameters:
- `event (dict)`: The event triggering the Lambda function.
- `context (LambdaContext)`: The runtime information of the Lambda function.

Returns:

- `None`

Raises:

- `ClientError`: If there is an error with the boto3 client connection.
- `Exception`: If there is an error during the processing of the event.

Configuration:

    S3 Bucket:
    Ensure that the S3 bucket specified in the bucket_name variable exists and has the necessary permissions for the Lambda function to read and write data.

    AWS Kinesis:
    Ensure that the Kinesis data stream has been correctly configured, and has the necessary permissions for the Lambda function to put records.

Dependencies:

    AWS Lambda
    AWS S3
    boto3: The AWS SDK for Python, used for interacting with S3.
    AWS Kinesis

Functionality:

    Read Transformed S3 JSONs:
    Function: read_transformed_s3_json(event)
    Extracts the JSON data from the specified S3 bucket and file.

##