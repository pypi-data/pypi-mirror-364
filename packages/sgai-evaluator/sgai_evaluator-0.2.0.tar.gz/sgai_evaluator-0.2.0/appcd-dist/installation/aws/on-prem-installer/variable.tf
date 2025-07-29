variable "region" {
  description = "The AWS region to deploy resources."
  default     = "us-west-2"
  type        = string
}

variable "tags" {
  description = "A map of tags to add to all resources."
  default     = {}
  type        = map(string)
}

variable "name" {
  description = "The name of the resources."
  type        = string
  default     = "appcd-installer"
}

variable "vpc_id" {
  description = "The VPC ID to deploy resources. if not provided, a new VPC will be created."
  type        = string
}

variable "instance_type" {
  description = "The instance type to deploy."
  type        = string
  default     = "m5.xlarge"
}
