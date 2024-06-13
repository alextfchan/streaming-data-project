provider "aws" {
    region      = "eu-west-2"
}

resource "aws_s3_bucket" "terraform_remote_state" {
    bucket      = "streaming-data-project-backend-s3-bucket"

    lifecycle {
        prevent_destroy = true
    }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
    bucket      = aws_s3_bucket.terraform_remote_state.id

    versioning_configuration {
      status    = "Enabled"
    }
}
