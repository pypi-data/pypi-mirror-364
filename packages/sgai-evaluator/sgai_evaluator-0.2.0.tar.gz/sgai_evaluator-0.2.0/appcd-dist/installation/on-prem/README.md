# StackGen On-Premise Installation Guide

## Table of Contents

- [StackGen On-Premise Installation Guide](#stackgen-on-premise-installation-guide)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Fresh installation with cluster creation](#fresh-installation-with-cluster-creation)
    - [Installation on existing cluster](#installation-on-existing-cluster)
    - [Securing the StackGen Installation](#securing-the-stackgen-installation)
    - [SCM configuration](#scm-configuration)
    - [More advanced configurations](#more-advanced-configurations)
  - [Upgrade](#upgrade)
  - [Uninstall](#uninstall)

## Introduction

This document provides instructions for installing and configuring the [StackGen](https://stackgen.com/) server on-premise.

## Prerequisites

Before you begin, ensure that you have the following:

- [ ] Install [tofu](https://opentofu.org/) or [terraform](https://www.terraform.io/) CLI to manage the infrastructure.
- [ ] Logged into [aws](https://aws.amazon.com/) account.
- [ ] A valid domain name for the StackGen server.
- [ ] Have a valid certificate for the domain you want to use for the StackGen server.
- [ ] [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed on your machine.

## Installation

### Fresh installation with cluster creation

1. [ ] Create a tfvars file with the following content:

   ```hcl
   domain = "stackgen.acme.org"
   load-balancer-ssl-cert-arn = "arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012"
   STACKGEN_PAT="PAT_TOKEN_FROM_STACKGEN_TEAM"
   ```

2. [ ] Bootstrap StackGen using `install.sh` script:

   ```sh
   ./install.sh [--auto-approve] 
   ```

3. [ ] Add a DNS "A" record in Route53. Set Alias to true, and select the Network Load Balancer

4. [ ] [Optional] For private installations, you would need to allow the IP address of
the machine where you are running  `terraform apply` so that terraform can connect to the EKS cluster and make changes

### Installation on existing cluster

1. Create a `tfvars` similar to [sample.auto.tfvars](./env/sample.tfvars) with the following content:
2. Run the following command:

```sh
./install.sh
```

### Securing the StackGen Installation

Check [Securing the StackGen Installation](./docs/Securing_the_StackGen_Installation.md) for more details.

### SCM configuration

Check [SCM Configuration](./docs/SCM_Configuration.md) for more details.

### More advanced configurations

After the installation, you can configure the StackGen server by updating the `appcd-configmap` config in the `appcd` namespace.

NOTE: We do not recommend doing this on your own unless you are familiar with the StackGen configuration. Please check with [support@stackgen.com](mailto:support@stackgen.com) for any assistance.

```sh
kubectl edit configmap appcd-configmap -n appcd

# Look for appcd_config_file and update the file with the desired configuration.
```

## Upgrade

To upgrade StackGen, run the following command:

```sh
./upgrade.sh
```

## Uninstall

To uninstall StackGen, run the following command:

```sh
tofu destroy
```
