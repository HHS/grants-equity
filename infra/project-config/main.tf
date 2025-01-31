locals {
  # Machine readable project name (lower case letters, dashes, and underscores)
  # This will be used in names of AWS resources
  project_name = "simpler-grants-gov"

  # Project owner (e.g. navapbc). Used for tagging infra resources.
  owner = "navapbc"

  # URL of project source code repository
  code_repository_url = "https://github.com/HHS/simpler-grants-gov"

  # Default AWS region for project (e.g. us-east-1, us-east-2, us-west-1).
  # This is dependent on where your project is located (if regional)
  # otherwise us-east-1 is a good default
  default_region = "us-east-1"

  github_actions_role_name                = "${local.project_name}-github-actions"
  aws_services_security_group_name_prefix = "aws-service-vpc-endpoints"

  network_configs = {
    dev = {
      account_name                 = "simpler-grants-gov"
      database_subnet_group_name   = "dev"
      vpc_name                     = "dev"
      second_octet                 = 0               # The second octet our the VPC CIDR block
      grants_gov_oracle_cidr_block = "10.220.0.0/16" # MicroHealth managed CIDR block where the dev origin Oracle database for Grants.gov is located
    }
    staging = {
      account_name                 = "simpler-grants-gov"
      database_subnet_group_name   = "staging"
      vpc_name                     = "staging"
      second_octet                 = 1               # The second octet our the VPC CIDR block
      grants_gov_oracle_cidr_block = "10.220.0.0/16" # MicroHealth managed CIDR block where the dev origin Oracle database for Grants.gov is located
    }
    prod = {
      account_name                 = "simpler-grants-gov"
      database_subnet_group_name   = "prod"
      vpc_name                     = "prod"
      second_octet                 = 3               # The second octet our the VPC CIDR block
      grants_gov_oracle_cidr_block = "10.250.0.0/16" # MicroHealth managed CIDR block where the prod origin Oracle database for Grants.gov is located
    }
    vpn = {
      second_octet = 4
    }
  }
}
