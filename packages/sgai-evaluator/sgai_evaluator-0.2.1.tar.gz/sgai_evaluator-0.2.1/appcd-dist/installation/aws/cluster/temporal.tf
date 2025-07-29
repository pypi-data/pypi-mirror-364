variable "temporal_db_instance_class" {
  type        = string
  description = "db_instance_class"
  default     = "db.t4g.medium"
}

locals {
  temporal_namespace = "temporal"
  secretStoreName    = "${var.suffix}-temporal-secret-store"
  databases          = ["temporal", "temporalvisibility"]
}


module "temporal_db" {
  source         = "terraform-aws-modules/rds-aurora/aws"
  version        = "9.10.0"
  name           = "temporal-rds-${var.suffix}"
  engine         = "aurora-postgresql"
  engine_version = "14.15"
  instance_class = var.temporal_db_instance_class

  master_username             = "temporal_admin"
  manage_master_user_password = true
  instances = {
    one = {}
    two = {
      #   instance_class = "db.r6g.2xlarge"
    }
  }

  performance_insights_enabled           = false
  cloudwatch_log_group_retention_in_days = 5
  vpc_id                                 = module.vpc.vpc_id
  final_snapshot_identifier              = "temporal-rds-${var.suffix}-final-snapshot"
  db_subnet_group_name                   = module.vpc.database_subnet_group_name
  availability_zones                     = module.vpc.azs
  security_group_rules = {
    ex1_ingress = {
      source_security_group_id = module.eks.node_security_group_id
    }
  }

  storage_encrypted               = true
  apply_immediately               = true
  monitoring_interval             = 10
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = local.tags
}


// store the endpoint
resource "aws_secretsmanager_secret" "rds_endpoint" {
  name = "/${var.suffix}/temporal_rds_endpoint"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "rds_endpoint" {
  secret_id     = aws_secretsmanager_secret.rds_endpoint.id
  secret_string = module.temporal_db.cluster_endpoint
}


// store the port
resource "aws_secretsmanager_secret" "rds_port" {
  name = "/${var.suffix}/temporal_rds_port"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "rds_port" {
  secret_id     = aws_secretsmanager_secret.rds_port.id
  secret_string = module.temporal_db.cluster_port
}

// store the database name
resource "aws_secretsmanager_secret" "rds_read_endpoint" {
  name = "/${var.suffix}/temporal_rds_read_endpoint"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "rds_read_endpoint" {
  secret_id     = aws_secretsmanager_secret.rds_read_endpoint.id
  secret_string = module.temporal_db.cluster_reader_endpoint
}

// add permisson to read the database secrets
resource "aws_iam_policy" "rds_secrets_policy" {
  name = "rds_secrets_policy_${var.suffix}"
  tags = local.tags
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "rdssecretspolicy",
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ],
        "Resource" : [
          aws_secretsmanager_secret.rds_endpoint.arn,
          aws_secretsmanager_secret.rds_port.arn,
          aws_secretsmanager_secret.rds_read_endpoint.arn,
          module.temporal_db.cluster_master_user_secret[0].secret_arn
        ]
      },
      {
        "Sid" : "secretForNamespaceRDS",
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ],
        "Resource" : [
          "arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current.account_id}:secret:*",
        ],
        # contains the tag repo:https://github.com/appcd-dev/appcd-dist
        "Condition" : {
          "StringEquals" : {
            "aws:ResourceTag/repo" : "https://github.com/appcd-dev/appcd-dist"
          }
        }
        # Also have a tag namespace:*
        "Condition" : {
          "StringEquals" : {
            "aws:ResourceTag/namespace" : "*"
          }
        }
      }
    ]
  })
}


output "temporal_keys" {
  sensitive = true
  value = yamlencode({
    driver          = "postgres"
    host            = module.temporal_db.cluster_endpoint
    port            = module.temporal_db.cluster_port
    database        = "temporal"
    user            = module.temporal_db.cluster_master_username
    existingSecret  = "temporal-default-store"
    maxConns        = 20
    maxConnLifetime = "1h"
    }
  )
}
