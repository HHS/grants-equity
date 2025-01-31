variable "app_name" {
  type = string
}

variable "environment" {
  description = "name of the application environment (e.g. dev, staging, prod)"
  type        = string
}

variable "network_name" {
  description = "Human readable identifier of the network / VPC"
  type        = string
}

variable "default_region" {
  description = "default region for the project"
  type        = string
}

variable "has_database" {
  type = bool
}

variable "has_incident_management_service" {
  type = bool
}

variable "instance_cpu" {
  description = "CPU units for the ECS container instances"
  type        = number
  default     = 256
}

variable "instance_memory" {
  description = "Memory in MiB for the ECS container instances"
  type        = number
  default     = 512
}

variable "instance_desired_instance_count" {
  type    = number
  default = 1
}

variable "instance_scaling_min_capacity" {
  type    = number
  default = 1
}

variable "instance_scaling_max_capacity" {
  type    = number
  default = 5
}

variable "domain" {
  description = "Public domain for the website, which is managed by HHS ITS."
  type        = string
  default     = null
}

variable "service_override_extra_environment_variables" {
  type        = map(string)
  description = <<EOT
    Map that overrides the default extra environment variables defined in environment-variables.tf.
    Map from environment variable name to environment variable value
    EOT
  default     = {}
}
