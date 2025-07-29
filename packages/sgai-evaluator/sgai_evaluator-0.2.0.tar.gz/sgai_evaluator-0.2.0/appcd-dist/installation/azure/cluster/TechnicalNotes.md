# Stackgen On Prem installation

## What gets installed by default

### Azure Resources

| Type                     | Who installs it                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------ |
| Resource Group           | [main.tf](./main.tf) `azurerm_resource_group`                                              |
| Azure Network            | [./modules/aks](./modules/aks/main.tf) Using `Azure/network/azurerm`                       |
| Azure Kubernetes cluster | [./modules/aks](./modules/aks/main.tf)  Using `Azure/terraform-azurerm-aks`                |
| Azure Flexible Postgres  | [./modules/aks](./modules/aks/main.tf)  Using `azurerm_postgresql_flexible_server`         |
| Azure Private DNS zone   | [./modules/aks](./modules/aks/main.tf)  Using `azurerm_postgresql_flexible_server`         |
| Azure Monitor Action     | [./modules/aks](./modules/aks/main.tf)  Using `azurerm_monitor_action_group`               |
| Azure postgres database  | [./modules/aks](./modules/aks/main.tf) using `azurerm_postgresql_flexible_server_database` |

### Kubernetes Resources

| Type              | Description                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| namespace         | namespace where all the Stackgen deployments are running                                             |
| ingress           | [ingress](https://github.com/nginxinc/kubernetes-ingress) based of nginx                          |
| kubernetes_secret | Secret that will let the nodes pull Stackgen container images                                        |
| kubernetes_secret | Named `temporal-visibility-store` that contains the postgres db password                          |
| kubernetes_secret | Named `appcd-secrets` that contains postgres connection parameters for Stackgen                      |
| kubernetes_secret | Named `temporal_default_store` that contains db password for temporal to connect                  |
| helm_release      | temporal helm release, We use temporal for workload                                               |
| helm_release      | appcd helm deployment, the image tags are specified in [values/images.yaml](./values/images.yaml) |

## Details

### Postgres

There is provision in the installation [variables.tf](./variables.tf) to provide information about pre-existing postgres server that you might want to use, in that case, Please make sure that the required databases are created upfont.

For more info look at variable `existing_postgres` in [variables.tf](./variables.tf)

We need these databases to be created in the postgres server.

1. `appcd`: Used by appcd orchestrator.
2. `iacgen`: Used by topology manager.
3. `exporter`: Used to IAC exporter functionality.
4. `temporal`: Used for HA workload management.
5. `temporalvisibility`: Used for HA workload management
6. `dex`: Used for authentication with third party systems

### Monitoring

monitoring is setup only if `alert_email_ids` variable has been provided, by default the mails go to [alert@appcd.com](mailto:alert+azure@appcd.com)

### Nginx Ingress

We chose nginx ingress as we need support for `master` and `minion` concept to reuse the same host values

### Temporal

You can read more about temporal [here](https://docs.temporal.io/).

### SCM Configuration

appCD works better with SCM configuration, so you will have to create a client_id and secret on the respective SCM. Check variable `scm_configuration` in [variables.tf](./variables.tf)
