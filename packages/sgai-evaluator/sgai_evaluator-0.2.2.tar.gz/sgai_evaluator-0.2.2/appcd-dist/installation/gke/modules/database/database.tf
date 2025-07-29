locals {
  pg_user_name = "stackgen-${var.suffix}"
  labels = merge(var.labels, {
    "module" : "database"
  })
  network_cidr_name = "${var.project_id}-cidr"
  read_replica_ip_configuration = {
    ipv4_enabled       = true
    ssl_mode           = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"
    private_network    = null
    allocated_ip_range = null
    authorized_networks = [
      {
        name  = local.network_cidr_name
        value = var.private_network
      },
    ]
  }

}


# Random password for PostgreSQL admin user
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "_%#-"
}

module "pg" {
  source  = "terraform-google-modules/sql-db/google//modules/postgresql"
  version = "~> 25.0"

  name                 = "stackgen-pg-${var.suffix}"
  random_instance_name = true
  project_id           = var.project_id
  database_version     = "POSTGRES_17"
  region               = var.region

  // Master configurations
  tier                            = var.machine_type
  availability_type               = "REGIONAL"
  zone                            = var.zones[0]
  maintenance_window_day          = 7
  maintenance_window_hour         = 12
  maintenance_window_update_track = "stable"

  deletion_protection         = true
  deletion_protection_enabled = true

  database_flags = [{ name = "autovacuum", value = "off" }]

  user_labels = {
    maintainer = "stackgen"
  }

  ip_configuration = {
    ipv4_enabled        = false
    require_ssl         = true
    private_network     = var.private_network
    allocated_ip_range  = null
    authorized_networks = []
  }

  backup_configuration = {
    enabled                        = true
    start_time                     = "20:55"
    point_in_time_recovery_enabled = false
    transaction_log_retention_days = null
    retained_backups               = 365
    retention_unit                 = "COUNT"
  }

  // Read replica configurations
  read_replica_name_suffix = "-test-ha"
  read_replicas = [
    {
      name              = "0"
      availability_type = "REGIONAL"
      tier              = var.machine_type
      ip_configuration  = local.read_replica_ip_configuration
      database_flags    = [{ name = "autovacuum", value = "off" }]
      zone              = var.zones[0]
      secondary_zone    = length(var.zones) > 1 ? var.zones[1] : null
      disk_autoresize   = null
      ip_configuration = {
        ipv4_enabled        = false
        ssl_mode            = "ALLOW_UNENCRYPTED_AND_ENCRYPTED"
        private_network     = var.private_network
        allocated_ip_range  = null
        authorized_networks = []
      }
      disk_autoresize_limit = null
      disk_size             = null
      user_labels = {
        maintainer = "stackgen"
      }
      encryption_key_name = null
    },
  ]

  db_name      = "stackgen"
  db_charset   = "UTF8"
  db_collation = "en_US.UTF8"

  additional_databases = [
    {
      name      = "temporal"
      charset   = "UTF8"
      collation = "en_US.UTF8"
    },
    {
      name    = "temporalvisibility"
      charset = "UTF8"

      collation = "en_US.UTF8"
    },
  ]

  user_name     = local.pg_user_name
  user_password = random_password.db_password.result
}
