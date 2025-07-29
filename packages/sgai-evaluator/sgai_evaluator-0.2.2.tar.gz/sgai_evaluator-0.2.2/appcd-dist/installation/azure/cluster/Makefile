setup:
	which -a tofu > /dev/null || (echo "tofu not found, please install it" && exit 1)

fmt:
	tofu fmt -recursive

init:
	tofu init -reconfigure \
		-backend-config="resource_group_name=cesarappcdstates-rg" \
		-backend-config="storage_account_name=cesarappcdstatessa" \
		-backend-config="container_name=tfstate" \
		-backend-config="key=cluster.terraform.tfstate"

plan: init
	tofu plan

apply: init
	tofu apply

apply/y: init
	tofu apply -auto-approve

k8s/configure:
	$(shell tofu output -raw aks_setup)

deps:
	mkdir -p docs
	cp ../../on-prem/docs/*.md ./docs/
	cp ../../on-prem/values/images.yaml ./values/images.yaml
	cp -r ../../on-prem/modules/k8s_deps/values/* ./values
	cp ../../on-prem/install.sh ./

package/%: deps
	zip -r stackgen-azure-enterprise-$*.zip TechnicalNotes.md modules docs/ *.md *.tgz main.tf appcd_deps.tf output.tf variables.tf values images ./env
