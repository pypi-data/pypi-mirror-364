#!/bin/sh -e

scm_api_urls_github="https://api.github.com/"
scm_api_urls_bitbucket="https://bitbucket.org/"
scm_api_urls_gitlab="https://gitlab.com/"
scm_api_urls_gitea="https://gitea.com/"
scm_api_urls_file="/data/repos"

RED='\033[0;31m'
NC='\033[0m'

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] \t $*"
}

exit_if_error() {
    if [ "$1" -eq 0 ]; then
        return
    fi
    local exit_code=${1}
    shift
    log "${RED}[ERROR]\t $*${NC}"
    exit "$exit_code"
}

get_scm_config_info() {
    printf "Enter scm config type (bitbucket/github/gitlab/gitea/file): "
    read -r scm_type
    if [ -z "$scm_type" ]; then
        exit_if_error 1 "SCM type is required"
    fi

    scm_api_url=$(eval "echo \${scm_api_urls_${scm_type}}")
    #validate that the scm type is valid in the array
    if [ -z "${scm_api_url}" ]; then
        exit_if_error 1 "SCM type is invalid"
    fi

    if [ "$scm_type" = "file" ]; then
        scm_api_url=${scm_api_urls_file}
        return
    fi

    printf "Enter Access token: "
    read -r -s secret_api_key
    echo ""
    if [ -z "$secret_api_key" ]; then
        exit_if_error 1 "Access token is required"
    fi

    printf "Enter scm api url: (${scm_api_url}) "
    read -r scm_api_url_input
    if [ ! -z "$scm_api_url_input" ]; then
        scm_api_url=${scm_api_url_input}
    fi

    log "[INFO] StackGen will be using ${scm_type} as the scm type connecting to ${scm_api_url}"
}

write_appcd_config() {
    cat <<EOF >config/appcd/config.yaml
server:
  database:
    connectionString: '/db/appcd.db'
  scm:
    ${scm_type}:
      type: ${scm_type}
      token: \${APPCD_SCM_TOKEN}
      api: ${scm_api_url}
EOF
}

docker_login() {
    if [ -z "$APPCD_PAT" ]; then
        if [ $(docker images ghcr.io/appcd-dev/appcd-dist/appcd -qa | wc -l) != 0 ]; then
            log "[INFO] StackGen images already exists, skipping docker login"
            return
        fi
        exit_if_error 1 "APPCD_PAT is required to login to registry."
    fi
    echo $APPCD_PAT | docker login ghcr.io -u appcd-user --password-stdin
}

setup() {
    log "Thank you for trying StackGen. Lets get started by configuring your SCM."

    docker_login

    get_scm_config_info

    write_appcd_config

    echo "APPCD_SCM_TOKEN=${secret_api_key}" >.secrets

    log "StackGen is now configured. Starting the server by running 'docker compose up'"
}

main() {
    if [ ! -f config/appcd/config.yaml ]; then
        setup
    fi

    mkdir -p out/data out/iac db data logs
    chmod +w out/data out/iac db data logs

    docker compose pull

    docker compose up -d

    log "[INFO] StackGen should be running now. You can access the UI at http://localhost:8001"

    log "[INFO] tailing logs"
    # To check if the SCM configuration is valid, we could visit http://localhost:8080/api/v1/repositories to list of repositories
    docker compose logs -f | tee logs/stackgen_$(date +%s).log
}

main
