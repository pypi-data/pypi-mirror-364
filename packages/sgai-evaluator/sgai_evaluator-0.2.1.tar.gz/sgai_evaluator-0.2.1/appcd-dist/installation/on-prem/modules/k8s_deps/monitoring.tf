locals {
  rds_instances = toset(
    concat(
      [module.db.db_instance_identifier],        # Primary DB instance
      aws_db_instance.read_replica[*].identifier # Dynamically fetch all replica identifiers
    )
  )
}

resource "aws_cloudwatch_metric_alarm" "cpu_utilization_alarms" {
  for_each            = { for k in local.rds_instances : k => k if var.enable_ops }
  alarm_name          = "CPU_Utilization_Alarm_${each.key}"
  alarm_description   = "Alarm when CPU exceeds ${var.cpu_threshold}%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.cpu_threshold
  tags_all            = local.tags
  tags                = local.tags

  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_actions      = [var.alerts_sns_topic_arn]
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "read_iops_alarms" {
  for_each            = { for k in local.rds_instances : k => k if var.enable_ops }
  alarm_name          = "Read_IOPS_Alarm_${each.key}"
  alarm_description   = "Alarm when Read IOPS exceeds ${var.read_iops_threshold}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ReadIOPS"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.read_iops_threshold
  tags_all            = local.tags
  tags                = local.tags
  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_actions      = [var.alerts_sns_topic_arn]
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "free_storage_alarms" {
  for_each            = { for k in local.rds_instances : k => k if var.enable_ops }
  alarm_name          = "Free_Storage_Space_Alarm_${each.key}"
  alarm_description   = "Alarm when Free Storage Space is less than ${var.free_storage_threshold} bytes"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.free_storage_threshold
  tags_all            = local.tags
  tags                = local.tags
  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_actions      = [var.alerts_sns_topic_arn]
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "free_local_storage_alarms" {
  for_each            = { for k in local.rds_instances : k => k if var.enable_ops }
  alarm_name          = "Free_Local_Storage_Alarm_${each.key}"
  alarm_description   = "Alarm when Free Local Storage is less than ${var.free_local_storage_threshold} MB"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeLocalStorage"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.free_local_storage_threshold
  tags_all            = local.tags
  tags                = local.tags
  dimensions = {
    DBInstanceIdentifier = each.key
  }

  alarm_actions      = [var.alerts_sns_topic_arn]
  treat_missing_data = "notBreaching"
}


# Define CloudWatch Alarms for SQS Monitoring
resource "aws_cloudwatch_metric_alarm" "karpenter_sqs_message_age" {
  alarm_name          = "${var.cluster_name}-karpenter-sqs-message-age"
  alarm_description   = "Alert when messages in the Karpenter SQS queue are not processed in time."
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 600 # Alerts if messages are unprocessed for 10+ minutes
  alarm_actions       = [var.alerts_sns_topic_arn]
  dimensions = {
    QueueName = module.eks_blueprints_addons.gitops_metadata["karpenter_sqs_queue_name"]
  }
  treat_missing_data = "notBreaching"
}
