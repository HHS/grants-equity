module "dev_config" {
  source                          = "./env-config"
  app_name                        = local.app_name
  default_region                  = module.project_config.default_region
  environment                     = "dev"
  has_database                    = local.has_database
  database_instance_count         = 2
  database_enable_http_endpoint   = true
  has_incident_management_service = local.has_incident_management_service
  database_max_capacity           = 16
  database_min_capacity           = 2

  has_search = true
  # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html#choosing-version
  opensearch_engine_version = "OpenSearch_2.15"

  # Runs, but with everything disabled.
  # See api/src/data_migration/command/load_transform.py for argument specifications.
  load_transform_args = [
    "poetry",
    "run",
    "flask",
    "data-migration",
    "load-transform",
    "--no-load",
    "--no-transform",
    "--no-set-current",
  ]

  service_override_extra_environment_variables = {
  }
}
