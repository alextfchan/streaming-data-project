variable "ingestion_lambda" {
  type    = string
  default = "ingestion_lambda"
}

variable "transformation_lambda" {
  type    = string
  default = "transformation_lambda"
}

variable "loading_lambda" {
  type    = string
  default = "loading_lambda"
}

variable "kinesis_input" {
  type    = string
  default = "streaming_data_project_input"
}

variable "kinesis_output" {
  type    = string
  default = "streaming_data_project_output"
}