data "aws_region" "current" {}

locals {
  tags = merge(module.project_config.default_tags, {
    network_name = var.network_name
    description  = "VPC resources"
  })
  region = module.project_config.default_region

  network_config = module.project_config.network_configs[var.network_name]

  # List of configuration for all applications, even ones that are not in the current network
  # If project has multiple applications, add other app configs to this list
  app_configs = [module.app_config]

  # List of configuration for applications that are in the current network
  # An application is in the current network if at least one of its environments
  # is mapped to the network
  apps_in_network = [
    for app in local.app_configs :
    app
    if anytrue([
      for environment_config in app.environment_configs : true if environment_config.network_name == var.network_name
    ])
  ]

  # Whether any of the applications in the network have a database
  has_database = anytrue([for app in local.apps_in_network : app.has_database])

  # Whether any of the applications in the network have dependencies on an external non-AWS service
  has_external_non_aws_service = anytrue([for app in local.apps_in_network : app.has_external_non_aws_service])
}

terraform {
  required_version = "< 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.68.0"
    }
  }

  backend "s3" {
    encrypt = "true"
  }
}

provider "aws" {
  region = local.region
  default_tags {
    tags = local.tags
  }
}

module "project_config" {
  source = "../project-config"
}

module "app_config" {
  source = "../api/app-config"
}

module "network" {
  source                                  = "../modules/network"
  name                                    = var.environment_name
  has_database                            = local.has_database
  database_subnet_group_name              = var.environment_name
  aws_services_security_group_name_prefix = module.project_config.aws_services_security_group_name_prefix
  second_octet                            = module.project_config.network_configs[var.environment_name].second_octet
}

module "dms_networking" {
  source                       = "../modules/dms-networking"
  environment_name             = var.environment_name
  our_vpc_id                   = module.network.vpc_id
  our_cidr_block               = module.network.vpc_cidr
  grants_gov_oracle_cidr_block = module.project_config.network_configs[var.environment_name].grants_gov_oracle_cidr_block
}
