module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.6.0"

  identifier = "${var.namespace}-${var.cluster_name}"


  engine                = "postgres"
  engine_version        = var.postgres_version
  instance_class        = var.db_instance_class
  allocated_storage     = 20
  max_allocated_storage = 200

  db_name                     = "postgres"
  username                    = local.db_username
  manage_master_user_password = false
  password                    = local.db_password
  port                        = "5432"

  storage_type                        = "gp3"
  iam_database_authentication_enabled = false
  multi_az                            = true

  maintenance_window               = "Mon:00:00-Mon:03:00"
  backup_retention_period          = 7
  backup_window                    = "03:00-06:00"
  final_snapshot_identifier_prefix = "${var.cluster_name}-${var.namespace}-db-final-snapshot"

  family = "postgres16"
  parameters = [
    {
      name  = "rds.force_ssl"
      value = 0
    },
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    }
  ]

  tags = merge(local.tags, {
    Name = "${var.namespace}-${var.cluster_name}-db"
  })

  # DB subnet group
  create_db_subnet_group = true
  subnet_ids             = var.database_subnets

  deletion_protection    = true
  vpc_security_group_ids = var.database_security_group_id
}

locals {
  databases = ["temporal", "temporalvisibility", "postgres", "dex"]
}

module "database" {
  depends_on   = [module.db, kubernetes_namespace.this]
  source       = "../database"
  databases    = local.databases
  namespace    = var.namespace
  pg_port      = "rds_port"
  pg_user      = "rds_username"
  rds_endpoint = "rds_host"
  rds_password = "rds_password"
  secrets_from = kubernetes_secret.appcd_secrets.metadata[0].name
}

resource "aws_db_instance" "read_replica" {
  count                   = 1
  identifier              = "${var.namespace}-${var.cluster_name}-replica-${count.index}"
  replicate_source_db     = module.db.db_instance_identifier
  instance_class          = var.db_instance_class
  storage_type            = "gp3"
  multi_az                = true
  storage_encrypted       = true
  vpc_security_group_ids  = var.database_security_group_id
  publicly_accessible     = false
  backup_retention_period = 7
  backup_window           = "03:00-06:00"
  maintenance_window      = "Mon:00:00-Mon:03:00"
  skip_final_snapshot     = true


  tags = merge(local.tags, {
    Name = "${var.namespace}-${var.cluster_name}-replica-${count.index}"
  })
}
