variable "namespace" {
  description = "The namespace to deploy the job to"
  type        = string
}


variable "databases" {
  description = "The databases to create"
  type        = list(string)
}

variable "pg_user" {
  description = "The postgres user to use"
  type        = string
}

variable "rds_endpoint" {
  description = "The postgres endpoint to use"
  type        = string
}

variable "rds_password" {
  description = "The postgres password to use"
  type        = string
  sensitive   = true
}

variable "pg_port" {
  description = "The postgres port to use"
  type        = string
  default     = "5432"
}

variable "secrets_from" {
  description = "The name of the secret to use"
  type        = string
}
