# Dynamically fetch the project number
PROJECT_ID := $(shell gcloud config get-value project)
PROJECT_NUMBER := $(shell gcloud projects describe "$(PROJECT_ID)" --format="value(projectNumber)")
STATES_DIR := $(PROJECT_NUMBER)-states

# Setup target to ensure required tools are installed
setup:
	@which -a tofu > /dev/null || (echo "tofu not found, please install it" && exit 1)

# Clean up Terraform-related files
clean:
	rm -rf .terraform.lock.hcl .terraform

# Initialize Terraform (Tofu) for a specific environment
init/%:
	tofu init -reconfigure \
		-backend-config="bucket=$(STATES_DIR)" \
		-backend-config="prefix=$*"

# Format Terraform files
fmt:
	tofu fmt -recursive

# Plan Terraform changes for a specific environment
plan/%: init/%
	tofu plan -var-file="./tfvars/$*.tfvars"

# Refresh the Terraform state for a specific environment
refresh/%: init/%
	tofu refresh -var-file="./tfvars/$*.tfvars"

# Apply the Terraform configuration for a specific environment
apply/%: init/%
	tofu apply -var-file="./tfvars/$*.tfvars"

# Destroy the Terraform resources for a specific environment
destroy/%: init/%
	tofu destroy -var-file="./tfvars/$*.tfvars"

# Default target to run the Terraform plan
default: plan

# Dependency setup
deps: build
	mkdir -p docs ./values/dex
	cp ../on-prem/docs/*.md ./docs/
	cp ../on-prem/values/images.yaml ./values/images.yaml
	cp -r ../on-prem/modules/k8s_deps/values/* ./values
	cp ../on-prem/install.sh ./
	cp -r ../aws/namespace/values/dex/* ./values/dex/

# Build Helm dependencies
build: helm/package
	helm dependency update ../k8s/appcd-dist

# Helm package creation
helm/package:
	helm package --destination . ../k8s/appcd-dist

# Package Terraform resources for deployment
package/%:
	zip -r stackgen-gcp-enterprise-$*.zip docs/ install.sh modules values main.tf README.md variables.tf *.tgz 

# Cleanup test artifacts
test/clean:
	rm -rf stackgen-gcp-enterprise-beta.zip ./test appcd-dist*.tgz

# Package test artifacts
test/package: deps
	$(MAKE) package/beta

# Run tests
test: test/clean test/package
	unzip stackgen-gcp-enterprise-beta.zip -d ./test
