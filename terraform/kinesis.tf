resource "aws_kinesis_stream" "input_stream" {
    name                = var.kinesis_input
    shard_count         = 1
    retention_period    = 12
}

resource "aws_kinesis_stream" "output_stream" {
    name                = var.kinesis_output
    shard_count         = 1
    retention_period    = 72
}