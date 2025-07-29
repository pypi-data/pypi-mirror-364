variable "tags" {
  description = "The tags for the Azure Storage Account"
  type        = map(string)
  default = {
    "repository" = "https://github.com/appcd-dev/appcd-dist"
    "maintainer" = "support@stackgen.com"
  }
}


variable "prefix" {
  description = "Prefix of the Storage Account"
  default     = "cesarappcdstates"
}
