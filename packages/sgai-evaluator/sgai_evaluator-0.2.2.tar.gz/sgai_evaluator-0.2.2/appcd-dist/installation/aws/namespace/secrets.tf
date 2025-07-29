locals {
  secretStoreName = "${var.namespace}-secret-store"
}

resource "kubernetes_manifest" "secret_store" {
  count = var.secret_management.skip_external_secrets ? 0 : 1
  depends_on = [
    kubernetes_namespace.appcd,
  ]
  manifest = {
    "apiVersion" = "external-secrets.io/v1beta1"
    "kind"       = "SecretStore"
    "metadata" = {
      "name"      = local.secretStoreName
      "namespace" = local.namespace
    }
    spec = {
      "provider" = {
        "aws" = {
          "service" = "SecretsManager"
          "region"  = var.region
        }
      }
    }
  }
}

resource "kubernetes_secret" "appcd-secrets" {
  count = var.secret_management.skip_external_secrets ? 1 : 0
  depends_on = [
    module.aurora_cluster
  ]
  metadata {
    name      = "appcd-secrets"
    namespace = local.namespace
  }
  data = {
    rds_endpoint                      = module.aurora_cluster.cluster_endpoint
    rds_port                          = module.aurora_cluster.cluster_port
    rds_read_endpoint                 = module.aurora_cluster.cluster_reader_endpoint
    rds_username                      = module.aurora_cluster.cluster_master_username
    rds_password                      = local.rds_password
    email_username                    = ""
    MAIL_PASSWORD                     = ""
    email_host                        = ""
    email_troubleshooting_sender_mail = ""
  }
}


resource "kubernetes_manifest" "secrets_for_pods" {
  count = var.secret_management.skip_external_secrets ? 0 : 1
  depends_on = [
    kubernetes_manifest.secret_store,
    module.aurora_cluster
  ]
  manifest = {
    kind       = "ExternalSecret"
    apiVersion = "external-secrets.io/v1beta1"
    metadata = {
      name      = "appcd-secrets"
      namespace = local.namespace
    }
    spec = {
      refreshInterval = "5m"
      secretStoreRef = {
        name = local.secretStoreName
        kind = "SecretStore"
      }
      data = [
        {
          secretKey = "rds_endpoint"
          remoteRef = {
            key = aws_secretsmanager_secret.rds_endpoint.name
          }
        },
        {
          secretKey = "rds_port"
          remoteRef = {
            key = aws_secretsmanager_secret.rds_port.name
          }
        },
        {
          secretKey = "rds_username"
          remoteRef = {
            key      = tostring(try(module.aurora_cluster.cluster_master_user_secret[0].secret_arn, ""))
            property = "username"
          }
        },
        {
          secretKey = "rds_password"
          remoteRef = {
            key      = tostring(try(module.aurora_cluster.cluster_master_user_secret[0].secret_arn, ""))
            property = "password"
          }
        },
        {
          secretKey = "email_username"
          remoteRef = {
            key      = local.ses_secret_key
            property = "username"
          }
        },
        {
          secretKey = "MAIL_PASSWORD"
          remoteRef = {
            key      = local.ses_secret_key
            property = "password"
          }
        },
        {
          secretKey = "email_host"
          remoteRef = {
            key      = local.ses_secret_key
            property = "host"
          }
        },
        {
          secretKey = "email_troubleshooting_sender_mail"
          remoteRef = {
            key      = local.ses_secret_key
            property = "troubleshooting_sender_mail"
          }
        },
        {
          secretKey = "rds_read_endpoint"
          remoteRef = {
            key = aws_secretsmanager_secret.rds_read_endpoint.name
          }
        }
      ]
    }
  }
}

resource "kubernetes_secret" "langfuse_agent_secrets" {
  metadata {
    name      = "langfuse-agent-secrets"
    namespace = "ai-observability"
  }

  data = {
    LANGFUSE_HOST       = base64encode("https://observe.dev.stackgen.com")
    LANGFUSE_PUBLIC_KEY = var.langfuse_public_key
    LANGFUSE_SECRET_KEY = var.langfuse_secret_key
  }

  type = "Opaque"
}

variable "langfuse_public_key" {
  description = "Langfuse public key for agent authentication (set via TF_VAR_langfuse_public_key environment variable)"
  type        = string
  sensitive   = true
  default     = "pk-lf-bcf7bc18-7dfa-4949-be75-502527cbca65"
}

variable "langfuse_secret_key" {
  description = "Langfuse secret key for agent authentication (set via TF_VAR_langfuse_secret_key environment variable)"
  type        = string
  sensitive   = true
  default     = "sk-lf-375ac1b4-c84f-423f-bea7-7d934eeae6bb"
}
