output "database_config" {
  value = var.has_database ? {
    region                      = var.default_region
    cluster_name                = "${var.app_name}-${var.environment}"
    app_username                = "app"
    migrator_username           = "migrator"
    schema_name                 = "app"
    app_access_policy_name      = "${var.app_name}-${var.environment}-app-access"
    migrator_access_policy_name = "${var.app_name}-${var.environment}-migrator-access"
    instance_count              = var.database_instance_count
  } : null
}

output "network_name" {
  value = var.network_name
}

output "service_config" {
  value = {
    region = var.default_region
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

output "domain" {
  value = var.domain
}
