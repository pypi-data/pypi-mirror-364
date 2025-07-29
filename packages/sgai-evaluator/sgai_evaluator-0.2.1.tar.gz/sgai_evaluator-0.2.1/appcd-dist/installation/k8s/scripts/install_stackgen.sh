#!/bin/sh -eu

TEMPORAL_VERSION="0.33.0"

scripts_dir=$(dirname $0)
base_dir=$(dirname $scripts_dir)

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

create_namespace_if_not_exists() {
    local namespace=$1
    kubectl get namespace $namespace || kubectl create namespace $namespace
}

set_registry_password() {
    local namespace=$1
    kubectl get secret/ghcr-pkg -n $namespace -o=jsonpath --template={.metadata.name} >/dev/null || kubectl create -n $namespace secret \
        docker-registry ghcr-pkg \
        --docker-server=https://ghcr.io \
        --docker-username="github_username" \
        --docker-password=${STACKGEN_PAT} \
        --docker-email=sks
}

install_temporal() {
    local namespace=$1
    ## Create postgres secrets for temporal
    kubectl get secret -n $namespace temporal-default-store || kubectl create secret generic temporal-default-store \
        --from-literal=password="thanks_for_trying_appcd"
    kubectl get secret -n $namespace  temporal-visibility-store || kubectl create secret generic temporal-visibility-store \
        --from-literal=password="thanks_for_trying_appcd"

    log "Installing temporal"
    helm upgrade -n $namespace --debug --wait --install \
        --values ./dev/temporal.yaml \
        temporal \
        https://github.com/temporalio/helm-charts/releases/download/temporal-${TEMPORAL_VERSION}/temporal-${TEMPORAL_VERSION}.tgz

    log "running job to create the namespace"
    kubectl apply -n $namespace -f ./dev/temporal-namespace-job.yaml
}

main() {
    local namespace=$1
    create_namespace_if_not_exists $namespace

    kubectl config set-context --current --namespace=$namespace

    set_registry_password $namespace

    log "Installing postgresql"
    helm upgrade --debug --wait --install \
        --values ${base_dir}/dev/postgres.yaml \
        postgresql \
        oci://registry-1.docker.io/bitnamicharts/postgresql

    log "Installing secrets"
    kubectl apply -f ./dev/secrets.yaml

    install_temporal $namespace

    log "Installing appcd"
    helm upgrade \
        --wait --debug --install \
        --values ./dev/dev.$namespace.yaml appcd \
        ./appcd-dist
}

main $*
