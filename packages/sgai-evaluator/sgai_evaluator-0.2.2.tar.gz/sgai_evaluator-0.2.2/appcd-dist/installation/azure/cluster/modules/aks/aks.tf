
locals {
  node_pools = {
    user = {
      name                  = "user"
      kubernetes_cluster_id = module.aks.aks_id
      vm_size               = var.agents_size
      enable_auto_scaling   = true
      node_count            = 1
      min_count             = 1
      max_count             = 5
      vnet_subnet_id        = data.azurerm_subnet.system.id
      # priority        = "Spot"
      tags = local.tags
    }
    ingress = {
      name                  = "ingress"
      kubernetes_cluster_id = module.aks.aks_id
      vm_size               = var.agents_size
      enable_auto_scaling   = true
      node_count            = 1
      min_count             = 1
      max_count             = 2
      vnet_subnet_id        = data.azurerm_subnet.system.id
      # priority              = "Spot"
      node_labels = {
        "nodepoolname" = "ingress"
      }
      tags = local.tags
    }
  }
  tags = merge(
    var.tags,
    {
      "module" = "cluster"
    }
  )
  database_names = ["appcd", "iacgen", "temporal", "temporalvisibility", "dex", "exporter"]
  setup_alerts   = length(var.alert_email_ids) > 0 || length(var.alert_sms_numbers) > 0
}


module "network" {
  source              = "Azure/network/azurerm"
  version             = "5.3.0"
  vnet_name           = var.resource_group
  resource_group_name = var.resource_group
  address_space       = "10.52.0.0/16"
  subnet_prefixes     = ["10.52.0.0/20", "10.52.16.0/20", "10.52.32.0/20"]

  subnet_names = ["system", "subnet-alb", "subnet-pgsql"]
  use_for_each = true
  subnet_delegation = {
    subnet-alb = [
      {
        name = "delegation"
        service_delegation = {
          name = "Microsoft.ServiceNetworking/trafficControllers"
          actions = [
            "Microsoft.Network/virtualNetworks/subnets/join/action",
          ]
        }
      }
    ]
    subnet-pgsql = [
      {
        name = "delegation"
        service_delegation = {
          name = "Microsoft.DBforPostgreSQL/flexibleServers"
          actions = [
            "Microsoft.Network/virtualNetworks/subnets/join/action",
          ]
        }
      }
    ]
  }
  subnet_service_endpoints = {
    "system" : ["Microsoft.Sql"]
    "subnet-pgsql" : ["Microsoft.Storage"]
  }
  tags = local.tags
}

# Create a DataSource to be able to reference subnet by name elsewhere
data "azurerm_subnet" "system" {
  name                 = "system"
  virtual_network_name = module.network.vnet_name
  resource_group_name  = var.resource_group
  depends_on           = [module.network]
}

data "azurerm_subnet" "subnet-alb" {
  name                 = "subnet-alb"
  virtual_network_name = module.network.vnet_name
  resource_group_name  = var.resource_group
  depends_on           = [module.network]
}

data "azurerm_subnet" "subnet-pgsql" {
  name                 = "subnet-pgsql"
  virtual_network_name = module.network.vnet_name
  resource_group_name  = var.resource_group
  depends_on           = [module.network]
}

module "aks" {
  source                            = "github.com/Azure/terraform-azurerm-aks.git?ref=9.0.0"
  resource_group_name               = var.resource_group
  kubernetes_version                = var.kubernetes_version
  automatic_channel_upgrade         = "patch"
  orchestrator_version              = var.kubernetes_version
  prefix                            = module.naming.kubernetes_cluster.name
  network_plugin                    = "azure"
  vnet_subnet_id                    = data.azurerm_subnet.system.id
  os_disk_size_gb                   = 50
  sku_tier                          = "Standard"
  role_based_access_control_enabled = true
  rbac_aad                          = false
  private_cluster_enabled           = false
  enable_auto_scaling               = true
  enable_host_encryption            = false
  log_analytics_workspace_enabled   = true
  agents_min_count                  = 1
  agents_max_count                  = 2
  agents_count                      = null
  agents_max_pods                   = 40
  agents_pool_name                  = "system"
  agents_availability_zones         = ["1", "2"]
  agents_type                       = "VirtualMachineScaleSets"
  agents_size                       = var.agents_size

  auto_scaler_profile_balance_similar_node_groups = true
  auto_scaler_profile_enabled                     = true

  agents_labels = {
    "nodepool" : "defaultnodepool"
  }

  agents_tags = {
    "Agent" : "defaultnodepoolagent"
  }
  storage_profile_enabled = true
  storage_profile_blob_driver_enabled = true

  workload_autoscaler_profile = {
    keda_enabled                    = true
    vertical_pod_autoscaler_enabled = true
  }

  network_policy             = "azure"
  net_profile_dns_service_ip = "10.0.0.10"
  net_profile_service_cidr   = "10.0.0.0/16"

  key_vault_secrets_provider_enabled = true
  secret_rotation_enabled            = true
  secret_rotation_interval           = "3m"

  workload_identity_enabled = true
  oidc_issuer_enabled       = true

  node_pools = local.node_pools

  depends_on = [module.network]
  tags       = local.tags
}

data "azurerm_kubernetes_cluster" "aks" {
  name                = module.aks.aks_name
  resource_group_name = var.resource_group
}

resource "azurerm_role_assignment" "aks_network_contributor" {
  principal_id         = data.azurerm_kubernetes_cluster.aks.identity[0].principal_id
  role_definition_name = "Network Contributor"
  scope                = module.network.vnet_id
}

resource "random_id" "db_password" {
  byte_length = 16
}

module "naming" {
  source  = "Azure/naming/azurerm"
  version = "~> 0.2.0"

  prefix = [var.prefix]
}


resource "azurerm_postgresql_flexible_server" "postgresql" {
  name                   = module.naming.postgresql_server.name
  resource_group_name    = var.resource_group
  location               = var.location
  sku_name               = var.postgres_sku_name
  version                = var.postgres_server_version
  storage_mb             = var.postgres_size_in_mb
  zone                   = 1
  administrator_login    = "postgres"
  administrator_password = "${random_id.db_password.hex}_P@ssw0rd"

  backup_retention_days = var.postgres_backup_retention_days
  tags                  = local.tags

  delegated_subnet_id           = data.azurerm_subnet.subnet-pgsql.id
  private_dns_zone_id           = azurerm_private_dns_zone.this.id
  public_network_access_enabled = false
  depends_on                    = [azurerm_private_dns_zone_virtual_network_link.this]
}

# Enable the uuid-ossp extension
resource "azurerm_postgresql_flexible_server_configuration" "uuid_ossp" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.postgresql.id
  value     = "uuid-ossp"
}

resource "azurerm_private_dns_zone" "this" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = var.resource_group
}

resource "azurerm_private_dns_zone_virtual_network_link" "this" {
  name                  = "link"
  resource_group_name   = var.resource_group
  private_dns_zone_name = azurerm_private_dns_zone.this.name
  virtual_network_id    = module.network.vnet_id
  depends_on            = [module.network]
}

resource "azurerm_postgresql_flexible_server_database" "this" {
  for_each = toset(local.database_names)

  name      = each.value
  server_id = azurerm_postgresql_flexible_server.postgresql.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

resource "azurerm_postgresql_flexible_server_configuration" "this" {
  name      = "require_secure_transport"
  server_id = azurerm_postgresql_flexible_server.postgresql.id
  value     = "off"
}

resource "azurerm_monitor_action_group" "this" {
  count               = local.setup_alerts ? 1 : 0
  name                = "appCD-alert-group"
  resource_group_name = var.resource_group
  short_name          = "appCD-alert"
  dynamic "email_receiver" {
    for_each = var.alert_email_ids
    content {
      name                    = "receiver-${email_receiver.value}"
      email_address           = email_receiver.value
      use_common_alert_schema = true
    }
  }
  dynamic "sms_receiver" {
    for_each = var.alert_sms_numbers
    content {
      name         = "receiver-${sms_receiver.value}"
      phone_number = sms_receiver.value
      country_code = var.alert_phone_number_country_code
    }
  }
}

resource "azurerm_monitor_metric_alert" "cpu_usage" {
  count               = local.setup_alerts ? 1 : 0
  name                = "appCD-alert-from-AKS-high-cpu-usage"
  resource_group_name = var.resource_group
  scopes              = [module.aks.aks_id]
  description         = "Send alert if node cpu usage is greater than 90%"
  severity            = 2
  enabled             = true
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.ContainerService/managedClusters"
    metric_name      = "node_cpu_usage_percentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 90
  }

  action {
    action_group_id = azurerm_monitor_action_group.this[0].id
  }
}

resource "azurerm_monitor_metric_alert" "disk_usage" {
  count               = local.setup_alerts ? 1 : 0
  name                = "appCD-alert-from-AKS-high-disk-usage"
  resource_group_name = var.resource_group
  scopes              = [module.aks.aks_id]
  description         = "Send alert if disk usage is greater than 80%"
  severity            = 2
  enabled             = true
  frequency           = "PT5M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.ContainerService/managedClusters"
    metric_name      = "node_disk_usage_percentage"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 80
  }

  action {
    action_group_id = azurerm_monitor_action_group.this[0].id
  }
}

resource "azurerm_monitor_metric_alert" "node_status" {
  count               = local.setup_alerts ? 1 : 0
  name                = "appCD-alert-from-AKS-notready-or-unknown-node-status"
  resource_group_name = var.resource_group
  scopes              = [module.aks.aks_id]
  description         = "Send alert if nodes are in unknown/notready state"
  severity            = 2
  enabled             = true
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.ContainerService/managedClusters"
    metric_name      = "kube_node_status_condition"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 0

    dimension {
      name     = "status2"
      operator = "Include"
      values   = ["notready", "unknown"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.this[0].id
  }
}

resource "azurerm_monitor_metric_alert" "pod_status" {
  count               = local.setup_alerts ? 1 : 0
  name                = "appCD-alert-from-AKS-failed-or-unknown-pod-status"
  resource_group_name = var.resource_group
  scopes              = [module.aks.aks_id]
  description         = "Send alert if pods are in unknown/failed state"
  severity            = 2
  enabled             = true
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.ContainerService/managedClusters"
    metric_name      = "kube_pod_status_phase"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 0

    dimension {
      name     = "phase"
      operator = "Include"
      values   = ["failed", "unknown"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.this[0].id
  }
}
