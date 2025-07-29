# FAQ

## How do I connect to the RDS instance through the pods

```sh
PODNAME="rdsproxy-read"
RDS_USER=$(kubectl get secret  appcd-secrets -o jsonpath='{.data.rds_username}' | base64 -D)
RDS_PASS=$(kubectl get secret  appcd-secrets -o jsonpath='{.data.rds_password}' | base64 -D)
echo "connect to RDS using the following user: ${RDS_USER} and password: '${RDS_PASS}'"
PORT=$(kubectl get secret  appcd-secrets -o jsonpath='{.data.rds_port}' | base64 -D)
RDS_ENDPOINT=$(kubectl get secret  appcd-secrets -o jsonpath='{.data.rds_read_endpoint}' | base64 -D)
kubectl run --restart=Never --image=alpine/socat ${PODNAME} -- -d -d tcp-listen:${PORT},fork,reuseaddr tcp-connect:${RDS_ENDPOINT}:${PORT}
kubectl wait --for=condition=Ready pod/${PODNAME}
kubectl port-forward pod/${PODNAME} ${PORT}:${PORT}
```

## Port forward

### Temporal web

```sh
kubectl port-forward svc/temporal-web 8080:8080 -n temporal
open "http://localhost:8080"
```

### Open Grafana

```sh
GRAFANA_USERNAME=$(kubectl get secret kube-prometheus-stack-grafana -o jsonpath="{.data.admin-user}" -n kube-prometheus-stack | base64 -D)
GRAFANA_PASSWORD=$(kubectl get secret kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" -n kube-prometheus-stack | base64 -D)
echo "Use the following username: ${GRAFANA_USERNAME} and password: ${GRAFANA_PASSWORD}"
kubectl port-forward  svc/kube-prometheus-stack-grafana 8080:80 -n kube-prometheus-stack
open "http://localhost:8080"
```

### Karpenter logs

```sh
kubectl logs -f -n karpenter -c controller -l app.kubernetes.io/name=karpenter --max-log-requests 3
```

### Logs from services

```sh
kubectl logs -l app.kubernetes.io/managed-by=Helm --tail 10 -f  --max-log-requests 155 | egrep -v "health|kube-probe" 
```

### Getting Logs for any request ID

Check response header for `X-Request-Id`

```sh
get_log() {
    local pod_name=$(echo $1 | cut -d'/' -f1)
    kubectl logs pods/${pod_name} --tail 1000 | grep -i $1
}

get_log <Request-Id>

```

### Get ingress logs

```sh
kubectl logs -l app.kubernetes.io/instance=ingress-nginx --tail 10 -f -n ingress-nginx
```
