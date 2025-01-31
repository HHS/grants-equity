module "dev_config" {
  source         = "./env-config"
  app_name       = local.app_name
  default_region = module.project_config.default_region
  environment    = "dev"
  network_name   = "dev"
  service_override_extra_environment_variables = {
    # In dev, only show the results in the AWS console
    ACTION = "show-results"
  }
}
