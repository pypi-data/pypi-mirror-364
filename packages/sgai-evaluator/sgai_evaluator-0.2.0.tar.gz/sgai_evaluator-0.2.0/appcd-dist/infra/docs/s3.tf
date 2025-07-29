/*
    Terraform template for creating S3 buckets for the documentation website.
*/

// Create S3 buckets for the documentation website.
resource "aws_s3_bucket" "docs_bucket" {
  bucket = "appcd-public-documentation"
}

data "aws_iam_policy_document" "docs_bucket_policy" {

  statement {
    sid       = "AllowCloudFrontServicePrincipal"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.docs_bucket.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = ["arn:aws:cloudfront::584974133937:distribution/EQVDK9RKDRI23"]
    }
  }
}

resource "aws_s3_bucket_policy" "docs_bucket" {
  bucket = aws_s3_bucket.docs_bucket.id
  policy = data.aws_iam_policy_document.docs_bucket_policy.json
}


resource "aws_s3_bucket_public_access_block" "docs_bucket" {
  bucket = aws_s3_bucket.docs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "docs_bucket" {
  bucket = aws_s3_bucket.docs_bucket.id
  rule {
    id     = "delete-objects-after-60-days"
    status = "Disabled"
    expiration {
      days = 60
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "docs_bucket" {
  bucket = aws_s3_bucket.docs_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "docs_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.docs_bucket, aws_s3_bucket_public_access_block.docs_bucket]
  bucket     = aws_s3_bucket.docs_bucket.id
  acl        = "public-read"
}

resource "aws_s3_bucket_website_configuration" "docs_bucket" {
  bucket = aws_s3_bucket.docs_bucket.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

// Create S3 buckets for staging documentation website.
resource "aws_s3_bucket" "staging_bucket" {
  bucket = "appcd-public-documentation-staging"
}

resource "aws_s3_bucket_policy" "staging_bucket" {
  bucket = aws_s3_bucket.staging_bucket.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "PublicReadGetObject",
        "Effect" : "Allow",
        "Principal" : "*",
        "Action" : "s3:GetObject",
        "Resource" : "${aws_s3_bucket.staging_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "staging_bucket" {
  bucket = aws_s3_bucket.staging_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_lifecycle_configuration" "staging_bucket" {
  bucket = aws_s3_bucket.staging_bucket.id
  rule {
    id     = "delete-objects-after-60-days"
    status = "Disabled"
    expiration {
      days = 60
    }
  }
}

resource "aws_s3_bucket_ownership_controls" "staging_bucket" {
  bucket = aws_s3_bucket.staging_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "staging_bucket" {
  depends_on = [aws_s3_bucket_ownership_controls.staging_bucket, aws_s3_bucket_public_access_block.staging_bucket]
  bucket     = aws_s3_bucket.staging_bucket.id
  acl        = "public-read"
}

resource "aws_s3_bucket_website_configuration" "staging_bucket" {
  bucket = aws_s3_bucket.staging_bucket.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

// Create bucket and config for enterprise-docs bucket
resource "aws_s3_bucket" "ent_docs_bucket" {
  bucket = "appcd-enterprise-public-documentation"
}

data "aws_iam_policy_document" "ent_docs_bucket_policy" {

  statement {
    sid       = "AllowCloudFrontServicePrincipal"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.ent_docs_bucket.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = ["${aws_cloudfront_distribution.ent_docs_distribution.arn}"]
    }
  }
}

resource "aws_s3_bucket_policy" "ent_docs_bucket" {
  bucket = aws_s3_bucket.ent_docs_bucket.id
  policy = data.aws_iam_policy_document.ent_docs_bucket_policy.json
}


resource "aws_s3_bucket_public_access_block" "ent_docs_bucket" {
  bucket = aws_s3_bucket.ent_docs_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "ent_docs_bucket" {
  bucket = aws_s3_bucket.ent_docs_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_website_configuration" "ent_docs_bucket" {
  bucket = aws_s3_bucket.ent_docs_bucket.id
  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "error.html"
  }
}

// Outputs
output "docs_bucket_name" {
  value = aws_s3_bucket.docs_bucket.id
}

output "staging_bucket_name" {
  value = aws_s3_bucket.staging_bucket.id
}

output "ent_docs_bucket_name" {
  value = aws_s3_bucket.ent_docs_bucket.id
}
