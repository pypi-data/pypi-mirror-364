
variable "alerts_sns_topic_arn" {
  type        = string
  description = "SNS topic ARN for alarm notifications"
}

variable "cpu_threshold" {
  default     = 80.0
  description = "CPU utilization threshold for the alarm"
}

variable "read_iops_threshold" {
  default     = 1000.0
  description = "Read IOPS threshold for the alarm"
}

variable "free_storage_threshold" {
  default     = 1000000000
  description = "Free Storage Space threshold for the alarm (in bytes)"
}

variable "free_local_storage_threshold" {
  default     = 1000.0
  description = "Free Local Storage threshold for the alarm (in MB)"
}

variable "rds_instances" {
  description = "List of RDS instance identifiers"
  type        = list(string)
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
}
