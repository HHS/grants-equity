data "aws_vpc" "network" {
  filter {
    name   = "tag:Name"
    values = [module.project_config.network_configs[var.environment_name].vpc_name]
  }
}

data "aws_subnets" "database" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.network.id]
  }
  filter {
    name   = "tag:subnet_type"
    values = ["database"]
  }
}

locals {
  # The prefix key/value pair is used for Terraform Workspaces, which is useful for projects with multiple infrastructure developers.
  # By default, Terraform creates a workspace named “default.” If a non-default workspace is not created this prefix will equal “default”,
  # if you choose not to use workspaces set this value to "dev"
  prefix = terraform.workspace == "default" ? "" : "${terraform.workspace}-"

  # Add environment specific tags
  tags = merge(module.project_config.default_tags, {
    environment = var.environment_name
    description = "Database resources for the ${var.environment_name} environment"
  })

  environment_config = module.app_config.environment_configs[var.environment_name]
  database_config    = local.environment_config.database_config
  network_config     = module.project_config.network_configs[local.environment_config.network_name]
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
  region = local.database_config.region
  default_tags {
    tags = local.tags
  }
}

module "project_config" {
  source = "../../project-config"
}

module "app_config" {
  source = "../app-config"
}

data "aws_security_groups" "aws_services" {
  filter {
    name   = "group-name"
    values = ["${module.project_config.aws_services_security_group_name_prefix}*"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.network.id]
  }
}

module "database" {
  source                      = "../../modules/database"
  name                        = "${local.prefix}${local.database_config.cluster_name}"
  access_policy_name          = "${local.prefix}${local.database_config.access_policy_name}"
  app_access_policy_name      = "${local.prefix}${local.database_config.app_access_policy_name}"
  migrator_access_policy_name = "${local.prefix}${local.database_config.migrator_access_policy_name}"
  # The following are not AWS infra resources and therefore do not need to be
  # isolated via the terraform workspace prefix
  app_username                   = local.database_config.app_username
  migrator_username              = local.database_config.migrator_username
  schema_name                    = local.database_config.schema_name
  instance_count                 = local.database_config.instance_count
  enable_http_endpoint           = true
  vpc_id                         = data.aws_vpc.network.id
  private_subnet_ids             = data.aws_subnets.database.ids
  aws_services_security_group_id = data.aws_security_groups.aws_services.ids[0]
  database_subnet_group_name     = var.environment_name
  environment_name               = var.environment_name
  grants_gov_oracle_cidr_block   = module.project_config.network_configs[var.environment_name].grants_gov_oracle_cidr_block
}
