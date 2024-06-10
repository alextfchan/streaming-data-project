resource "aws_kinesis_stream" "input_stream" {
    name = var.kinesis_input
    shard_count = 1
    retention_period = 72
}