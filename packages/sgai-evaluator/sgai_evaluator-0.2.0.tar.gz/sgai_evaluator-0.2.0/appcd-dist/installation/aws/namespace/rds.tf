locals {
  should_skip_external_secrets = var.secret_management.skip_external_secrets
  rds_password_rotation_days   = var.is_dev ? 90 : 30
  rds_password                 = local.should_skip_external_secrets ? random_password.rds_master_user_password[0].result : "this_password_is_not_used"
  vpc_id                       = var.existing_cluster.lookup ? data.aws_vpc.appcd_vpc[0].id : var.vpc_id
  eks_sg_id                    = var.existing_cluster.lookup ? data.aws_security_group.appcd_eks_sg[0].id : var.eks_sg_id
  db_subnet_group_name         = var.existing_cluster.lookup ? data.aws_db_subnet_group.database[0].name : var.database_subnet_group_name
}

# create a random password for the RDS master user
resource "random_password" "rds_master_user_password" {
  count            = local.should_skip_external_secrets ? 1 : 0
  length           = 16
  special          = true
  override_special = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
}

# data lookup vpc by tag
data "aws_vpc" "appcd_vpc" {
  count = var.existing_cluster.lookup ? 1 : 0
  tags = {
    created_for = var.existing_cluster.created_for
  }
}

data "aws_security_group" "appcd_eks_sg" {
  count = var.existing_cluster.lookup ? 1 : 0
  tags = {
    created_for = var.existing_cluster.created_for
    Name        = "${var.existing_cluster.created_for}-eks-node"
  }
}

data "aws_db_subnet_group" "database" {
  count = var.existing_cluster.lookup ? 1 : 0
  name  = "appcd-vpc-${var.existing_cluster.created_for}"
}


module "aurora_cluster" {
  source         = "terraform-aws-modules/rds-aurora/aws"
  version        = "9.11.0"
  name           = "appcd-rds-${var.namespace}"
  engine         = var.db_engine
  engine_version = var.db_engine_version
  engine_mode    = var.db_engine_mode
  instance_class = var.db_instance_class

  allow_major_version_upgrade = var.is_dev
  master_username             = "appcd_rds_admin"

  manage_master_user_password                            = local.should_skip_external_secrets ? false : true
  master_user_password_rotation_automatically_after_days = local.should_skip_external_secrets ? null : local.rds_password_rotation_days
  master_password                                        = local.should_skip_external_secrets ? local.rds_password : ""

  instances = {
    one = {}
  }

  performance_insights_enabled         = var.enable_rds_insights
  vpc_id                               = local.vpc_id
  final_snapshot_identifier            = "appcd-rds-${var.namespace}-final-snapshot"
  manage_master_user_password_rotation = local.should_skip_external_secrets ? false : true
  db_subnet_group_name                 = local.db_subnet_group_name
  availability_zones                   = var.azs
  security_group_rules = {
    ex1_ingress = {
      source_security_group_id = local.eks_sg_id
      description              = "Allow access from EKS security group"
      type                     = "ingress"
    }
  }

  storage_encrypted               = true
  apply_immediately               = true
  monitoring_interval             = 10
  enabled_cloudwatch_logs_exports = ["postgresql"]

  scaling_configuration = {
    auto_pause               = true
    max_capacity             = 2
    min_capacity             = 1
    seconds_until_auto_pause = 300
    timeout_action           = "ForceApplyCapacityChange"
  }

  serverlessv2_scaling_configuration = {
    max_capacity = 1.0
    min_capacity = 0.5
  }

  tags = local.tags
}

// store the endpoint
resource "aws_secretsmanager_secret" "rds_endpoint" {
  name = "/${local.namespace}/rds_endpoint"
  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "rds_endpoint" {
  secret_id     = aws_secretsmanager_secret.rds_endpoint.id
  secret_string = module.aurora_cluster.cluster_endpoint
}

// store the port
resource "aws_secretsmanager_secret" "rds_port" {
  name = "/${local.namespace}/rds_port"
  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "rds_port" {
  secret_id     = aws_secretsmanager_secret.rds_port.id
  secret_string = module.aurora_cluster.cluster_port
}

// store the database name
resource "aws_secretsmanager_secret" "rds_read_endpoint" {
  name = "/${local.namespace}/rds_read_endpoint"
  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "rds_read_endpoint" {
  secret_id     = aws_secretsmanager_secret.rds_read_endpoint.id
  secret_string = module.aurora_cluster.cluster_reader_endpoint
}


module "monitoring" {
  count                = length(module.aurora_cluster.cluster_instances) > 0 ? 1 : 0
  depends_on           = [module.aurora_cluster]
  source               = "../monitoring"
  rds_instances        = length(module.aurora_cluster.cluster_instances) > 0 ? [for instance in module.aurora_cluster.cluster_instances : instance.id] : []
  alerts_sns_topic_arn = var.alerts_sns_topic_arn
  tags                 = local.tags
}
