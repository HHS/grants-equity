output "search_config" {
  value = var.has_search ? {
    instance_type           = var.search_data_instance_type
    instance_count          = var.search_data_instance_count
    dedicated_master_type   = var.search_master_instance_type
    engine_version          = var.search_engine_version
    volume_size             = var.search_data_volume_size
    availability_zone_count = var.search_availability_zone_count
  } : null
}

output "database_config" {
  value = var.has_database ? {
    region                      = var.default_region
    cluster_name                = "${var.app_name}-${var.environment}"
    app_username                = "app"
    migrator_username           = "migrator"
    schema_name                 = var.app_name
    app_access_policy_name      = "${var.app_name}-${var.environment}-app-access"
    migrator_access_policy_name = "${var.app_name}-${var.environment}-migrator-access"
    instance_count              = var.database_instance_count
    enable_http_endpoint        = var.database_enable_http_endpoint
    max_capacity                = var.database_max_capacity
    min_capacity                = var.database_min_capacity
  } : null
}

output "network_name" {
  value = var.network_name
}

output "service_config" {
  value = {
    region                          = var.default_region
    instance_desired_instance_count = var.instance_desired_instance_count
    instance_scaling_max_capacity   = var.instance_scaling_max_capacity
    instance_scaling_min_capacity   = var.instance_scaling_min_capacity
    instance_cpu                    = var.instance_cpu
    instance_memory                 = var.instance_memory
    extra_environment_variables = merge(
      local.default_extra_environment_variables,
      var.service_override_extra_environment_variables
    )

    secrets = local.secrets
  }
}

output "scheduled_jobs" {
  value = local.scheduled_jobs
}

output "s3_buckets" {
  value = local.s3_buckets
}

output "incident_management_service_integration" {
  value = var.has_incident_management_service ? {
    integration_url_param_name = "/monitoring/${var.app_name}/${var.environment}/incident-management-integration-url"
  } : null
}

output "domain" {
  value = var.domain
}
