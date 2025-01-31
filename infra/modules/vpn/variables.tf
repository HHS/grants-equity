variable "environment_name" {
  description = "The name of the environment"
  type        = string
}

variable "second_octet" {
  description = "The second octet of the VPC CIDR block"
  type        = number
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}
