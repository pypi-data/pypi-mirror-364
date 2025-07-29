variable "prefix" {
  description = "The prefix for the stackgen user"
  type        = string
}

variable "oidc_provider" {
  description = "The OIDC provider for the stackgen user"
  type = object({
    client_id_list  = string
    thumbprint_list = string
    url             = string
  })
}

variable "assume_role_policy" {
  description = "The assume role policy for the stackgen user"
  type = object({
    test     = optional(string, "StringLike")
    variable = string
    values   = list(string)
  })
}
