#!/bin/bash
# -----------------------------------------------------------------------------
# This script sets up the terraform backend for the AWS account that you are
# currently authenticated into and creates the terraform backend config file.
#
# The script takes a human readable account name that is used to prefix the tfbackend
# file that is created. This is to make it easier to visually identify while
# tfbackend file corresponds to which AWS account. The account ID is still
# needed since all AWS accounts are guaranteed to have an account ID, and the
# account ID cannot change, whereas other things like the AWS account alias
# can change and is not guaranteed to exist.
#
# Positional parameters:
#   ACCOUNT_NAME (required) - human readable name for the AWS account that you're
#     authenticated into. The account name will be used to prefix the created
#     tfbackend file so that it's easier to visually identify as opposed to
#     identifying the file using the account id.
#     For example, you have an account per environment, the account name can be
#     the name of the environment (e.g. "prod" or "staging"). Or if you are
#     setting up an account for all lower environments, account name can be "lowers".
#     If your AWS account has an account alias, you can also use that.
# -----------------------------------------------------------------------------
set -euo pipefail

ACCOUNT_NAME=$1

ACCOUNT_ID=$(./bin/current-account-id.sh)
REGION=$(./bin/current-region.sh)

# Get project name
terraform -chdir="infra/project-config" apply -refresh-only -auto-approve> /dev/null
PROJECT_NAME=$(terraform -chdir=infra/project-config output -raw project_name)

TF_STATE_BUCKET_NAME="$PROJECT_NAME-$ACCOUNT_ID-$REGION-tf"
TF_STATE_KEY="infra/account.tfstate"

echo "=================="
echo "Setting up account"
echo "=================="
echo "ACCOUNT_NAME=$ACCOUNT_NAME"
echo "ACCOUNT_ID=$ACCOUNT_ID"
echo "PROJECT_NAME=$PROJECT_NAME"
echo "TF_STATE_BUCKET_NAME=$TF_STATE_BUCKET_NAME"
echo "TF_STATE_KEY=$TF_STATE_KEY"
echo "REGION=$REGION"
echo
echo "------------------------------------------------------------------------------"
echo "Bootstrapping the account by creating an S3 backend with minimal configuration"
echo "------------------------------------------------------------------------------"
echo
echo "Creating bucket: $TF_STATE_BUCKET_NAME"
# For creating buckets outside of us-east-1, a LocationConstraint needs to be set
# For creating buckets in us-east-1, LocationConstraint cannot be set
# See https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html
CREATE_BUCKET_CONFIGURATION=("")
if [ "$REGION" != "us-east-1" ]; then
  CREATE_BUCKET_CONFIGURATION=("--create-bucket-configuration" "LocationConstraint=$REGION")
fi

aws s3api create-bucket --bucket "$TF_STATE_BUCKET_NAME" --region "$REGION" "${CREATE_BUCKET_CONFIGURATION[@]}" > /dev/null
echo
echo "----------------------------------"
echo "Creating rest of account resources"
echo "----------------------------------"
echo

cd infra/accounts

# Create the OpenID Connect provider for GitHub Actions to allow GitHub Actions
# to authenticate with AWS and manage AWS resources. We create the OIDC provider
# via AWS CLI rather than via Terraform because we need to first check if there
# is already an existing OpenID Connect provider for GitHub Actions. This check
# is needed since there can only be one OpenID Connect provider per URL per AWS
# account.
github_arn=$(aws iam list-open-id-connect-providers | jq -r ".[] | .[] | .Arn" | grep github || echo "")

if [[ -z ${github_arn} ]]; then
  aws iam create-open-id-connect-provider \
    --url "https://token.actions.githubusercontent.com" \
    --client-id-list "sts.amazonaws.com" \
    --thumbprint-list "0000000000000000000000000000000000000000"
fi

# Create the infrastructure for the terraform backend such as the S3 bucket
# for storing tfstate files and the DynamoDB table for tfstate locks.
# -reconfigure is used in case this isn't the first account being set up
# and there is already a .terraform directory
terraform init \
  -reconfigure \
  -input=false \
  -backend-config="bucket=$TF_STATE_BUCKET_NAME" \
  -backend-config="key=$TF_STATE_KEY" \
  -backend-config="region=$REGION"

# Import the bucket that we created in the previous step so we don't recreate it
# But first check if the bucket already exists in the state file. If we are
# re-running account setup and the bucket already exists then skip the import step
if ! terraform state list module.backend.aws_s3_bucket.tf_state; then
  terraform import module.backend.aws_s3_bucket.tf_state "$TF_STATE_BUCKET_NAME"
fi

terraform apply \
  -input=false \
  -auto-approve

cd -

MODULE_DIR=infra/accounts
BACKEND_CONFIG_NAME="$ACCOUNT_NAME.$ACCOUNT_ID"
./bin/create-tfbackend.sh "$MODULE_DIR" "$BACKEND_CONFIG_NAME" "$TF_STATE_KEY"
