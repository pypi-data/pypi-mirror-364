/*
    Terraform template for creating S3 bucket for hosting released artifacts.
*/

// Create S3 buckets for the releases website
resource "aws_s3_bucket" "bucket" {
  bucket = "appcd-public-releases"
}

# DEV-377
# TODO sync this new bucket with the old one
# TODO update cloudfront to use the new bucket
# TODO also update these https://github.com/search?q=org%3Aappcd-dev%20appcd-public-releases&type=code
resource "aws_s3_bucket" "new_bucket" {
  bucket = "stackgen-public-releases"
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.bucket.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${aws_cloudfront_origin_access_identity.oai.id}"]
    }
  }
}

resource "aws_s3_bucket_policy" "bucket" {
  bucket = aws_s3_bucket.bucket.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}


resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_ownership_controls" "bucket" {
  bucket = aws_s3_bucket.bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_website_configuration" "bucket" {
  bucket = aws_s3_bucket.bucket.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "index.html"
  }
}

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.bucket.id
  key          = "index.html"
  source       = "index.html"
  etag         = filemd5("index.html")
  content_type = "text/html"
}

resource "aws_s3_object" "install" {
  bucket       = aws_s3_bucket.bucket.id
  key          = "install.sh"
  source       = "../../install.sh"
  etag         = filemd5("../../install.sh")
  content_type = "text/x-shellscript"
}

// Outputs
output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}
