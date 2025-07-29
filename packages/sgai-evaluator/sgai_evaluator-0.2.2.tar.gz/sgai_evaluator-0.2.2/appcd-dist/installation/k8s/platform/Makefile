AWS_ACCOUNT_ID=$(shell aws sts get-caller-identity --query Account --output text)


init:
	tofu init -reconfigure \
		-backend-config="bucket=${AWS_ACCOUNT_ID}-states" \
		-backend-config="key=platform/platform.tfstate" \
		-backend-config="region=us-west-2"

fmt:
	tofu fmt  -recursive

get_tf_var:
	@aws secretsmanager get-secret-value --secret-id "platform/platform.tfvars" --query SecretString --output text --region us-west-2 > tfvars/${AWS_ACCOUNT_ID}.tfvars

plan: fmt init get_tf_var
	tofu plan --var-file=tfvars/${AWS_ACCOUNT_ID}.tfvars -out=tfplan_${AWS_ACCOUNT_ID}.plan

helper:
	@echo "You might need to set KUBE_CONFIG_PATH=~/.kube/config"

apply: plan
	@$(MAKE) helper
	tofu apply tfplan_${AWS_ACCOUNT_ID}.plan

destroy: fmt init get_tf_var
	@$(MAKE) helper
	tofu destroy --var-file=tfvars/${AWS_ACCOUNT_ID}.tfvars

refresh: fmt init get_tf_var
	@$(MAKE) helper
	tofu refresh --var-file=tfvars/${AWS_ACCOUNT_ID}.tfvars
