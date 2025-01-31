module "prod_config" {
  source                          = "./env-config"
  app_name                        = local.app_name
  default_region                  = module.project_config.default_region
  environment                     = "prod"
  network_name                    = "prod"
  has_database                    = local.has_database
  has_incident_management_service = local.has_incident_management_service
  domain                          = "simpler.grants.gov"

  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
  # https://us-east-1.console.aws.amazon.com/ecs/v2/clusters/frontend-prod/services/frontend-prod/health?region=us-east-1
  # instance_desired_instance_count and instance_scaling_min_capacity are scaled for 5x the average CPU and Memory
  # seen over 12 months, as of November 2024 exlucing an outlier range around February 2024.
  # The math is: 5 * max(average CPU or average Memory) * 1.3. The 1.3 is for a buffer.
  instance_desired_instance_count = 4
  instance_scaling_min_capacity   = 4
  # instance_scaling_max_capacity is 5x the instance_scaling_min_capacity
  instance_scaling_max_capacity = 20

  instance_cpu    = 1024
  instance_memory = 2048
}
