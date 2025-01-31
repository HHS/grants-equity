module "staging_config" {
  source                          = "./env-config"
  app_name                        = local.app_name
  default_region                  = module.project_config.default_region
  environment                     = "staging"
  network_name                    = "staging"
  has_database                    = local.has_database
  database_enable_http_endpoint   = true
  has_incident_management_service = local.has_incident_management_service

  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
  # https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/api-staging/services/api-staging/health?region=us-east-1
  # instance_desired_instance_count and instance_scaling_min_capacity are scaled for the average CPU and Memory
  # seen over 12 months, as of November 2024 exlucing an outlier range around February 2024.
  # With a minimum of 2, so CPU doesn't spike to infinity on deploys.
  instance_desired_instance_count = 2
  instance_scaling_min_capacity   = 2
  # instance_scaling_max_capacity is 5x the instance_scaling_min_capacity
  instance_scaling_max_capacity = 10

  # https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html
  # https://us-east-1.console.aws.amazon.com/rds/home?region=us-east-1#database:id=api-dev;is-cluster=true;tab=monitoring
  # database_min_capacity is average api-staging ServerlessDatabaseCapacity seen over 12 months, as of November 2024
  database_min_capacity = 2
  # database_max_capacity is 5x the database_min_capacity
  database_max_capacity   = 10
  database_instance_count = 2

  has_search = true
  # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html#choosing-version
  search_engine_version = "OpenSearch_2.15"

  service_override_extra_environment_variables = {
    # Login.gov OAuth
    ENABLE_AUTH_ENDPOINT = 0
  }
}
