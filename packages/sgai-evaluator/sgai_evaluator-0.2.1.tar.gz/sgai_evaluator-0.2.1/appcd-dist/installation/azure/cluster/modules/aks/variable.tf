variable "agents_size" {
  default     = "Standard_DS3_v2"
  description = "The default virtual machine size for the Kubernetes agents"
  type        = string
}

variable "resource_group" {
  description = "The name of the resource group"
  type        = string
}

variable "prefix" {
  description = "Prefix of the AKS cluster"
  default     = "appcd_cluster"
}

variable "location" {
  type    = string
  default = "westus2"
}

variable "tags" {
  description = "The tags for the AKS cluster"
  type        = map(string)
  default = {
    "module" = "appcd"
  }
}

variable "kubernetes_version" {
  description = "Specify which Kubernetes release to use. The default used is the latest Kubernetes version available in the region"
  type        = string
  default     = "1.29"
}


variable "postgres_sku_name" {
  description = "The SKU name for the PostgreSQL server"
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "postgres_size_in_mb" {
  description = "The size of the the PostgreSQL server"
  type        = number
  default     = 65536
}


variable "postgres_backup_retention_days" {
  description = "The number of days to retain backups for"
  type        = number
  default     = 7
}

variable "postgres_server_version" {
  description = "The version of the PostgreSQL server"
  type        = string
  default     = "14"
}

variable "alert_email_ids" {
  description = "The email ids to send the alerts to when appcd deployment is having issues"
  type        = list(string)
}

variable "alert_sms_numbers" {
  description = "The phone number(without country code) to send sms alerts to when appcd deployment is having issues."
  type        = list(string)
  default     = []
}
variable "alert_phone_number_country_code" {
  description = "The country code for the alert phone number (without +). Example 1 or 91"
  type        = string
  default     = "1"
}
