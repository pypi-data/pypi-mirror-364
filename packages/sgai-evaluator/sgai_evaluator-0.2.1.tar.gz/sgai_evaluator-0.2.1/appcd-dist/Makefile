include .env

DOCKER_IMAGE:=ghcr.io/appcd-dev/appcd-dist/appcd
.PHONY: install docker
DEFAULT: install docker
CURRENT_UID := $(shell id -u)
CURRENT_GID := $(shell id -g)


## saves all the required components in tar folder
save/tar/%: docker/pull
	mkdir -p build/tar
	docker pull ghcr.io/appcd-dev/appcd-dist/appcd:$*
	docker save -o build/tar/appcd-latest.tar ghcr.io/appcd-dev/appcd-dist/appcd:$*
	docker save -o build/tar/appcd-ui-latest.tar ghcr.io/appcd-dev/appcd-ui:$(APPCDUI_VERSION)
	docker save -o build/tar/appcd-iac-gen-latest.tar ghcr.io/appcd-dev/iac-gen:$(IACGEN_VERSION)
	# docker save -o build/tar/appcd-env-manager-latest.tar ghcr.io/appcd-dev/env-manager:$(ENVMANAGER_VERSION)
	cp install.sh build/tar/

tools:
	which -a yq > /dev/null || brew install yq

docker: docker/pull docker/build


docker/build: tools
	docker build \
		--build-arg APPCD_VERSION=$(APPCD_VERSION) \
		--build-arg APPCD_ANALYZER=$(APPCD_ANALYZER) \
		-t $(DOCKER_IMAGE):latest \
		.

docker/tag/%: docker/build
	docker tag $(DOCKER_IMAGE):latest $(DOCKER_IMAGE):$*

docker/generate:
	docker run \
		--rm \
		-v ${PWD}:/code \
		$(DOCKER_IMAGE):latest \
		generate \
		--scanpath=/code \
		--output /code \
		--log 2

docker/pull:
	touch .secrets
	docker pull ghcr.io/appcd-dev/appcd-analyzer:$(APPCD_ANALYZER)
	docker compose pull

dev: tools docker/build
	touch .secrets
	yq  '.services.appcd.image = "$(DOCKER_IMAGE):latest"' ./compose.yaml > compose.yaml.dev
	docker-compose -f compose.yaml.dev up

dev/down:
	docker-compose -f compose.yaml.dev down

dev/cloud: dev/file/cloud

dev/file/%: docker/build
	touch .secrets
	yq  '.services.appcd.image = "$(DOCKER_IMAGE):latest"' ./compose.$*.yaml > compose.yaml.dev
	APPCD_UID=${CURRENT_UID} APPCD_GID=${CURRENT_GID} docker-compose -f compose.yaml.dev up

local:
	docker-compose -f compose.local.yaml up -d& cd ../appcd-ui && make run-ui-dev

local/down:
	docker-compose -f compose.local.yaml down
