#!/bin/sh -eu

DIR="$(dirname "$0")"
WORK_DIR=$(mktemp -d -p "$DIR")
NAMESPACE="appcd"
VALUES_YAML="./values/appcd-final.yaml"
IS_DEBUG="false"

log(){
    echo "$(date +%Y-%m-%dT%H:%M:%S) - $*"
}

check_deps() {
    which -a kubectl > /dev/null || { echo "kubectl is not installed" 1>&2; exit 1; }
    which -a helm > /dev/null || { echo "helm is not installed" 1>&2; exit 1; }
    which -a curl > /dev/null || { echo "curl is not installed" 1>&2; exit 1; }
}

usage() { echo "Usage: $0 [-n namespace] [-v values.yaml] -d -h" 1>&2; exit 1; }

while getopts ":n:v:dh" o; do
case "${o}" in
    h)
        usage
        ;;
    n)
        NAMESPACE=${OPTARG}
        ;;
    v)
        # get the absolute path of the values.yaml file
        VALUES_YAML=${OPTARG}
        ;;
    d)
        IS_DEBUG="true"
        ;;
    *)
        usage
        ;;
esac
done
if [ ! -f "$VALUES_YAML" ]; then
    usage
fi
        
shift $((OPTIND-1))

download_latest_artifacts() {
    log "Downloading latest stackgen artifacts"
    curl -u stackgen:user -o "${WORK_DIR}/images.yaml" https://releases.stackgen.com/appcd-dist/images/latest.yaml
    curl -u stackgen:user -o "${WORK_DIR}/stackgen.tgz" https://releases.stackgen.com/appcd-dist/charts/latest.tgz
}

cleanup() {      
  rm -rf "$WORK_DIR"
  log "Deleted temp working directory $WORK_DIR"
}

trap cleanup EXIT

upgrade_appcd_chart() {
    command_opts=""
    if [ "$IS_DEBUG" = "true" ]; then
        command_opts=" --debug --dry-run"
    fi
    log "Upgrading stackgen chart"
    helm upgrade --dry-run ${command_opts} \
        --install appcd "${WORK_DIR}/stackgen.tgz" \
        --namespace "${NAMESPACE}" \
        --values "${VALUES_YAML}" \
        --values "${WORK_DIR}/images.yaml"
}

show_stats() {
    log "Getting stats"
    kubectl get pods -n "${NAMESPACE}"
    helm history appcd -n "${NAMESPACE}"
}

main() {
    check_deps
    download_latest_artifacts
    upgrade_appcd_chart
    show_stats
}

main "$@"
