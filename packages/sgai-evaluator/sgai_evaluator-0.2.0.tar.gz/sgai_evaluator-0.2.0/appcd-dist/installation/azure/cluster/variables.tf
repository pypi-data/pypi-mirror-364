variable "tags" {
  description = "The tags for the AKS cluster"
  type        = map(string)
  default     = {}
}

variable "location" {
  type = string
}

variable "namespace" {
  description = "The namespace in AKS cluster where the appcd will be deployed"
  type        = string
  default     = "appcd"
}

variable "agents_size" {
  default     = "Standard_DS3_v2"
  description = "The default virtual machine size for the Kubernetes agents"
  type        = string
}

variable "kubernetes_version" {
  description = "Specify which Kubernetes release to use. The default used is the latest Kubernetes version available in the region"
  type        = string
  default     = "1.29"
}

variable "prefix" {
  description = "Prefix for Resource group and AKS cluster"
}

variable "STACKGEN_PAT" {
  description = "The GitHub Personal Access Token for the stackgen repository. (This is a sensitive entry)"
  type        = string
  sensitive   = true
}


variable "enable_ops" {
  description = "Enable the Ops portal"
  default     = false
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

variable "admin_emails" {
  description = "The email ids of the admin users"
  type        = list(string)
  default     = []
}

variable "alert_email_ids" {
  description = "The email ids to send the alerts to when appcd deployment is having issues"
  type        = list(string)
  default     = ["alert+azure@appcd.com"]
}


variable "additional_secrets" {
  description = "Additional secrets that are to be injected to the appcd installation. This can be handy if you are configuring auth and SCM configurations"
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

variable "enable_feature" {
  description = "stackgen features to enable"
  type = object({
    exporter = optional(bool, false)
    llm      = optional(bool, false)
  })
  default = {
    exporter = true
    llm      = false
  }
}
