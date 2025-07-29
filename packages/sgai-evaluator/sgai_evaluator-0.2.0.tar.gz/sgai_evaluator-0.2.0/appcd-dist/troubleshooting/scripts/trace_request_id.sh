#/bin/sh -exu

run_query() {
    local request_id=${1}
    local query_id=$(aws logs start-query \
        --log-group-name /aws/containerinsights/cloud-eks/application \
        --start-time $(date -v-30M "+%s") \
        --end-time $(date "+%s") \
        --query-string 'fields @timestamp,kubernetes.container_name, log | filter log_processed.requestID =~ "appcd-"' |
        jq -r '.queryId')
    echo ${query_id}
}

main() {
    local request_id=${1}
    local query_id=$(run_query ${request_id})
    local logfile=$(mktemp)
    echo "Query started (query id: $query_id), please hold ... Log entries will be saved in ${logfile} too " && sleep 5

    aws logs get-query-results --query-id $query_id >$logfile

    jq -r '.results[] | [.[] | {(.field): .value}] | add | [.["@timestamp"], .["kubernetes.container_name"], .log] | @tsv' $logfile

    echo "Query results are also saved in $logfile"
}

main $*
