dep:
	@which -a tofu > /dev/null || brew install tofu 
	tofu init

plan: dep
	tofu plan

apply: plan
	tofu apply

apply/eks:
	tofu apply --target=module.vpc_eks

apply/y:
	tofu apply --auto-approve

fmt:
	tofu fmt -recursive
