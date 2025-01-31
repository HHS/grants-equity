locals {
  app_name                        = "api"
  environments                    = ["dev", "prod"]
  project_name                    = module.project_config.project_name
  has_database                    = true
  has_incident_management_service = false

  # Whether or not the application depends on external non-AWS services.
  # If enabled, the networks associated with this application's environments
  # will have NAT gateways, which allows the service in the private subnet to
  # make calls to the internet.
  has_external_non_aws_service = true

  environment_configs = {
    dev     = module.dev_config
    staging = module.staging_config
    prod    = module.prod_config
  }

  # Map from environment name to the account name for the AWS account that
  # contains the resources for that environment. Resources that are shared
  # across environments use the key "shared".
  # The list of configured AWS accounts can be found in /infra/account
  # by looking for the backend config files of the form:
  #   <ACCOUNT_NAME>.<ACCOUNT_ID>.s3.tfbackend
  #
  # Projects/applications that use the same AWS account for all environments
  # will refer to the same account for all environments. For example, if the
  # project has a single account named "myaccount", then infra/accounts will
  # have one tfbackend file myaccount.XXXXX.s3.tfbackend, and the
  # account_names_by_environment map will look like:
  #
  #   account_names_by_environment = {
  #     shared  = "myaccount"
  #     dev     = "myaccount"
  #     staging = "myaccount"
  #     prod    = "myaccount"
  #   }
  #
  # Projects/applications that have separate AWS accounts for each environment
  # might have a map that looks more like this:
  #
  #   account_names_by_environment = {
  #     shared  = "dev"
  #     dev     = "dev"
  #     staging = "staging"
  #     prod    = "prod"
  #   }
  account_names_by_environment = {
    shared  = "simpler-grants-gov"
    dev     = "simpler-grants-gov"
    staging = "simpler-grants-gov"
    prod    = "simpler-grants-gov"
  }

  # The name of the network that contains the resources shared across all
  # application environments, such as the build repository.
  # The list of networks can be found in /infra/networks
  # by looking for the backend config files of the form:
  #   <NETWORK_NAME>.s3.tfbackend
  shared_network_name = "dev"
}

module "project_config" {
  source = "../../project-config"
}
