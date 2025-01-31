variable "name" {
  type        = string
  description = "Name to give the VPC. Will be added to the VPC under the 'network_name' tag."
}

variable "second_octet" {
  type        = number
  description = "Second octet of the VPC CIDR block. Must be between 0 and 255."
}

variable "aws_services_security_group_name_prefix" {
  type        = string
  description = "Prefix for the name of the security group attached to VPC endpoints"
}

variable "database_subnet_group_name" {
  type        = string
  description = "Name of the database subnet group"
}

variable "has_database" {
  type        = bool
  description = "Whether the application(s) in this network have a database. Determines whether to create VPC endpoints needed by the database layer."
  default     = false
}

variable "has_external_non_aws_service" {
  type        = bool
  description = "Whether the application(s) in this network need to call external non-AWS services. Determines whether or not to create NAT gateways."
  default     = true
}
