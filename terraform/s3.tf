resource "aws_s3_bucket" "lambda_code_bucket" {
  bucket = "streaming-data-lambda-code-bucket"
}

resource "aws_s3_bucket" "ingestion_data_bucket" {
  bucket = "streaming-data-ingested-data-bucket"
}

resource "aws_s3_bucket" "transformed_data_bucket" {
  bucket = "streaming-data-transformed-data-bucket"
}