output "postgresql_administrator_password" {
  value       = random_password.db_password.result
  description = "The administrator password for the PostgreSQL instance."
}

output "postgresql_fqdn" {
  value       = module.pg.instance_first_ip_address
  description = "The fully qualified domain name (FQDN) of the PostgreSQL instance."
}

output "postgresql_administrator_login" {
  value       = local.pg_user_name
  description = "The administrator login username for the PostgreSQL instance."
}

output "postgresql_instance_name" {
  value       = module.pg.instance_name
  description = "The name of the PostgreSQL instance."
}

output "replicas" {
  value       = module.pg.replicas
  description = "The ID of the PostgreSQL instance."
}
