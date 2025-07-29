AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity --query Account --output text)
DEV_CERT_ARN=arn:aws:acm:us-west-2:339712749745:certificate/1b666650-1e6c-49fc-b533-1427a8aaf594

dep:
	@which -a tofu > /dev/null || brew install tofu
	tofu init

fmt:
	tofu fmt

plan: dep
	tofu plan

apply: plan
	tofu apply

apply/y:
	tofu apply --auto-approve

init:
	tofu init \
		-backend-config="bucket=${AWS_ACCOUNT_ID}-states" \
		-backend-config="key=s3/terraform.tfstate" \
		-backend-config="region=us-west-2"
