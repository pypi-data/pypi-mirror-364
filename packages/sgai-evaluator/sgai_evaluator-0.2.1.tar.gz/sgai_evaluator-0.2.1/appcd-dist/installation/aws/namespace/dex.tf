locals {
  ssm_secret_name = "/${local.namespace}/dex-secret"
}

module "dex_database" {
  depends_on   = [module.aurora_cluster]
  source       = "../database"
  databases    = ["dex"]
  namespace    = local.namespace
  pg_port      = "rds_port"
  pg_user      = "rds_username"
  rds_endpoint = "rds_endpoint"
  rds_password = "rds_password"
  secrets_from = local.should_skip_external_secrets ? kubernetes_secret.appcd-secrets[0].metadata[0].name : kubernetes_manifest.secrets_for_pods[0].manifest.metadata.name
}

resource "kubernetes_secret" "dex_secret" {
  count = local.should_skip_external_secrets ? 1 : 0

  depends_on = [
    module.dex_database
  ]
  metadata {
    name      = "dex-secret"
    namespace = local.namespace
  }
  data = jsondecode(data.aws_secretsmanager_secret_version.env_secrets_version.secret_string)
}

resource "kubernetes_manifest" "dex_connectors" {
  count = local.should_skip_external_secrets ? 0 : 1

  field_manager {
    force_conflicts = true
  }
  depends_on = [data.aws_secretsmanager_secret_version.env_secrets_version]
  # update everytime the data changes
  manifest = {
    kind       = "ExternalSecret"
    apiVersion = "external-secrets.io/v1beta1"
    metadata = {
      name      = "dex-secret"
      namespace = local.namespace
    }
    spec = {
      refreshInterval = "1h"
      secretStoreRef = {
        name = local.secretStoreName
        kind = "SecretStore"
      }
      target = {
        name           = "dex-secret"
        creationPolicy = "Owner"
      }

      dataFrom = [
        {
          extract = {
            key              = data.aws_secretsmanager_secret.env_secrets.id
            decodingStrategy = "Auto"
          }
        }
      ]
    }
  }
}

data "aws_secretsmanager_secret" "env_secrets" {
  name = local.ssm_secret_name
}

data "aws_secretsmanager_secret_version" "env_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.env_secrets.id
}


resource "kubernetes_config_map" "dex_configmap" {
  metadata {
    name      = "dex-configmap"
    namespace = local.namespace
  }
  data = {
    stylecss : templatefile("${path.module}/values/dex/style.css", {})
    header : templatefile("${path.module}/values/dex/header.html", {})
    footer : templatefile("${path.module}/values/dex/footer.html", {})
    login : templatefile("${path.module}/values/dex/login.html", {})
  }
}


# random password for local connector dex 
resource "random_password" "dex_local_connector_password" {
  count = var.auth_connectors.number_of_users

  length           = 16
  special          = true
  override_special = "!@#$%^&*()_+"
}

data "external" "dex_password_hash" {
  count = var.auth_connectors.number_of_users
  program = [
    "bash", "${path.module}/scripts/generate_htpasswd.sh",
    random_password.dex_local_connector_password[count.index].result
  ]
}

locals {
  create_local_password = var.auth_connectors.number_of_users > 0
  user_password_mapping = { for index, user in range(var.auth_connectors.number_of_users) : "${var.auth_connectors.local_connector_email}_${index + 1}" => data.external.dex_password_hash[index].result }
  local_users = local.create_local_password ? [for user, password in local.user_password_mapping : {
    email : "${user}@stackgen.com",
    hash : password.hash,
    username : user,
    userID : uuidv5("oid", user)
  }] : []
}

resource "helm_release" "dex" {
  depends_on = [
    kubernetes_manifest.dex_connectors,
    kubernetes_manifest.secrets_for_pods,
    module.dex_database
  ]
  name       = "dex"
  repository = "https://charts.dexidp.io"
  chart      = "dex"
  version    = "0.19.1"
  namespace  = local.namespace
  values = [
    templatefile("${path.module}/values/dex.yaml", {
      host_domain            = var.host_domain,
      is_dev                 = var.is_dev,
      auth_connectors        = var.auth_connectors
      auth_connectors_type   = var.auth_connectors.type,
      auth_connectors_name   = var.auth_connectors.name,
      local_users            = local.local_users,
      enable_local_connector = local.create_local_password,
      appcd_authentication_config = indent(8, yamlencode(merge({
        redirectURI : "https://${var.host_domain}/auth/callback"
      }, var.auth_connectors.config))),
    })
  ]
}

locals {
  user_password_output = [
    for index, user in range(var.auth_connectors.number_of_users) : "- ${var.auth_connectors.local_connector_email}_${index + 1}@stackgen.com / ${random_password.dex_local_connector_password[index].result}"
  ]

  notes_to_customer = local.create_local_password ? "For this environment, Local user are the following: \n\n${join("\n", local.user_password_output)}\n\n" : ""
}


output "connection_notes" {
  sensitive   = true
  value       = <<-EOT
    ${local.notes_to_customer}
    
    To access the product, visit: https://${var.host_domain}
EOT
  description = "Connection notes for Dex"

}
