# Create IAM role for Loading lambda
resource "aws_iam_role" "role_for_loading_lambda" {
  name = "role_for_loading_lambda"
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
resource "aws_iam_policy" "kinesis_output_policy_for_loading_lambda" {
    name = "loading_lambda_kinesis_output_policy"
    description = "Allows the loading lambda to interact with AWS Kinesis stream"
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
            "Resource": "${aws_kinesis_stream.output_stream.arn}"
        }
        ]
    })
}

# Attach the Kinesis policy to the role
resource "aws_iam_role_policy_attachment" "loading_lambda_kinesis_policy_attachment" {
    role = aws_iam_role.role_for_loading_lambda.name
    policy_arn = aws_iam_policy.kinesis_output_policy_for_loading_lambda.arn
}

# Create IAM policy for Cloudwatch logs
resource "aws_iam_policy" "cloudwatch_logs_policy_for_loading_lambda" {
  name        = "loading_lambda_cloudwatch_logs_policy"
  description = "Allows loading lambda to write logs to cloudwatch"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "logs:CreateLogGroup",
        Effect   = "Allow",
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
      },
      {
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.loading_lambda}:*"
      }
    ]
  })
}

# Attach the CW policy to the role
resource "aws_iam_role_policy_attachment" "loading_lambda_cw_policy_attachment" {
  policy_arn = aws_iam_policy.cloudwatch_logs_policy_for_loading_lambda.arn
  role       = aws_iam_role.role_for_loading_lambda.name
}


# Create IAM policy for S3 Bucket
resource "aws_iam_policy" "loading_lambda_s3_policy" {
  name        = "loading_lambda_s3_policy"
  description = "Allows reading from  transformed data bucket"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3-object-lambda:GetObject",
          "s3-object-lambda:PutObject",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          "${aws_s3_bucket.transformed_data_bucket.arn}/*",
          "${aws_s3_bucket.transformed_data_bucket.arn}",
        ]
      },
    ]
  })
}

# Attach the S3 policy to the role
resource "aws_iam_role_policy_attachment" "loading_lambda_s3_bucket_policy_attachment" {
  role = aws_iam_role.role_for_loading_lambda.name
  policy_arn = aws_iam_policy.loading_lambda_s3_policy.arn
}