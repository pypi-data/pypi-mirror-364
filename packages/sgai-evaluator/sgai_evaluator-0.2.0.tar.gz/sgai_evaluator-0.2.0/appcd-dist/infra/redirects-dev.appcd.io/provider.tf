terraform {
  backend "s3" {
    bucket  = "339712749745-states"
    key     = "redirects-dev.appcd.io/terraform.tfstate"
    region  = "us-west-2"
    encrypt = true
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

data "aws_route53_zone" "dev_appcd_io" {
  name = "dev.appcd.io."
}

data "aws_acm_certificate" "dev_appcd_io" {
  provider = aws.us-east-1
  domain   = "*.dev.appcd.io"
  statuses = ["ISSUED"]
}
