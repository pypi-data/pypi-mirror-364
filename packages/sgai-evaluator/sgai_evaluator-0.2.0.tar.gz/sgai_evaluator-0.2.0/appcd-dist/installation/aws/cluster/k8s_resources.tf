provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      # This requires the awscli to be installed locally where Terraform is executed
      args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

variable "temporal_version" {
  description = "The version of Temporal to deploy"
  default     = "0.33.0"
}

variable "skater_release" {
  description = "The version of Stakater to deploy"
  default     = "v1.0.67"
}

resource "helm_release" "reloader" {
  name       = "reloader"
  namespace  = "kube-system"
  repository = "https://stakater.github.io/stakater-charts"
  chart      = "reloader"
  version    = var.skater_release
}

variable "loki_stack_chart_version" {
  description = "The version of Loki Stack to deploy"
  default     = "2.10.2"
}

resource "helm_release" "loki" {
  name             = "loki"
  namespace        = "loki-stack"
  repository       = "https://grafana.github.io/helm-charts"
  create_namespace = true

  chart   = "loki-stack"
  version = var.loki_stack_chart_version
  values = [
    file("./values/loki.yaml")
  ]
}

resource "helm_release" "temporal" {
  namespace = local.temporal_namespace
  name      = "temporal"
  chart     = "https://github.com/temporalio/helm-charts/releases/download/temporal-${var.temporal_version}/temporal-${var.temporal_version}.tgz"
  values = [
    templatefile("./values/temporal.tfpl", {
      temporal-default-store-secret = kubernetes_manifest.temporal-default-store.manifest.metadata.name,
      temporal-visibility-secret    = kubernetes_manifest.temporal-visibility-store.manifest.metadata.name,
      temporal-sql-host             = module.temporal_db.cluster_endpoint
      temporal-sql-port             = module.temporal_db.cluster_port,
      temporal-sql-user             = module.temporal_db.cluster_master_username
    })
  ]
}
resource "kubernetes_namespace" "temporal" {
  depends_on = [module.eks_blueprints_addons]
  metadata {
    name = local.temporal_namespace
  }
}

resource "kubernetes_manifest" "secret_store" {
  depends_on = [
    module.eks_blueprints_addons,
    kubernetes_namespace.temporal,
    aws_iam_role_policy_attachment.rds_secrets_role_policy_attachment,
  ]
  manifest = {
    "apiVersion" = "external-secrets.io/v1beta1"
    "kind"       = "SecretStore"
    "metadata" = {
      "name"      = local.secretStoreName
      "namespace" = local.temporal_namespace
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

resource "kubernetes_manifest" "temporal-default-store" {
  depends_on = [
    kubernetes_manifest.secret_store,
    module.temporal_db,
  ]
  manifest = {
    kind       = "ExternalSecret"
    apiVersion = "external-secrets.io/v1beta1"
    metadata = {
      name      = "temporal-default-store"
      namespace = local.temporal_namespace
    }
    spec = {
      refreshInterval = "5m"
      secretStoreRef = {
        name = local.secretStoreName
        kind = "SecretStore"
      }
      data = [
        {
          secretKey = "password"
          remoteRef = {
            key      = tostring(try(module.temporal_db.cluster_master_user_secret[0].secret_arn, "not this"))
            property = "password"
          }
        }
      ]
    }
  }
}


resource "kubernetes_manifest" "temporal-visibility-store" {
  field_manager {
    force_conflicts = true
  }
  depends_on = [
    kubernetes_manifest.secret_store,
    module.temporal_db,
  ]
  manifest = {
    kind       = "ExternalSecret"
    apiVersion = "external-secrets.io/v1beta1"
    metadata = {
      name      = "temporal-visibility-store"
      namespace = local.temporal_namespace
    }
    spec = {
      refreshInterval = "1h"
      secretStoreRef = {
        name = local.secretStoreName
        kind = "SecretStore"
      }
      data = [
        {
          secretKey = "password"
          remoteRef = {
            key      = tostring(try(module.temporal_db.cluster_master_user_secret[0].secret_arn, "not this"))
            property = "password"
          }
        },
        {
          secretKey = "rds_password"
          remoteRef = {
            key      = tostring(try(module.temporal_db.cluster_master_user_secret[0].secret_arn, "not this"))
            property = "password"
          }
        },
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
            key      = tostring(try(module.temporal_db.cluster_master_user_secret[0].secret_arn, "not this"))
            property = "username"
          }
        },
      ]
    }
  }
}

module "temporal_database" {
  depends_on   = [kubernetes_manifest.temporal-visibility-store]
  source       = "../database"
  databases    = local.databases
  namespace    = local.temporal_namespace
  pg_port      = "rds_port"
  pg_user      = "rds_username"
  rds_endpoint = "rds_endpoint"
  rds_password = "rds_password"
  secrets_from = kubernetes_manifest.temporal-visibility-store.manifest.metadata.name
}

// create s3 bucket
resource "aws_s3_bucket" "csi-backend" {
  bucket = "appcd-blobs-${var.suffix}"
  tags   = local.tags
}

// add a lifecycle rule to expire objects after 45 days
resource "aws_s3_bucket_lifecycle_configuration" "csi-backend" {
  bucket = aws_s3_bucket.csi-backend.id

  rule {
    id = "expire"

    filter {
      prefix = "" # Empty prefix means apply to all objects
    }

    expiration {
      days = 45
    }

    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
}

// remove public acccess to the bucket
resource "aws_s3_bucket_public_access_block" "csi-backend" {
  bucket = aws_s3_bucket.csi-backend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


module "s3-csi-driver" {
  source = "github.com/appcd-dev/terraform-aws-s3-csi-driver?ref=83640d82cf0dfdd4e73b012b48cad9e884ff5b34"

  aws_region    = var.region
  bucket_name   = aws_s3_bucket.csi-backend.id
  iam_role_name = var.suffix
  eks_cluster   = module.eks.cluster_name
  tags          = local.tags
}


resource "kubernetes_storage_class" "s3_csi" {
  depends_on             = [module.s3-csi-driver]
  storage_provisioner    = "s3.csi.aws.com"
  allow_volume_expansion = true
  metadata {
    name = "s3-csi"
  }
}


// attach the policy to the role
resource "aws_iam_role_policy_attachment" "rds_secrets_role_policy_attachment" {
  role       = module.eks_blueprints_addons.external_secrets.iam_role_name
  policy_arn = aws_iam_policy.rds_secrets_policy.arn
}