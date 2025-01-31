module "prod_config" {
  source                          = "./env-config"
  app_name                        = local.app_name
  default_region                  = module.project_config.default_region
  environment                     = "prod"
  network_name                    = "prod"
  has_database                    = local.has_database
  domain                          = "api.simpler.grants.gov"
  database_enable_http_endpoint   = true
  has_incident_management_service = local.has_incident_management_service

  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
  # https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/api-prod/services/api-prod/health?region=us-east-1
  # instance_desired_instance_count and instance_scaling_min_capacity are scaled for 5x the average CPU and Memory
  # seen over 12 months, as of November 2024 exlucing an outlier range around February 2024.
  # The math is: 5 * max(average CPU or average Memory) * 1.3. The 1.3 is for a buffer.
  instance_desired_instance_count = 2
  instance_scaling_min_capacity   = 2
  # instance_scaling_max_capacity is 5x the instance_scaling_min_capacity
  instance_scaling_max_capacity = 10

  # https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.setting-capacity.html
  # https://us-east-1.console.aws.amazon.com/rds/home?region=us-east-1#database:id=api-prod;is-cluster=true;tab=monitoring
  # database_min_capacity is 5x the average api-prod ServerlessDatabaseCapacity seen over 12 months, as of November 2024
  # The math is: 5 * (ServerlessDatabaseCapacity) * 1.3. The 1.3 is for a buffer.
  database_min_capacity = 20
  # max capacity is as high as it goes
  database_max_capacity   = 128
  database_instance_count = 2

  has_search = true
  # Pricing: https://aws.amazon.com/opensearch-service/pricing/
  search_master_instance_type = "m6g.large.search"
  # 20 is the minimum volume size for the or1.medium.search instance type.
  # Scale the search_data_volume_size number to meet your storage needs.
  # Scale the search_data_instance_count number to meet your compute needs.
  # The search_data_instance_count should be a multiple of the number of availability zones.
  # Use the AWS Console to determine the number of availability zones in your region.
  search_data_instance_type      = "or1.medium.search"
  search_data_volume_size        = 20
  search_data_instance_count     = 3
  search_availability_zone_count = 3
  # Versions: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html#choosing-version
  search_engine_version = "OpenSearch_2.15"

  service_override_extra_environment_variables = {
    # Set the opportunity search index to have more shards/replicas in prod
    LOAD_OPP_SEARCH_SHARD_COUNT   = 3
    LOAD_OPP_SEARCH_REPLICA_COUNT = 2

    # Login.gov OAuth
    ENABLE_AUTH_ENDPOINT     = 0
    LOGIN_GOV_ENDPOINT       = "https://secure.login.gov/"
    LOGIN_GOV_JWK_ENDPOINT   = "https://secure.login.gov/api/openid_connect/certs"
    LOGIN_GOV_AUTH_ENDPOINT  = "https://secure.login.gov/openid_connect/authorize"
    LOGIN_GOV_TOKEN_ENDPOINT = "https://secure.login.gov/api/openid_connect/token"
  }
}
