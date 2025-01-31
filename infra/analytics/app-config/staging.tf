module "staging_config" {
  source         = "./env-config"
  app_name       = local.app_name
  default_region = module.project_config.default_region
  environment    = "staging"
  network_name   = "staging"
  service_override_extra_environment_variables = {
    # In staging, post results to the #z_bot-analytics-ci-test channel in slack
    ACTION = "post-results"
  }
}
