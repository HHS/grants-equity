package test

import (
	"flag"
	"fmt"
	"strings"
	"testing"
	"time"

	http_helper "github.com/gruntwork-io/terratest/modules/http-helper"
	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/shell"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

var uniqueId = strings.ToLower(random.UniqueId())
var workspaceName = fmt.Sprintf("t-%s", uniqueId)
var appName = flag.String("app_name", "", "name of subdirectory that holds the app's infrastructure code")

func TestService(t *testing.T) {
	BuildAndPublish(t)

	imageTag := shell.RunCommandAndGetOutput(t, shell.Command{
		Command:    "git",
		Args:       []string{"rev-parse", "HEAD"},
		WorkingDir: "./",
	})
	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		Reconfigure:  true,
		TerraformDir: fmt.Sprintf("../%s/service/", *appName),
		Vars: map[string]interface{}{
			"environment_name": "dev",
			"image_tag":        imageTag,
		},
	})

	fmt.Println("::group::Initialize service module")
	TerraformInit(t, terraformOptions, "dev.s3.tfbackend")
	fmt.Println("::endgroup::")

	defer terraform.WorkspaceDelete(t, terraformOptions, workspaceName)
	fmt.Println("::group::Select new terraform workspace")
	terraform.WorkspaceSelectOrNew(t, terraformOptions, workspaceName)
	fmt.Println("::endgroup::")

	defer DestroyService(t, terraformOptions)
	fmt.Println("::group::Create service layer")
	terraform.Apply(t, terraformOptions)
	fmt.Println("::endgroup::")

	WaitForServiceToBeStable(t, workspaceName)
	RunEndToEndTests(t, terraformOptions)
}

func BuildAndPublish(t *testing.T) {
	fmt.Println("::group::Initialize build-repository module")
	// terratest currently does not support passing a file as the -backend-config option
	// so we need to manually call terraform rather than using terraform.Init
	// see https://github.com/gruntwork-io/terratest/issues/517
	// it looks like this PR would add functionality for this: https://github.com/gruntwork-io/terratest/pull/558
	// after which we add BackendConfig: []string{"dev.s3.tfbackend": terraform.KeyOnly} to terraformOptions
	// and replace the call to terraform.RunTerraformCommand with terraform.Init
	TerraformInit(t, &terraform.Options{
		TerraformDir: fmt.Sprintf("../%s/build-repository/", *appName),
	}, "shared.s3.tfbackend")
	fmt.Println("::endgroup::")

	fmt.Println("::group::Build release")
	shell.RunCommand(t, shell.Command{
		Command:    "make",
		Args:       []string{"release-build", fmt.Sprintf("APP_NAME=%s", *appName)},
		WorkingDir: "../../",
	})
	fmt.Println("::endgroup::")

	fmt.Println("::group::Publish release")
	shell.RunCommand(t, shell.Command{
		Command:    "make",
		Args:       []string{"release-publish", fmt.Sprintf("APP_NAME=%s", *appName)},
		WorkingDir: "../../",
	})
	fmt.Println("::endgroup::")
}

func WaitForServiceToBeStable(t *testing.T, workspaceName string) {
	fmt.Println("::group::Wait for service to be stable")
	appName := *appName
	environmentName := "dev"
	serviceName := fmt.Sprintf("%s-%s-%s", workspaceName, appName, environmentName)
	shell.RunCommand(t, shell.Command{
		Command:    "aws",
		Args:       []string{"ecs", "wait", "services-stable", "--cluster", serviceName, "--services", serviceName},
		WorkingDir: "../../",
	})
	fmt.Println("::endgroup::")
}

func RunEndToEndTests(t *testing.T, terraformOptions *terraform.Options) {
	fmt.Println("::group::Check service for healthy status 200")
	serviceEndpoint := terraform.Output(t, terraformOptions, "service_endpoint")
	http_helper.HttpGetWithRetryWithCustomValidation(t, serviceEndpoint, nil, 5, 1*time.Second, func(responseStatus int, responseBody string) bool {
		return responseStatus == 200
	})
	// Hit feature flags endpoint to make sure Evidently integration is working
	featureFlagsEndpoint := fmt.Sprintf("%s/feature-flags", serviceEndpoint)
	http_helper.HttpGetWithRetryWithCustomValidation(t, featureFlagsEndpoint, nil, 5, 1*time.Second, func(responseStatus int, responseBody string) bool {
		return responseStatus == 200
	})
	fmt.Println("::endgroup::")
}

func EnableDestroyService(t *testing.T, terraformOptions *terraform.Options) {
	fmt.Println("::group::Set force_destroy = true and prevent_destroy = false for s3 buckets in service layer")
	shell.RunCommand(t, shell.Command{
		Command: "sed",
		Args: []string{
			"-i.bak",
			"s/force_destroy = false/force_destroy = true/g",
			"infra/modules/service/access-logs.tf",
		},
		WorkingDir: "../../",
	})
	shell.RunCommand(t, shell.Command{
		Command: "sed",
		Args: []string{
			"-i.bak",
			"s/prevent_destroy = true/prevent_destroy = false/g",
			"infra/modules/service/access-logs.tf",
		},
		WorkingDir: "../../",
	})
	shell.RunCommand(t, shell.Command{
		Command: "sed",
		Args: []string{
			"-i.bak",
			"s/force_destroy = false/force_destroy = true/g",
			"infra/modules/storage/main.tf",
		},
		WorkingDir: "../../",
	})

	// Clone the options and set targets to only apply to the buckets
	terraformOptions, err := terraformOptions.Clone()
	require.NoError(t, err)
	terraformOptions.Targets = []string{
		"module.service.aws_s3_bucket.access_logs",
		"module.storage.aws_s3_bucket.storage",
	}
	terraform.Apply(t, terraformOptions)
	fmt.Println("::endgroup::")
}

func DestroyService(t *testing.T, terraformOptions *terraform.Options) {
	EnableDestroyService(t, terraformOptions)
	fmt.Println("::group::Destroy service layer")
	terraform.Destroy(t, terraformOptions)
	fmt.Println("::endgroup::")
}
