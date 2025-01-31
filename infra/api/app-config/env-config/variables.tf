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

variable "has_search" {
  type    = bool
  default = false
}

variable "search_data_instance_type" {
  type    = string
  default = "or1.medium.search"
}

variable "search_master_instance_type" {
  type    = string
  default = "m6g.large.search"
}

variable "search_engine_version" {
  type = string
}

variable "search_data_instance_count" {
  type    = number
  default = 3
}

variable "search_data_volume_size" {
  type    = number
  default = 20
}

variable "search_availability_zone_count" {
  type    = number
  default = 3
}

variable "has_database" {
  type = bool
}

variable "database_instance_count" {
  description = "Number of database instances. Should be 2+ for production environments."
  type        = number
  default     = 1
}

variable "database_enable_http_endpoint" {
  description = "Enable HTTP endpoint (data API). Enables the Query Editor in the AWS Console."
  type        = bool
  default     = false
}

variable "database_max_capacity" {
  description = "Maximum capacity of the Aurora Serverless v2 cluster"
  type        = number
}

variable "database_min_capacity" {
  description = "Minimum capacity of the Aurora Serverless v2 cluster"
  type        = number
}

variable "instance_cpu" {
  description = "CPU units for the ECS container instances"
  type        = number
  default     = 1024
}

variable "instance_memory" {
  description = "Memory in MiB for the ECS container instances"
  type        = number
  default     = 2048
}

variable "instance_desired_instance_count" {
  description = "Number of desired ECS container instances for the service"
  type        = number
  default     = 1
}

variable "instance_scaling_max_capacity" {
  description = "Maximum number of ECS container instances for the service"
  type        = number
}

variable "instance_scaling_min_capacity" {
  description = "Minimum number of ECS container instances for the service"
  type        = number
}

variable "has_incident_management_service" {
  type = bool
}

variable "domain" {
  type        = string
  description = "DNS domain of the website managed by HHS"
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
