# Variables
AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
LAMBDA_DIR      := ../../../tools/aws-lambda-go/lambda
BINARY_NAME     := bootstrap
ZIP_FILE        := function.zip
LAMBDA_FUNCTION := cloudwatch-alert-lambda-go

# Dependency: Ensure tofu is installed and initialized
dep:
	@which -a tofu > /dev/null || brew install tofu
	tofu init -upgrade

# Format the configuration using tofu
fmt:
	tofu fmt

# Terraform planning and applying
plan: dep
	tofu plan

apply: plan
	tofu apply

apply/eks:
	tofu apply

# Reinitialize backend with dynamic AWS account and state file key
init/%: lambda-package
	tofu init -reconfigure -upgrade \
		-backend-config="bucket=$(AWS_ACCOUNT_ID)-states" \
		-backend-config="key=appcd/eks/$*.tfstate" \
		-backend-config="region=us-west-2"

# Targets that use specific variable files from tfvars directory
apply/%: 
	@$(MAKE) init/$*
	tofu apply -var-file "./tfvars/$*.tfvars"

plan/%: 
	@$(MAKE) init/$*
	tofu plan -var-file "./tfvars/$*.tfvars"

refresh/%:
	@$(MAKE) init/$*
	tofu refresh -var-file "./tfvars/$*.tfvars"

# Run tfsec with a minimum severity filter for specific tfvars file
tfsec/%:
	@which -a tfsec > /dev/null || brew install tfsec
	tfsec --minimum-severity=CRITICAL --tfvars-file=./tfvars/$*.tfvars .

# Uncomment and adjust if you need a destroy target
# destroy/%:
# 	@read -p "Are you sure you want to destroy $*? [y/N] " confirm && [ $$confirm = "y" ] && tofu destroy -var-file "./tfvars/$*.tfvars"

# Create EKS and VPC for development environment

otel/secret/registry:
	@if kubectl get ns open-telemetry > /dev/null 2>&1; then \
		kubectl get secret ghcr-pkg -n open-telemetry -o=jsonpath='{.metadata.name}' > /dev/null 2>&1 || \
		kubectl create secret docker-registry ghcr-pkg \
			--docker-server=https://ghcr.io \
			--docker-username="github_username" \
			--docker-password=${STACKGEN_PAT} \
			--docker-email=sks \
			-n open-telemetry; \
	else \
		echo "Namespace 'open-telemetry' does not exist. Skipping secret creation."; \
	fi

create/dev/%: 
	@$(MAKE) init/$*
	tofu apply \
		-var load-balancer-ssl-cert-arn="$(DEV_CERT_ARN)" \
		-var suffix=$* \
		-var region=us-west-2 \
		-target=module.vpc \
		-target=module.eks

# Create EKS and VPC for production environment
create/prod/%: 
	@$(MAKE) init/$*
	tofu apply \
		-var load-balancer-ssl-cert-arn="$(PROD_CERTN_ARN)" \
		-var suffix=$* \
		-var region=us-west-2 \
		-target=module.vpc \
		-target=module.eks

# Build the Go Lambda function for Linux (for AWS Lambda)
lambda-build:
	@echo "🔨 Building the Go Lambda function..."
	cd $(LAMBDA_DIR) && GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o $(BINARY_NAME) main.go
	@echo "✅ Build complete: $(LAMBDA_DIR)/$(BINARY_NAME)"

# Package the Lambda function into a zip file
lambda-package: lambda-build
	@echo "📦 Packaging the Lambda function..."
	cd $(LAMBDA_DIR) && zip $(ZIP_FILE) $(BINARY_NAME)
	cp $(LAMBDA_DIR)/$(ZIP_FILE) $(ZIP_FILE)
	@echo "✅ Package created: $(LAMBDA_DIR)/$(ZIP_FILE)"

# Examples to help users know which targets to run
examples:
	@echo "make refresh/developer"
	@echo "make plan/developer"
	@echo "make apply/developer"
	@echo "Following commands are for PROD: Beware"
	@echo "make refresh/cloud"
	@echo "make plan/cloud"
	@echo "make apply/cloud"

# Run tfsec for the entire project
tfsec:
	@which -a tfsec > /dev/null || brew install tfsec
	tfsec .
