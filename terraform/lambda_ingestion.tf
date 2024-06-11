resource "aws_lambda_function" "ingestion_lambda" {
  function_name     = var.ingestion_lambda
  handler           = "ingestion_handler.ingestion_handler"
  runtime           = "python3.11"
  timeout           = 900
  role              = aws_iam_role.role_for_ingestion_lambda.arn
  s3_bucket         = aws_s3_bucket.lambda_code_bucket.id
  s3_key            = "ingestion_lambda/ingestion_handler.zip"
  layers            = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python311:3"]
  source_code_hash  = resource.aws_s3_object.ingestion_lambda_code_upload.source_hash
}

# Trigger the lambda function with the Kinesis stream
resource "aws_lambda_event_source_mapping" "ingestion_lambda_event_source_mapping" {
  event_source_arn  = aws_kinesis_stream.input_stream.arn
  enabled           = true
  function_name     = aws_lambda_function.ingestion_lambda.arn
  starting_position = "LATEST"
}