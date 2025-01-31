module "prod_config" {
  source                  = "./env-config"
  app_name                = local.app_name
  default_region          = module.project_config.default_region
  environment             = "prod"
  network_name            = "prod"
  database_instance_count = 2
  service_override_extra_environment_variables = {
    # In prod, post results to the #z_bot-sprint-reporting channel in slack
    ACTION = "post-results"
  }
}
