variable "tags" {
  description = "The tags for the EKS cluster"
  type        = map(string)
  default     = {}
}

// get user input
variable "region" {
  description = "AWS region"
}

variable "suffix" {
  description = "Suffix of the EKS cluster"
}

variable "load-balancer-ssl-cert-arn" {
  description = "ARN of the SSL certificate for the load balancer"
}

variable "use_spot_instances" {
  description = "Use spot"
  default     = true
}

variable "max_instances" {
  description = "Maximum number instances"
  default     = 3
}

variable "is_dev_cluster" {
  description = "Is this a dev cluster"
  default     = true
}

variable "instance_type" {
  description = "The instance type for the EKS cluster"
  type        = string
  default     = "m7g.xlarge"
}

variable "enable_gpu" {
  description = "Enable GPU"
  default     = false
}

variable "alert_email" {
  description = "Email for alerts"
}

variable "read_only_role_name" {
  description = "Name of the read-only IAM role"
  type        = string
}

variable "flow_log_retention_days" {
  description = "Retention period in days for VPC flow log CloudWatch log group"
  type        = number
  default     = 0
}
