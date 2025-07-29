# StackGen Kubernetes Installation

## Prerequisites

- Kubernetes cluster
- Helm 3
- kubectl

## How To

```bash
export STACKGEN_PAT="STACKGEN_PAT_TOKEN"
make secret/registry
```

## Setting up k8s

```bash
## list clusters

aws eks --region us-west-2 list-clusters

aws eks update-kubeconfig --name ${CLUSTER_NAME}
```

### Install StackGen

```bash
make upgrade
```

### Installing StackGen on a new namespace

If you are trying out StackGen and dont want to provision the postgres and temporal in a scalable way, [install_stackgen.sh](./scripts/install_stackgen.sh) is your friend.

#### Pre-requisites

1. Create file `./dev/dev.<namespace>.yaml`. Check [./dev/dev.sks.yaml](./dev/dev.sks.yaml) for an example. `cp dev.sks.yaml dev.<namespace>.yaml`

```sh

# token that have access to ghcr registry

export STACKGEN_TOKEN="STACKGEN_TOKEN"
./scripts/install_stackgen.sh <namespace>

# Example
./scripts/install_stackgen.sh sks

#  this should create an ingress at <namespace>.dev.appcd.io
```
