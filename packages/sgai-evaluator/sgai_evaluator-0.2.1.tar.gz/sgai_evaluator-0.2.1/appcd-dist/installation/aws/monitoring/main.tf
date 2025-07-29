locals {
  rds_instances = toset(var.rds_instances)
  tags = merge(
    var.tags, {
      "repo" = "https://github.com/appcd-dev/appcd-dist"
      "path" = "installation/aws/monitoring"
  })
}

resource "aws_cloudwatch_metric_alarm" "cpu_utilization_alarms" {
  for_each            = local.rds_instances
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
  for_each            = local.rds_instances
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
  for_each            = local.rds_instances
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
  for_each            = local.rds_instances
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

