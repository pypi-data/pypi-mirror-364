variable "region" {
  description = "The region in which the S3 bucket will be created"
  default     = "us-west-2"
  type        = string
}

variable "allow_connection_from_sg" {
  description = "The security group that will be allowed to connect to the RDS instance"
  type        = string
  sensitive   = true
}


variable "vpc_id" {
  description = "The VPC ID in which the security group will be created"
  type        = string
}

variable "db_subnet_group_name" {
  description = "The name of the DB subnet group"
  type        = string
}


variable "tags" {
  description = "The tags to apply to the resources"
  type        = map(string)
  default     = {}
}


variable "google_auth" {
  type = object({
    client_id     = string
    client_secret = string
    callback_url  = string
  })
  sensitive = true
}

variable "domain_host" {
  type        = string
  description = "domain name of the host"
  default     = ""
}
