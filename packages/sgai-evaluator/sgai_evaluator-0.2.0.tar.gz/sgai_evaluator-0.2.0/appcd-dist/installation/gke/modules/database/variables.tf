variable "suffix" {
  description = "The prefix to apply to all resources."
  type        = string
}

variable "zones" {
  description = "The zones to use for the PostgreSQL instance."
  type        = list(string)
}

variable "project_id" {
  description = "The GCP project ID where resources will be created."
  type        = string
}

variable "region" {
  description = "The GCP region where resources will be created."
  type        = string
  default     = "us-central1"
}

variable "machine_type" {
  description = "The machine type to use for the PostgreSQL instance."
  type        = string
  default     = "db-perf-optimized-N-2"
}

variable "labels" {
  type        = map(string)
  description = "labels to apply to all resources"
}

variable "private_network" {
  description = "The name of the network to use for the database instance."
  type        = string
}
