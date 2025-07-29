---
sidebar_position: 2.6
---

# Azure Deployment Guide

## Table of Contents

  - [Azure Deployment Guide](#azure-deployment-guide)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Understanding StackGen resources created](#understanding-stackgen-resources-created)
  - [Advanced Configuration](#advanced-configuration)
    - [Securing the StackGen Installation](#securing-the-stackgen-installation)
    - [SCM configuration](#scm-configuration)
    - [More advanced configurations](#more-advanced-configurations)
  - [Uninstall](#uninstall)

## Introduction

This document provides instructions for installing and configuring the [StackGen](https://stackgen.com/) server on AKS(Azure Kubernetes Service).

## Prerequisites

Before you begin, ensure that you have the following:

- [ ] Install [tofu](https://opentofu.org/) or [terraform](https://www.terraform.io/) CLI to manage the infrastructure.
- [ ] Logged into [Azure](https://portal.azure.com/) account.
   - Ensure that you have privileges to create resource group and resources on Azure.
- [ ] A valid domain name for the StackGen server.
- [ ] Have a valid certificate for the domain you want to use for the StackGen server.

## Installation

1. [ ] run `tofu init`
2. [ ] Create a tfvars file with the following content:

   ```hcl
   domain = "acme.stackgen.com"
   STACKGEN_PAT="PAT_TOKEN_FROM_STACKGEN_TEAM"
   prefix = "prefix-assigned-to-resource-names"
   ```

3. Run the following command to load the variables file:

   ```sh
   tofu apply -var-file=<path-to-tfvars-file>
   ```

4. [ ] Bootstrap StackGen using `tofu`.

   ```sh
   tofu apply
   ```

5. [ ] Get the external IP of the ingress controller and add it as an "A" DNS record for your domain.

## Understanding StackGen resources created:

1. The above terraform script will create a separate resource group with following resources:
    1. Virtual Network
    2. AKS
    3. Log Analytics Workspace
    4. ContainerInsights

2. AKS is deployed in its own virtual network created by the script.
3. AKS will need egress rules to access Github Container Registry (https://ghcr.io) to pull the StackGen and other images like nginx.


## Advanced Configuration

### Securing the StackGen Installation

Check [Securing the StackGen Installation](./docs/Securing_the_StackGen_Installation.md) for more details.

### SCM configuration

Check [SCM Configuration](./docs/SCM_Configuration.md) for more details.

### More advanced configurations

After the installation, you can configure the StackGen server by updating the `appcd-configmap` config in the `appcd` namespace.

NOTE: We do not recommend doing this on your own unless you are familiar with the StackGen configuration. Please check with [support@stackgen.com](mailto:support@stackgen.com) for further assistance.

```sh
kubectl edit configmap appcd-configmap -n appcd

# Look for stackgen_config_file and update the file with the desired configuration.
```

## Uninstall

To uninstall StackGen, run the following command:

```sh
tofu destroy
```
