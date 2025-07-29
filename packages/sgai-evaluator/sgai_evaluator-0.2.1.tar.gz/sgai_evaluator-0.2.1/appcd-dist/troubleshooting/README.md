# appCD Prod Troubleshooting

## Get logs for a requestID

To get logs for a requestID, you can use the following command:

```bash
./scripts/trace_request_id.sh $REQUEST_ID
```

## Check number of nodes in the cluster

To check the number of nodes in the cluster, you can use the following command:

```bash
kubectl get nodes

kubectl top nodes
```

## Check if there were many spot requests history

To check if there were many spot requests, you can use the following command:

```bash
aws ec2 describe-spot-instance-requests --query 'SpotInstanceRequests[*].[InstanceId,State,Status.Code,Status.Message,SpotPrice,LaunchedAvailabilityZone,CreateTime]' --output table
```
