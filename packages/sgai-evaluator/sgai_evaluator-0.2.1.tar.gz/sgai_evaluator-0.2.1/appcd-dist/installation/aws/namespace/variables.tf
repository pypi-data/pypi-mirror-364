variable "cluster_endpoint" {
  type        = string
  description = "(deprecated) k8s cluster_endpoint, Use existing_cluster.lookup instead"
  default     = ""
}

variable "cluster_certificate_authority_data" {
  type        = string
  description = "(deprecated) k8s cluster_certificate_authority_data, Use existing_cluster.lookup instead"
  default     = ""
}

variable "db_instance_class" {
  type        = string
  description = "db_instance_class"
  default     = "db.t4g.medium"
}

variable "db_engine_version" {
  type        = string
  description = "db_engine_version"
  default     = "14.15"
}

variable "cluster_name" {
  type        = string
  description = "(deprecated) k8s eks: cluster_name, Use existing_cluster.lookup instead"
  default     = ""
}

variable "namespace" {
  type        = string
  description = "suffix"
}

variable "host_domain" {
  type        = string
  description = "host domain"
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "region" {
  type        = string
  description = "value of aws region"
}

variable "eks_sg_id" {
  type        = string
  description = "(deprecated) eks security group id, Use existing_cluster.lookup instead"
  default     = ""
}

variable "database_subnet_group_name" {
  type        = string
  description = "(deprecated) database subnet, Use existing_cluster.lookup instead"
  default     = ""
}

variable "vpc_id" {
  description = "(deprecated) The VPC ID, Use existing_cluster.created_for lookup instead"
  type        = string
  default     = ""
}

variable "azs" {
  description = "vpc azs"
  type        = list(string)
}

variable "data_bucket_name" {
  description = "s3 bucket name"
  type        = string
}

variable "is_dev" {
  description = "mark this as a developer namespace"
  type        = bool
  default     = true
}

variable "enable_rds_insights" {
  description = "enable rds insights"
  type        = bool
  default     = true
}

variable "db_engine" {
  description = "db engine"
  type        = string
  default     = "aurora-postgresql"
}

variable "db_engine_mode" {
  description = "db engine mode"
  type        = string
  default     = "provisioned"
}

variable "enable_gpu" {
  description = "enable gpu"
  type        = bool
  default     = false
}

variable "auth_connectors" {
  description = "auth connectors"
  type = object({
    enable                = bool
    type                  = string
    config                = any
    name                  = string
    local_connector_email = optional(string, "workshop@stackgen.com")
    number_of_users       = optional(number, 0)
  })
  default = {
    enable                 = false
    type                   = "CHANGE_BASED_ON_CUSTOMER"
    config                 = {}
    name                   = "acme_corp"
    enable_local_connector = false
  }
}

variable "alerts_sns_topic_arn" {
  type        = string
  description = "SNS topic ARN for alarm notifications"
}


variable "secret_management" {
  description = "Skip the creation of external secrets"
  type = object({
    skip_external_secrets = bool
  })
  default = {
    skip_external_secrets = false
  }
}

variable "existing_cluster" {
  type = object({
    lookup      = bool
    created_for = string
  })
  default = {
    lookup      = false
    created_for = "FILL_THIS_IN_WITH_CUSTOMER_NAME"
  }
  description = "value of existing cluster and connections to it"
}
