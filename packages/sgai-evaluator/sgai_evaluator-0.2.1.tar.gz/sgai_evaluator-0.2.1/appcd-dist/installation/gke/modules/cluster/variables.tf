variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Region"
}

variable "zones" {
  type        = list(string)
  description = "GCP Availability Zones"
}

variable "suffix" {
  type        = string
  description = "resource suffix"
  default     = "dev"
}

variable "labels" {
  type        = map(string)
  description = "labels to apply to all resources"
  default     = {}
}

variable "machine_type" {
  description = "The machine type to use for the GKE nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "min_count" {
  description = "The minimum number of nodes to be created."
  type        = number
  default     = 1
}

variable "max_count" {
  description = "The maximum number of nodes to be created."
  type        = number
}


variable "devops_ips" {
  description = "List of IP addresses to allow access to the GKE master"
  type        = map(string)
}

variable "retention_period" {
  description = "Retention period for objects in storage bucket"
  type        = number
  default     = 0
}
