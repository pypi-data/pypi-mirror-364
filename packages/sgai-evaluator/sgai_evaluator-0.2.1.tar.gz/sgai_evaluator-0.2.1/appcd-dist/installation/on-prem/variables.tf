variable "STACKGEN_PAT" {
  description = "token shared by stackgen team to download the stackgen binaries"
  type        = string
}

variable "appcd_version" {
  description = "The version of the appcd to deploy"
  type        = string
  default     = "0.9.2"
}

variable "domain" {
  description = "The domain for the appcd without the protocol"
  type        = string
}

variable "instance_type" {
  description = "The instance type for the EKS cluster"
  type        = string
  default     = "m7g.2xlarge"
}

variable "max_instances" {
  description = "The maximum number of instances for the EKS cluster"
  type        = number
  default     = 2
}


variable "suffix" {
  description = "Suffix of the EKS cluster"
  type        = string
}

variable "tags" {
  description = "The tags for the EKS cluster"
  type        = map(string)
  default     = {}
}

variable "region" {
  description = "The region for the EKS cluster"
  type        = string
  default     = "us-west-2"
}

variable "load-balancer-ssl-cert-arn" {
  description = "The ARN of the SSL certificate for the load balancer. Required if creating cluster and ingress"
  type        = string
  default     = ""
}

variable "namespace" {
  description = "The namespace for the appcd"
  type        = string
  default     = "appcd"
}

variable "additional_secrets" {
  description = "Additional secrets that are to be injected to the appcd installation. This can be handy if you are configuring auth and SCM configurations"
  type        = list(string)
  default     = []
}

variable "enable_ops" {
  description = "Enable ops"
  type        = bool
  default     = true
}

variable "db_instance_class" {
  description = "Instance class for the RDS database"
  type        = string
  default     = "db.t4g.medium"
}

variable "lb_cidr_blocks" {
  description = "The CIDR blocks for the load balancer"
  type        = list(string)
  default     = []
}

variable "scm_configuration" {
  description = "The SCM configuration for the appcd"
  type = object({
    scm_type = string # could be none, github, gitlab, azuredev
    github_config = optional(object({
      client_id     = string
      client_secret = string
      auth_url      = optional(string, "https://github.com/login/oauth/authorize")
      token_url     = optional(string, "https://github.com/login/oauth/access_token")
    }))
    gitlab_config = optional(object({
      client_id     = string
      client_secret = string,
      auth_url      = optional(string, "https://gitlab.com/oauth/authorize")
      token_url     = optional(string, "https://gitlab.com/oauth/token")
    }))
    azuredev_config = optional(object({
      client_id     = string
      client_secret = string
      auth_url      = optional(string, "https://app.vssps.visualstudio.com/oauth2/authorize")
      token_url     = optional(string, "https://app.vssps.visualstudio.com/oauth2/token")
    }))
  })
  default = {
    scm_type = "none"
    github_config = {
      client_id     = ""
      client_secret = ""
    }
    gitlab_config = {
      client_id     = ""
      client_secret = ""
    }
    azuredev_config = {
      client_id     = ""
      client_secret = ""
    }
  }
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

variable "admin_emails" {
  description = "The emails of the admin user"
  type        = list(string)
  default     = []
}

variable "enable_feature" {
  description = "stackgen features to enable"
  type = object({
    exporter          = optional(bool, true)
    llm               = optional(bool, false)
    vault             = optional(bool, true)
    enable_group_sync = optional(bool, false)
    artifacts_support = optional(bool, false)
    need_user_vetting = optional(bool, false)
    editableIac       = optional(bool, false)
    moduleEditor      = optional(bool, false)
    log_analysis      = optional(bool, false)
    integrations      = optional(bool, false)
    backstage_adapter = optional(bool, false)
  })
  default = {
    exporter          = true
    vault             = true
    llm               = false
    enable_group_sync = false
    artifacts_support = false
    need_user_vetting = false
    log_analysis      = false
    integrations      = false
    backstage_adapter = false
  }
}

variable "devops_ips" {
  description = "The IPs of the devops team"
  type        = list(string)
  default     = []
}

variable "use_spot_instances" {
  description = "Whether to use spot instances for the main workers nodes in the cluster"
  type        = bool
  default     = false
}

variable "ops_user" {
  description = "Create an ops user for the stackgen, this will be responsible for the appcd upgrade operations"
  type = object({
    enable = bool
    oidc_provider = optional(object({
      client_id_list  = optional(string, "")
      thumbprint_list = optional(string, "")
      url             = optional(string, "")
    }))
    assume_role_policy = optional(object({
      test     = optional(string, "StringLike")
      variable = optional(string, "")
      values   = optional(list(string), [])
    }))
  })
  default = {
    enable = false
  }
}

variable "alert_email" {
  description = "Email for alerts"
  default     = "alerts-prod-ops-aaaamju5k3vxefjpxt2u5sllwy@stackgen.slack.com"
}

variable "nginx_config" {
  type = object({
    client_max_body_size = string
  })
  default = {
    client_max_body_size = "10M"
  }
}
