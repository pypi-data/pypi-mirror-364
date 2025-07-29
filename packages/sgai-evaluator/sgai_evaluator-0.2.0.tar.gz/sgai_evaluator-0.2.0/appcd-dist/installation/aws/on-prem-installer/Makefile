init:
	tofu init

plan:
	tofu plan

apply:
	tofu apply $(TF_APPLY_YES)

fmt:
	@tofu fmt -recursive

apply/y: fmt init
	@$(MAKE) TF_APPLY_YES='--auto-approve -var vpc_id=""' apply
	$(tofu output -raw connect)
