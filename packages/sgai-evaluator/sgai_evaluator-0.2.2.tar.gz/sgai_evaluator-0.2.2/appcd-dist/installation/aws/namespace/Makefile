AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity --query Account --output text)

clean:
	rm -rf .terraform

init/%:
	tofu init -reconfigure \
		-backend-config="bucket=${AWS_ACCOUNT_ID}-states" \
		-backend-config="key=appcd/k8s/$*.tfstate" \
		-backend-config="region=us-west-2"

apply/%:
	@$(MAKE) init/$*
	tofu apply \
		-var-file=../terraform.tfvars \
		${ARGS}

fmt:
	tofu fmt -recursive

tofu/%:
	@$(MAKE) init/$*
	tofu ${CMD} \
		-var-file=../terraform.tfvars \
		-var-file=./values/env/${ENV}.$*.tfvars

_plan/%:
	@$(MAKE) CMD=plan ENV=${ENV} tofu/$*

dev/plan/%:
	@$(MAKE) ENV=dev _plan/$*

dev/refresh/%:
	@$(MAKE) init/$*
	tofu refresh \
		-var-file=../terraform.tfvars \
		-var-file=./values/env/dev.$*.tfvars

dev/apply/%:
	@$(MAKE) init/$*
	tofu apply \
		-var-file=../terraform.tfvars \
		-var-file=./values/env/dev.$*.tfvars

prod/plan/%:
	@$(MAKE) ENV=prod _plan/$*

prod/refresh/%:
	@$(MAKE) init/$*
	tofu refresh \
		-var-file=../terraform.tfvars \
		-var-file=./values/env/prod.$*.tfvars

prod/apply/%:
	@$(MAKE) init/$*
	tofu apply \
		-var-file=../terraform.tfvars \
		-var-file=./values/env/prod.$*.tfvars
	tofu output -json

examples:
	@echo "make dev/refresh/main to refresh namespace specific resources for main in dev"
	@echo "make dev/plan/main to plan namespace specific resources for main in dev"
	@echo "make prod/plan/somenamespace to plan namespace specific resources for somenamespace in prod" 
