variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Region"
}

variable "suffix" {
  type        = string
  description = "Suffix to all names"
}

variable "domain" {
  description = "The domain for the appcd without the protocol"
  type        = string
}

variable "STACKGEN_PAT" {
  description = "The GitHub Personal Access Token for the stackgen repository. (This is a sensitive entry)"
  type        = string
  sensitive   = true
}

variable "labels" {
  type        = map(string)
  description = "labels to apply to all resources"
  default     = {}
}

variable "devops_ips" {
  type        = map(string)
  description = "The IP addresses of the DevOps team \n Key: IP Address \n Value: Name"
  default     = {}
}

variable "pre_shared_cert_name" {
  type = string
}