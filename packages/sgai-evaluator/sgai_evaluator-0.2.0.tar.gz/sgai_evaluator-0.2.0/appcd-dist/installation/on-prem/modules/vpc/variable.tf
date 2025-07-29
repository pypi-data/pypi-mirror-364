variable "STACKGEN_PAT" {
  description = "token shared by stackgen team to download the stackgen binaries"
  type        = string
}

variable "region" {
  description = "The region for the EKS cluster"
  type        = string
}
variable "suffix" {
  description = "Suffix of the EKS cluster"
}

variable "tags" {
  description = "The tags for the EKS cluster"
  type        = map(string)
  default     = {}
}

variable "use_spot_instances" {
  description = "Whether to use spot instances for the EKS cluster"
  type        = bool
  default     = true
}

variable "max_instances" {
  description = "The maximum number of instances for the EKS cluster"
  type        = number
}

variable "instance_type" {
  description = "The instance type for the EKS cluster"
  type        = string
}

variable "autoscaling_average_cpu" {
  description = "The average CPU for autoscaling"
  type        = number
  default     = 70
}

variable "devops_ips" {
  description = "The IPs of the devops team"
  type        = list(string)
  default     = []
}

variable "ops_user" {
  description = "The user for ops"
  type = object({
    rolearn  = string
    username = string
  })
  default = {
    rolearn  = ""
    username = ""
  }
}


variable "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  type        = string
}
