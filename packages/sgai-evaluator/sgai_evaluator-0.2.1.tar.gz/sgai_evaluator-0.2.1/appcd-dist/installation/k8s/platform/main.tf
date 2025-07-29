locals {
  unleash_chart_version = "5.5.0"
  tags = merge(var.tags, {
    "created_by" = "platform"
  })
  unleash_db_name = "unleash"
}

# get caller identity
data "aws_caller_identity" "current" {}
terraform {
  backend "s3" {
  }
}


terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.33.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}


resource "kubernetes_namespace" "this" {
  metadata {
    name = "platform"
  }
}

resource "random_password" "postgres" {
  length           = 16
  special          = true
  override_special = "!#$&*()-=+[]{}<>:?"
}

resource "aws_security_group" "platform_rds_sg" {
  name        = "platform-rds-sg"
  description = "Allow connection from security group"
  vpc_id      = var.vpc_id
  tags_all    = local.tags
  tags        = local.tags
}

# postgres rds instance
resource "aws_db_instance" "postgres" {
  allocated_storage         = 20
  storage_type              = "gp3"
  identifier                = "platform-db"
  engine                    = "postgres"
  engine_version            = "14.13"
  storage_encrypted         = true
  instance_class            = "db.t3.micro"
  username                  = local.unleash_db_name
  password                  = random_password.postgres.result
  backup_retention_period   = 5
  final_snapshot_identifier = "unleash-final-snapshot"
  vpc_security_group_ids    = [aws_security_group.platform_rds_sg.id]
  db_subnet_group_name      = var.db_subnet_group_name
  tags                      = local.tags
  deletion_protection       = true
  multi_az                  = true
}

# allow for allow_connection_from_sg to connect to the RDS instance
resource "aws_security_group_rule" "allow_connection_from_sg" {
  type                     = "ingress"
  description              = "Allow for pods in the same VPC to connect to the RDS instance"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.platform_rds_sg.id
  source_security_group_id = var.allow_connection_from_sg
}

locals {
  unleash_helm_values = {
    resources = {
      requests = {
        cpu    = "100m"
        memory = "100Mi"
      }
      limits = {
        cpu    = "200m"
        memory = "512Mi"
      }
    }
    ingress = {
      enabled   = var.domain_host != ""
      className = "nginx"
      hosts = [
        {
          host = var.domain_host
          paths = [
            {
              path     = "/"
              pathType = "ImplementationSpecific"
            }
          ]
        }
      ]
    }
    dbConfig = {
      database = "unleash"
      host     = aws_db_instance.postgres.address
      pass     = random_password.postgres.result
      port     = aws_db_instance.postgres.port
      user     = aws_db_instance.postgres.username
    }
    env = [
      {
        name  = "GOOGLE_CLIENT_ID"
        value = var.google_auth.client_id
      },
      {
        name  = "GOOGLE_CLIENT_SECRET"
        value = var.google_auth.client_secret
      },
      {
        name  = "GOOGLE_CALLBACK_URL"
        value = var.google_auth.callback_url
      },
      {
        name  = "CHECK_VERSION",
        value = "false"
      },
      {
        name  = "SEND_TELEMETRY",
        value = "false"
      }
    ]
  }
}

# create a k8s configmap with index.js and google-auth-hook.js
resource "kubernetes_config_map" "unleash_config" {
  metadata {
    name      = "unleash-config"
    namespace = kubernetes_namespace.this.metadata.0.name
  }

  data = {
    "index_js"            = file("${path.module}/featureflag/config/index.js")
    "google_auth_hook_js" = file("${path.module}/featureflag/config/google-auth-hook.js")
  }
}


# create a k8s job to create the database
resource "kubernetes_job" "create_db" {
  depends_on = [kubernetes_namespace.this]
  metadata {
    name      = "create-db"
    namespace = kubernetes_namespace.this.metadata.0.name
  }

  spec {
    ttl_seconds_after_finished = 10
    template {
      metadata {
        name = "create-db"
        labels = {
          app = "create-db"
        }
      }

      spec {
        container {
          name    = "create-db"
          image   = "ghcr.io/appcd-dev/bitnami/postgresql:17"
          command = ["sh", "-c"]
          args = [
            "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '${local.unleash_db_name}'\" | grep -q 1 || psql -c \"CREATE DATABASE ${local.unleash_db_name}\""
          ]
          env {
            name  = "PGPASSWORD"
            value = random_password.postgres.result
          }
          env {
            name  = "PGDATABASE"
            value = "postgres"
          }
          env {
            name  = "PGUSER"
            value = aws_db_instance.postgres.username
          }
          env {
            name  = "PGHOST"
            value = aws_db_instance.postgres.address
          }
          env {
            name  = "PGPORT"
            value = aws_db_instance.postgres.port
          }
        }
        restart_policy = "Never"
      }
    }
  }
  provisioner "local-exec" {
    command = "kubectl wait --namespace=${kubernetes_namespace.this.metadata[0].name} --for=condition=complete job/create-db"
  }
}

resource "helm_release" "unleash" {
  depends_on = [
    kubernetes_job.create_db,
    kubernetes_config_map.unleash_config
  ]
  name            = "unleash"
  chart           = "unleash"
  repository      = "https://docs.getunleash.io/helm-charts"
  version         = local.unleash_chart_version
  namespace       = kubernetes_namespace.this.metadata.0.name
  cleanup_on_fail = true
  wait            = true

  values = [
    "${file("${path.module}/values/unleash.yaml")}",
    yamlencode(local.unleash_helm_values)
  ]
}
