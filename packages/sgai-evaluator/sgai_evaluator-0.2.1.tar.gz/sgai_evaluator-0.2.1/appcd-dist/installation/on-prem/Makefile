AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity --query Account --output text)
LAMBDA_DIR      := ../../tools/aws-lambda-go/lambda
BINARY_NAME     := bootstrap
ZIP_FILE        := function.zip
LAMBDA_FUNCTION := cloudwatch-alert-lambda-go

MY_IP=$(shell curl -s http://checkip.amazonaws.com)

copy: copy/dex_artifacts lambda-package copy/lambda_function 

copy/dex_artifacts: lambda-package
	mkdir -p ./modules/k8s_deps/values/dex
	cp -r ../aws/namespace/values/dex/* ./modules/k8s_deps/values/dex

copy/lambda_function:
	cp -r ../aws/cluster/lambda.tf .
	@if [ -f lambda.tf ]; then \
		if [[ "$$(uname)" == "Darwin" ]]; then \
			sed -i '' 's|\$${module.eks.cluster_name}|\$${var.suffix}-eks|g' lambda.tf; \
			sed -i '' 's|depends_on = \[module.eks\]|depends_on = \[module.appcd_vpc_eks\]|g' lambda.tf; \
		else \
			sed -i 's|\$${module.eks.cluster_name}|\$${var.suffix}-eks|g' lambda.tf; \
			sed -i 's|depends_on = \[module.eks\]|depends_on = \[module.appcd_vpc_eks\]|g' lambda.tf; \
		fi \
	fi


package/%: copy
	zip -r stackgen-AWS-enterprise-$*.zip install.sh .gitignore README.md *.tgz main.tf output.tf variables.tf ./modules values ./images ./env docs upgrade.sh

fmt:
	tofu fmt -recursive

dev/plan: copy
	tofu plan

dev/apply: copy
	tofu apply --auto-approve

dev/destroy: copy
	tofu destroy

onprem/install:
	#  get secret from aws ssm and store in tfstate.tfvars
	aws secretsmanager get-secret-value --secret-id stackgen/dev/onprem --region ap-south-1 --output text --query SecretString > ./test.auto.tfvars
	echo terraform {\\n backend "s3" {\\n\\t region = \"us-west-2\"\\n\\t bucket = \"$(AWS_ACCOUNT_ID)-states\"\\n\\t key    = \"appcd/dev_onprem/terraform.tfstate\"\\n  }\\n} > backend.tf
	tofu init
	tofu apply --auto-approve
	aws secretsmanager put-secret-value --secret-id stackgen/dev/onprem --region ap-south-1 --secret-string file://test.auto.tfvars

helm/package:
	helm dependency update ../k8s/appcd-dist
	helm package --destination . ../k8s/appcd-dist

customer/onboard/%:
	echo 'terraform {\n  backend "s3" {\n    region = "us-west-2"\n    bucket = "$(AWS_ACCOUNT_ID)-states"\n    key    = "customer/$*/terraform.tfstate"\n  }\n}' > backend.tf
	echo "TODO=COPY_FROM_EXISTING" > $*.tfvars
	aws secretsmanager create-secret --name "stackgen/dev/customer/$*" --secret-string "file://$*.tfvars" --region us-west-2
	aws secretsmanager create-secret --name "stackgen/dev/customer/$*.backend" --secret-string "file://backend.tf" --region us-west-2

customer/list:
	aws secretsmanager list-secrets --region us-west-2 --query='SecretList[].Name' --output json | jq -r '.[]' | grep "stackgen/dev/customer" | grep -v "backend" | sed 's/stackgen\/dev\/customer\///g'

customer/values/%:
	aws secretsmanager get-secret-value --secret-id /stackgen/customer-$* --region us-west-2 --output text --query SecretString > customer-$*.yaml

customer/put/values/%:
	aws secretsmanager put-secret-value --secret-id /stackgen/customer-$* --region us-west-2 --secret-string file://customer-$*.yaml

customer/access/%:
	aws eks update-cluster-config --name customer-$*-eks --resources-vpc-config publicAccessCidrs=$(MY_IP)/32 &> update.json
	kubectx arn:aws:eks:us-west-2:${AWS_ACCOUNT_ID}:cluster/customer-$*-eks

customer/init/%:
	aws sts get-caller-identity > /dev/null || aws sso login || echo "login to aws sso"
	#  get secret from aws ssm and store in tfstate.tfvars and backend.tf
	cp $*.tfvars $*.tfvars.bkp || true
	cp backend.tf backend.tf.bkp || true
	aws secretsmanager get-secret-value --secret-id stackgen/dev/customer/$* --region us-west-2 --output text --query SecretString > $*.tfvars
	aws secretsmanager get-secret-value --secret-id stackgen/dev/customer/$*.backend --region us-west-2 --output text --query SecretString > backend.tf
	tofu init -reconfigure

customer/plan/%: customer/init/%
	tofu plan -var-file=$*.tfvars

customer/apply/%:
	tofu fmt -recursive
	tofu apply -var-file=$*.tfvars
	aws secretsmanager put-secret-value --secret-id stackgen/dev/customer/$* --region us-west-2 --secret-string file://$*.tfvars
	aws secretsmanager put-secret-value --secret-id stackgen/dev/customer/$*.backend --region us-west-2 --secret-string file://backend.tf

customer/%: customer/plan/% customer/apply/%

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
