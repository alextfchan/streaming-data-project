# Create IAM role for Ingestion lambda
resource "aws_iam_role" "role_for_ingestion_lambda" {
  name = "role_for_ingestion_lambda"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "sts:AssumeRole"
        ],
        "Principal" : {
          "Service" : [
            "lambda.amazonaws.com"
          ]
        }
      }
    ]
  })
}

# Create IAM policy for Kinesis
resource "aws_iam_policy" "kinesis_input_policy_for_ingestion_lambda" {
    name = "ingestion_lambda_kinesis_input_policy"
    description = "Allows the ingestion lambda to interact with AWS Kinesis stream"
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:DescribeStream",
                "kinesis:DescribeStreamSummary",
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:ListShards",
                "kinesis:ListStreams",
                "kinesis:SubscribeToShard",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "role_for_ingestion_lambda_kinesis_policy_attachment" {
    role = aws_iam_role.role_for_ingestion_lambda.name
    policy_arn = aws_iam_policy.kinesis_input_policy_for_ingestion_lambda.arn
}

# https://developer.hashicorp.com/terraform/tutorials/aws/aws-iam-policy
# Refactor aws_iam_policy for s3 bucket.

# Create IAM policy for s3 Bucket
resource "aws_iam_policy" "ingestion_lambda_input_to_bucket" {
    name = "ingestion_lambda_input_to_bucket"
    description = "Allows the ingestion lambda to put objects into an s3 bucket"
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "s3-object-lambda:*"
            ],
            "Resource": "*"
        }
    ]
})
}

# Attach the s3 policy to the role
resource "aws_iam_role_policy_attachment" "role_for_ingestion_lambda_s3_bucket_policy_attachment" {
    role = aws_iam_role.role_for_ingestion_lambda.name
    policy_arn = aws_iam_policy.ingestion_lambda_input_to_bucket.arn
}