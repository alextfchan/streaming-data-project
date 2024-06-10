resource "aws_lambda_function" "transformation_lambda" {
  function_name    = var.transformation_lambda
  handler          = "transformation_handler.transformation_handler"
  runtime          = "python3.11"
  timeout          = 900
  role             = aws_iam_role.role_for_transformation_lambda.arn
  s3_bucket        = aws_s3_bucket.lambda_code_bucket.id
  s3_key           = "transformation_lambda/transformation_handler.zip"
  layers = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python311:3", aws_lambda_layer_version.automated_layer.arn]
  source_code_hash = resource.aws_s3_object.transformation_lambda_code_upload.source_hash
}


# Trigger the lambda function with the S3 bucket
resource "aws_lambda_permission" "allow_transformation_put_object_event" {
  action         = "lambda:InvokeFunction"
  function_name  = aws_lambda_function.transformation_lambda.function_name
  principal      = "s3.amazonaws.com"
  source_arn     = aws_s3_bucket.ingestion_data_bucket.arn
}

resource "aws_s3_bucket_notification" "transformation_bucket_notification" {
  bucket = aws_s3_bucket.ingestion_data_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.transformation_lambda.arn
    events              = ["s3:ObjectCreated:*"]
  }
  depends_on = [aws_lambda_permission.allow_transformation_put_object_event]
}