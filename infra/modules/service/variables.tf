variable "service_name" {
  description = "name of the service, to be used for infra structure resource naming"
  validation {
    condition     = can(regex("^[-_\\da-z]+$", var.service_name))
    error_message = "use only lower case letters, numbers, dashes, and underscores"
  }
}

variable "image_tag" {
  type        = string
  description = "The tag of the image to deploy"
}

variable "image_repository_url" {
  type        = string
  description = "The full URL of the container image repository, used instead of image_repository_name if set."
  default     = null
}

variable "image_repository_name" {
  type        = string
  description = "The name of the container image repository"
  default     = null
}

variable "desired_instance_count" {
  type        = number
  description = "Number of instances of the task definition to place and keep running."
  default     = 1
}

variable "cpu" {
  type        = number
  default     = 256
  description = "Number of cpu units used by the task, expessed as an integer value, e.g 512 "
}

variable "memory" {
  type        = number
  default     = 512
  description = "Amount (in MiB) of memory used by the task. e.g. 2048"
}


variable "container_port" {
  type        = number
  description = "The port number on the container that's bound to the user-specified"
  default     = 8000
}

variable "environment_name" {
  type        = string
  description = "The name of the environment"
  default     = ""
}

variable "hostname" {
  type        = string
  description = "The hostname to override the default AWS configuration"
  default     = null
}

variable "vpc_id" {
  type        = string
  description = "Uniquely identifies the VPC."
}

variable "public_subnet_ids" {
  type        = list(any)
  description = "Public subnet ids in VPC"
}

variable "private_subnet_ids" {
  type        = list(any)
  description = "Private subnet ids in VPC"
}

variable "extra_environment_variables" {
  type        = map(string)
  description = "Additional environment variables to pass to the service container. Map from environment variable name to the value."
  default     = {}
}

variable "scheduled_jobs" {
  description = "Variable for configuration of the step functions scheduled job"
  type = map(object({
    task_command        = list(string)
    schedule_expression = string
    state               = string
  }))
  default = {}
}

variable "s3_buckets" {
  type = map(object({
    env_var = string
    public  = bool
    paths = list(object({
      path    = string
      env_var = string
    }))
  }))
  default = {}
}

variable "enable_drafts_bucket" {
  description = "does the service need a private S3 bucket for draft document storage"
  type        = bool
  default     = false
}

variable "secrets" {
  type = set(object({
    name      = string
    valueFrom = string
  }))
  description = "List of configurations for defining environment variables that pull from SSM parameter store"
}

variable "aws_services_security_group_id" {
  type        = string
  description = "Security group ID for VPC endpoints that access AWS Services"
}

variable "db_vars" {
  description = "Variables for integrating the app service with a database"
  type = object({
    security_group_ids = list(string)
    connection_info = object({
      host        = string
      port        = string
      user        = string
      db_name     = string
      schema_name = string
    })
  })
  default = null
}

variable "app_access_policy_arn" {
  description = "The ARN of the IAM policy to attach to the app service role for database access"
  type        = string
  default     = null
}

variable "migrator_access_policy_arn" {
  description = "The ARN of the IAM policy to attach to the migrator task role for database access"
  type        = string
  default     = null
}

variable "extra_policies" {
  description = "Map of extra IAM policies to attach to the service's task role. The map's keys define the resource name in terraform."
  type        = map(string)
  default     = {}
}

variable "cert_arn" {
  description = "The ARN for the TLS certificate passed in from the app service layer"
  type        = string
  default     = null
}

variable "enable_autoscaling" {
  description = "Flag to enable or disable auto-scaling"
  type        = bool
  default     = false
}

variable "max_capacity" {
  description = "Maximum number of tasks for autoscaling"
  type        = number
  default     = 4
}

variable "min_capacity" {
  description = "Minimum number of tasks for autoscaling"
  type        = number
  default     = 2
}

variable "is_temporary" {
  description = "Whether the service is meant to be spun up temporarily (e.g. for automated infra tests). This is used to disable deletion protection for the load balancer."
  type        = bool
}

variable "readonly_root_filesystem" {
  description = "Whether the container has a read-only root filesystem"
  type        = bool
  default     = true
}

variable "domain" {
  description = "The domain name for the service"
  type        = string
  default     = null
}

variable "drop_linux_capabilities" {
  description = "Whether to drop linux parameters"
  type        = bool
  default     = true
}

variable "enable_load_balancer" {
  description = "Whether to enable a load balancer for the service"
  type        = bool
  default     = true
}

variable "enable_alb_cdn" {
  description = "Whether to enable an ALB origin CDN for the service. Cannot be enabled at the same time as the S3 CDN."
  type        = bool
  default     = false
}

variable "enable_s3_cdn" {
  description = "Whether to enable a S3 origin CDN for the service. Cannot be enabled at the same time as the ALB CDN."
  type        = bool
  default     = false
}

variable "s3_cdn_bucket_name" {
  description = "The name of the S3 bucket to use for the S3 CDN."
  type        = string
  default     = null
}

variable "s3_cdn_domain_name" {
  description = "The domain name of the S3 bucket to use for the S3 CDN"
  type        = string
  default     = null
}

variable "healthcheck_command" {
  description = "The command to run to check the health of the container, used on the container health check"
  type        = list(string)
  default = [
    "CMD-SHELL",
    "wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1"
  ]
}

variable "healthcheck_path" {
  description = "The path to check the health of the container, used on the load balancer health check"
  type        = string
  default     = "/health"
}
