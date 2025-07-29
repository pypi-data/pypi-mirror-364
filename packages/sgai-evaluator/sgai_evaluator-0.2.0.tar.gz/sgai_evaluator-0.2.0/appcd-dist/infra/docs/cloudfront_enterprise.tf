// This tf file is used to create a cloudfront distribution for the enterprise documentation bucket

resource "aws_cloudfront_origin_access_control" "ent_docs_oac" {
  name                              = aws_s3_bucket.ent_docs_bucket.bucket
  description                       = "OAC for ${aws_s3_bucket.ent_docs_bucket.bucket}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "ent_docs_distribution" {
  origin {
    domain_name              = aws_s3_bucket.ent_docs_bucket.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.ent_docs_bucket.id}" # This is the origin ID
    origin_access_control_id = aws_cloudfront_origin_access_control.ent_docs_oac.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"


  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.ent_docs_bucket.id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    lambda_function_association {
      event_type   = "viewer-request"
      lambda_arn   = aws_lambda_function.basic_auth_lambda.qualified_arn
      include_body = false
    }

    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  viewer_certificate {
    acm_certificate_arn = data.aws_acm_certificate.ent_issued.arn
    ssl_support_method  = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  aliases = ["enterprise-docs.appcd.io", "enterprise-docs.stackgen.com"]
}

data "aws_acm_certificate" "ent_issued" {
  domain   = "enterprise-docs.stackgen.com"
  statuses = ["ISSUED"]
  provider = aws.us-east-1
}

output "ent_docs_distribution_url" {
  value = aws_cloudfront_distribution.ent_docs_distribution.domain_name
}
