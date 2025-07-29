variable "cluster_endpoint" {
  description = "The endpoint for the EKS Kubernetes API"
  type        = string
}

variable "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  type        = string
}

variable "oidc_provider_arn" {
  description = "The OIDC provider ARN for the EKS cluster"
  type        = string
}

variable "cluster_certificate_authority_data" {
  description = "The base64 encoded certificate data required to communicate with the cluster"
  type        = string
}

variable "cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}

variable "load-balancer-ssl-cert-arn" {
  description = "The ARN of the SSL certificate to use for the load balancer"
  type        = string
}

variable "enable_ops" {
  description = "Whether to enable metrics for the EKS cluster"
  type        = bool
}

variable "STACKGEN_PAT" {
  description = "token shared by stackgen team to download the stackgen binaries"
  type        = string
}

variable "namespace" {
  description = "The namespace for the EKS cluster"
  type        = string
}

variable "postgres_version" {
  description = "PostgreSQL version to use"
  type        = string
  default     = "16.4"
}

variable "db_instance_class" {
  description = "Instance class for the RDS database"
  type        = string
}

variable "database_subnets" {
  description = "The RDS subnet group"
  type        = list(string)
}

variable "database_security_group_id" {
  description = "The security group for the RDS database"
  type        = list(string)
}

variable "domain" {
  description = "The domain for the ingress"
  type        = string
}
variable "lb_cidr_blocks" {
  description = "The cidr blocks to allow for the load balancer"
  type        = list(string)
}

variable "appcd_authentication" {
  description = "The auth configuration for the appcd"
  type = object({
    type   = string
    config = any
  })
  default = {
    type   = "none"
    config = {}
  }
}

variable "volume_name" {
  description = "The name of the volume"
  type        = string
}

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

variable "alert_email" {
  description = "Email for alerts"
  default     = "alerts-prod-ops-aaaamju5k3vxefjpxt2u5sllwy@stackgen.slack.com"
}