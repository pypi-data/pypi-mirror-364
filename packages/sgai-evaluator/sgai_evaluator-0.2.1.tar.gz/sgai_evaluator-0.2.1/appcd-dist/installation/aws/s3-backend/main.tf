terraform {
  backend "s3" {
    region = "us-west-2"
  }
}


variable "region" {
  description = "AWS region"
  default     = "us-west-2"
}
provider "aws" {
  region = var.region

}
// get current account id
data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "${data.aws_caller_identity.current.account_id}-states"
}

// remove public acccess to the bucket
resource "aws_s3_bucket_public_access_block" "my_bucket" {
  bucket = aws_s3_bucket.my_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

// enable versioning
resource "aws_s3_bucket_versioning" "my_bucket" {
  bucket = aws_s3_bucket.my_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
