terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

# Get the hosted zone for dev.stackgen.com
data "aws_route53_zone" "dev_stackgen" {
  name = "dev.stackgen.com."
}

# Create DNS record for Langfuse
resource "aws_route53_record" "langfuse" {
  zone_id = data.aws_route53_zone.dev_stackgen.zone_id
  name    = "observe.dev.stackgen.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["k8s-ingressn-ingressn-efb5f6ecf7-a04f395ff369e7c5.elb.us-west-2.amazonaws.com"]
} 