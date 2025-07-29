output "temporal_namespace" {
  value = local.temporal_namespace
}

output "appcd_secrets" {
  value = kubernetes_secret.appcd_secrets.metadata[0].name
}

output "rds_instances" {
  description = "Set of RDS instance identifiers created by the module."
  value       = toset([module.db.db_instance_identifier])
}
