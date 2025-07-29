DEFAULT := install

install: deps secret upgrade

deps:
	which helm > /dev/null || brew install helm
	which kubectl > /dev/null || brew install kubectl

uninstall: destroy

secret: secret/registry

secret/registry:
	@kubectl get secret/ghcr-pkg -o=jsonpath --template={.metadata.name} > /dev/null || kubectl create secret docker-registry ghcr-pkg \
    	--docker-server=https://ghcr.io \
    	--docker-username="github_username" \
		--docker-password=${STACKGEN_PAT} \
		--docker-email=sks

build:
	helm dependency  update ./appcd-dist

upgrade: build
	helm upgrade \
		--install \
		--debug --wait \
		${ARGS} appcd \
		appcd-dist

logs/%:
	kubectl logs -l app.kubernetes.io/instance=$(notdir $@) -f --tail 100

exec/%:
	kubectl exec -ti deployment/$(notdir $@) -- sh

destroy: destroy/appcd

destroy/%:
	helm uninstall $(notdir $@)  || echo "No $(notdir $@) to uninstall"

upgrade/dev/%:
	@$(MAKE) ARGS="--values ./values/dev.$(notdir $@).yaml -n appcd-$(notdir $@)" upgrade

upgrade/prod/%:
	@$(MAKE) ARGS="--values ./values/prod.$(notdir $@).yaml -n appcd-$(notdir $@)" upgrade

debug/dev/%:
	@$(MAKE) \
		ARGS="--dry-run --values ./values/dev.$(notdir $@).yaml -n appcd-$(notdir $@)" \
		upgrade

debug/prod/%:
	@$(MAKE) \
		ARGS="--dry-run --values ./values/prod.$(notdir $@).yaml -n appcd-$(notdir $@)" \
		upgrade

examples:
	@echo "make upgrade/dev/alpha to upgrade alpha namespace in dev environment"
	@echo "make upgrade/prod/cloud-prod to upgrade appcd-cloud-prod namespace in prod environment"
	@echo "make upgrade/prod/customer-innovaccer for customer-innovaccer namespace in prod environment"
	@echo "make debug/prod/cloud-prod to see plan info appcd-cloud-prod namespace in prod environment"
	@echo "make debug/dev/alpha to see plan info appcd-alpha namespace in dev environment"

i_am_done/%:
	helm uninstall -n $* appcd || echo "failed to delete appcd helm"
	helm uninstall -n $* postgresql || echo "failed to delete postgresql"
	helm uninstall -n $* temporal || echo "failed to delete temporal"
	helm uninstall -n $* postgresql || echo "failed to delete postgresql"
	kubectl delete -n $* pvc data-postgresql-0 || echo "failed to delete pvc"
	kubectl delete ns $(notdir $@) || echo "failed to delete ns"

helm/package: build
	helm package --destination ../on-prem appcd-dist

helm/update-index:
	aws s3 cp s3://appcd-public-releases/charts/index.yaml index.yaml
	helm repo index --merge index.yaml --url https://appcd-public-releases.s3.us-east-2.amazonaws.com/charts/ .
	aws s3 cp index.yaml s3://appcd-public-releases/charts/index.yaml
