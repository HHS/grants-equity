data "aws_ssm_parameter" "search_username_arn" {
  count = local.environment_config.search_config != null ? 1 : 0
  name  = "/search/${local.prefix}${var.environment_name}/username"
}

data "aws_ssm_parameter" "search_password_arn" {
  count = local.environment_config.search_config != null ? 1 : 0
  name  = "/search/${local.prefix}${var.environment_name}/password"
}

data "aws_ssm_parameter" "search_endpoint_arn" {
  count = local.environment_config.search_config != null ? 1 : 0
  name  = "/search/${local.prefix}${var.environment_name}/endpoint"
}
