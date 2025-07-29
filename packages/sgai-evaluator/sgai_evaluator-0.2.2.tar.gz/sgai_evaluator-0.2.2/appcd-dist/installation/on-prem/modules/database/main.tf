resource "kubernetes_job" "db-creator" {
  for_each = toset(var.databases)
  metadata {
    name      = "${each.key}-db-creator"
    namespace = var.namespace
  }

  spec {
    ttl_seconds_after_finished = 10
    template {
      metadata {
        name = "${each.key}-db-creator"
        labels = {
          "created-for" = "appcd"
        }
      }
      spec {
        termination_grace_period_seconds = 10
        restart_policy                   = "Never"
        container {
          image   = "ghcr.io/appcd-dev/bitnami/postgresql:17"
          name    = "${each.key}-db-creator"
          command = ["sh", "-c"]
          args = [
            "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '${each.key}'\" | grep -q 1 || psql -c \"CREATE DATABASE ${each.key}\""
          ]
          env {
            name  = "PGDATABASE"
            value = "postgres"
          }
          env {
            name = "PGUSER"
            value_from {
              secret_key_ref {
                key  = var.pg_user
                name = var.secrets_from
              }
            }
          }
          env {
            name = "PGHOST"
            value_from {
              secret_key_ref {
                key  = var.rds_endpoint
                name = var.secrets_from
              }
            }
          }
          env {
            name = "PGPASSWORD"
            value_from {
              secret_key_ref {
                key  = var.rds_password
                name = var.secrets_from
              }
            }
          }
          env {
            name = "PGPORT"
            value_from {
              secret_key_ref {
                key  = var.pg_port
                name = var.secrets_from
              }
            }
          }
          env_from {
            secret_ref {
              name = var.secrets_from
            }
          }
        }
      }
    }
  }

  provisioner "local-exec" {
    command = "kubectl wait --namespace=${var.namespace} --for=condition=complete job/${var.databases[0]}-db-creator"
  }
}
