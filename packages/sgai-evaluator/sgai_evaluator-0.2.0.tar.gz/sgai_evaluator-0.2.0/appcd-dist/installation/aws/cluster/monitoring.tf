# create kms  key
data "aws_instances" "eks_nodes" {
  filter {
    name   = "tag:aws:eks:cluster-name"
    values = [module.eks.cluster_name]
  }
}

resource "aws_kms_key" "infra" {
  description             = "${var.suffix}-KMS key for infra"
  deletion_window_in_days = 10
  rotation_period_in_days = 180
  enable_key_rotation     = true
  tags = merge(local.tags, {
    "name"    = "infra"
    "cluster" = var.suffix
  })
}
# create sns topic for alerts
resource "aws_sns_topic" "alerts" {
  name              = "${var.suffix}-infra-alerts"
  kms_master_key_id = aws_kms_key.infra.key_id
  tags = merge(local.tags, {
    "name"    = "infra-alerts"
    "cluster" = var.suffix
  })
}

# send email to the alert email
resource "aws_sns_topic_subscription" "alerts_subscription" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}


# Create CPU utilization alarms for each RDS instance
module "monitoring" {
  source               = "../monitoring"
  rds_instances        = [for instance in module.temporal_db.cluster_instances : instance.id]
  alerts_sns_topic_arn = aws_sns_topic.alerts.arn
  tags = merge(local.tags, {
    "name"    = "monitoring"
    "cluster" = var.suffix
  })
}

# Define CloudWatch Alarms for SQS Monitoring
resource "aws_cloudwatch_metric_alarm" "karpenter_sqs_message_age" {
  alarm_name          = "${module.eks.cluster_name}-karpenter-sqs-message-age"
  alarm_description   = "Alert when messages in the Karpenter SQS queue are not processed in time."
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 600 # Alerts if messages are unprocessed for 10+ minutes
  alarm_actions       = [aws_sns_topic.alerts.arn]
  dimensions = {
    QueueName = module.eks_blueprints_addons.gitops_metadata["karpenter_sqs_queue_name"]
  }
  treat_missing_data = "notBreaching"
  tags = merge(local.tags, {
    "name"    = "karpenter-sqs-age-alarm"
    "cluster" = var.suffix
  })
}
