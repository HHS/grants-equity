variable "has_database" {
  type        = bool
  description = "whether the application has a database"
  default     = true
}

variable "environment_name" {
  type        = string
  description = "name of the application environment"
}

variable "network_name" {
  type        = string
  description = "Human readable identifier for the VPC"
}
