# terraform {
#   backend "azurerm" {
#         resource_group_name  = "appcd-rg"
#         storage_account_name = "appcdsa"
#         container_name       = "tfstate"
#         key                  = "cluster.terraform.tfstate"
#   }
# }


# Configure the Azure provider
provider "azurerm" {
  features {}
}


locals {
  tags = merge(var.tags, {
    purpose      = "stackgen_azure_enterprise"
    supported_by = "support@stackgen.com"
  })
}


resource "azurerm_resource_group" "this" {
  name     = "${var.prefix}-rg"
  location = var.location
  tags     = local.tags
}

module "aks" {
  depends_on         = [azurerm_resource_group.this]
  source             = "./modules/aks"
  agents_size        = var.agents_size
  resource_group     = azurerm_resource_group.this.name
  prefix             = var.prefix
  location           = var.location
  tags               = local.tags
  kubernetes_version = var.kubernetes_version
  alert_email_ids    = var.alert_email_ids
}

locals {
  temporal_helm_version             = "0.33.0"
  postgresql_administrator_password = module.aks.postgresql.administrator_password
  postgresql_fqdn                   = module.aks.postgresql.fqdn
  postgresql_administrator_login    = module.aks.postgresql.administrator_login
}

provider "helm" {
  kubernetes {
    host                   = module.aks.host
    client_certificate     = base64decode(module.aks.client_certificate)
    client_key             = base64decode(module.aks.client_key)
    cluster_ca_certificate = base64decode(module.aks.cluster_ca_certificate)
    username               = module.aks.username
    password               = module.aks.password
  }
}

provider "kubernetes" {
  host                   = module.aks.host
  client_certificate     = base64decode(module.aks.client_certificate)
  client_key             = base64decode(module.aks.client_key)
  cluster_ca_certificate = base64decode(module.aks.cluster_ca_certificate)
  username               = module.aks.username
  password               = module.aks.password
}

resource "kubernetes_namespace" "this" {
  depends_on = [module.aks.host]
  provider   = kubernetes
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_config_map" "dex_configmap" {
  metadata {
    name      = "dex-configmap"
    namespace = var.namespace
  }
  data = {
    stylecss : templatefile("${path.module}/values/dex/style.css", {})
    header : templatefile("${path.module}/values/dex/header.html", {})
    footer : templatefile("${path.module}/values/dex/footer.html", {})
    login : templatefile("${path.module}/values/dex/login.html", {})
  }
}



resource "helm_release" "dex" {
  depends_on = [
    kubernetes_config_map.dex_configmap
  ]
  count            = var.appcd_authentication.type == "none" ? 0 : 1
  name             = "dex"
  repository       = "https://charts.dexidp.io"
  chart            = "dex"
  namespace        = var.namespace
  create_namespace = false
  version          = "0.18.0"
  values = [
    templatefile("${path.module}/values/dex.yaml", {
      host_domain               = var.domain,
      appcd_authentication_type = var.appcd_authentication.type
      appcd_authentication_config = indent(8, yamlencode(merge({
        redirectURI : "https://${var.domain}/auth/callback"
      }, var.appcd_authentication.config))),
      rds_endpoint = local.postgresql_fqdn
    })
  ]
}


// install nginx ingress
resource "helm_release" "nginx_ingress" {
  depends_on = [
    kubernetes_namespace.this
  ]
  name       = "nginx-ingress"
  repository = "oci://ghcr.io/nginxinc/charts"
  chart      = "nginx-ingress"
  namespace  = var.namespace
  wait       = true
  values = [
    templatefile("${path.module}/values/nginx-ingress.yaml", {})
  ]
}

resource "kubernetes_secret" "ghcr_pkg" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "ghcr-pkg"
    namespace = var.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "https://ghcr.io" = {
          "username" = "github_username"
          "password" = var.STACKGEN_PAT
          "email"    = "support"
          "auth"     = base64encode("github_username:${var.STACKGEN_PAT}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}

resource "kubernetes_secret" "temporal_visibility_store" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "temporal-visibility-store"
    namespace = var.namespace
  }

  data = {
    password = local.postgresql_administrator_password
  }

  type = "Opaque"
}

resource "kubernetes_secret" "appcd_secrets" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "appcd-secrets"
    namespace = var.namespace
  }

  type = "Opaque"

  data = {
    rds_port          = "5432"
    rds_password      = local.postgresql_administrator_password
    rds_endpoint      = local.postgresql_fqdn
    rds_read_endpoint = local.postgresql_fqdn
    rds_username      = local.postgresql_administrator_login
  }
}


locals {
  secret_data = {}

  github_secrets = var.scm_configuration.scm_type == "github" ? {
    scm_github_client_id     = var.scm_configuration.github_config.client_id
    scm_github_client_secret = var.scm_configuration.github_config.client_secret
  } : {}

  gitlab_secrets = var.scm_configuration.scm_type == "gitlab" ? {
    gitlab_client_id     = var.scm_configuration.gitlab_config.client_id
    gitlab_client_secret = var.scm_configuration.gitlab_config.client_secret
  } : {}

  azure_devops_secrets = var.scm_configuration.scm_type == "azuredev" ? {
    scm_azure_devops_client_id     = var.scm_configuration.azuredev_config.client_id
    scm_azure_devops_client_secret = var.scm_configuration.azuredev_config.client_secret
  } : {}

  final_scm_secrets = merge(
    local.secret_data,
    local.github_secrets,
    local.gitlab_secrets,
    local.azure_devops_secrets,
  )
}

# add secrets for auth and scm
resource "kubernetes_secret" "appcd_scm_secrets" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "appcd-scm-secrets"
    namespace = var.namespace
  }

  data = local.final_scm_secrets
}

resource "kubernetes_secret" "temporal_default_store" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "temporal-default-store"
    namespace = var.namespace
  }

  data = {
    password = local.postgresql_administrator_password
  }

  type = "Opaque"
}


resource "helm_release" "temporal" {
  depends_on = [module.aks, kubernetes_secret.temporal_visibility_store, kubernetes_secret.temporal_default_store]
  name       = "temporal"
  chart      = "https://github.com/temporalio/helm-charts/releases/download/temporal-${local.temporal_helm_version}/temporal-${local.temporal_helm_version}.tgz"
  namespace  = var.namespace
  wait       = true
  values = [
    templatefile("${path.module}/values/temporal.yaml", {
      enable_ops : var.enable_ops,
      domain : var.domain,
      postgres_host : local.postgresql_fqdn,
      postgres_port : 5432,
      postgres_user : local.postgresql_administrator_login
      namespace : var.namespace
    })
  ]
}

resource "kubernetes_persistent_volume_claim" "app_pvc" {
  depends_on = [helm_release.temporal]
  metadata {
    name      = "storage-${var.namespace}"
    namespace = var.namespace
  }

  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "100Gi"
      }
    }

    storage_class_name = "azureblob-nfs-premium"
  }
}

locals {
  appcdYAML = templatefile("${path.module}/values/appcd.yaml", {
    temporal_namespace : var.namespace
    appcd_secrets : concat([kubernetes_secret.appcd_secrets.metadata[0].name, kubernetes_secret.appcd_scm_secrets.metadata[0].name], var.additional_secrets)
    enable_ops : var.enable_ops
    domain : var.domain
    auth_enabled : var.appcd_authentication.type != "none"
    scm_github_auth_url : try(var.scm_configuration.github_config.auth_url, "")
    scm_github_token_url : try(var.scm_configuration.github_config.token_url, "")
    scm_gitlab_auth_url : try(var.scm_configuration.gitlab_config.auth_url, "")
    scm_gitlab_token_url : try(var.scm_configuration.gitlab_config.token_url, "")
    scm_azure_auth_url : try(var.scm_configuration.azuredev_config.auth_url, "")
    scm_azure_token_url : try(var.scm_configuration.azuredev_config.token_url, "")
    enable_feature : var.enable_feature
    appcd_admin_emails : var.admin_emails
  })
}

resource "helm_release" "appcd" {
  depends_on = [helm_release.nginx_ingress]
  name       = "appcd"
  chart      = "appcd-dist-${var.appcd_version}.tgz"
  namespace  = var.namespace
  wait       = true
  values = [
    local.appcdYAML,
    templatefile("${path.module}/values/images.yaml", {})
  ]
}

output "appcd_yaml" {
  value = local.appcdYAML
}

resource "local_file" "appcd_yaml" {
  content  = local.appcdYAML
  filename = "${path.module}/values/appcd-final.yaml"
}

# get public IP of the nginx ingress
data "kubernetes_service" "nginx_ingress" {
  depends_on = [helm_release.nginx_ingress]
  metadata {
    name      = "nginx-ingress-controller"
    namespace = var.namespace
  }
}

locals {
  public_ip = data.kubernetes_service.nginx_ingress.status[0].load_balancer[0].ingress[0].ip
}
