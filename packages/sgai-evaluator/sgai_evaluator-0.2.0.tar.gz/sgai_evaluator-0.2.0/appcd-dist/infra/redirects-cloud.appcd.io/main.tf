# cloud.appcd.io redirect to cloud.stackgen.com
module "cloud_appcd_io_redirects" {
  source = "terraform-aws-modules/s3-bucket/aws"
  bucket = "cloud.appcd.io"
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::cloud.appcd.io/*"
      }
    ]
  }
  EOF
  website = {
    redirect_all_requests_to = {
      host_name = "cloud.stackgen.com"
      protocol  = "https"
    }
  }
}

# cloudfront to redirect https traffic from cloud.appcd.io to cloud.stackgen.com
module "cloud_appcd_io_redirects_cloudfront" {
  aliases         = ["cloud.appcd.io"]
  source          = "terraform-aws-modules/cloudfront/aws"
  enabled         = true
  is_ipv6_enabled = true
  price_class     = "PriceClass_100"

  origin = {
    "cloud.appcd.io.s3-website-us-west-2.amazonaws.com" = {
      domain_name           = module.cloud_appcd_io_redirects.s3_bucket_website_endpoint
      origin_access_control = "cloud.appcd.io.s3-website-us-west-2.amazonaws.com"
      custom_origin_config = {
        http_port                = 80
        https_port               = 443
        origin_keepalive_timeout = 5
        origin_protocol_policy   = "http-only"
        origin_read_timeout      = 30
        origin_ssl_protocols = [
          "SSLv3",
          "TLSv1",
          "TLSv1.1",
          "TLSv1.2",
        ]
      }
    }
  }

  default_cache_behavior = {
    compress               = true
    target_origin_id       = "cloud.appcd.io.s3-website-us-west-2.amazonaws.com"
    viewer_protocol_policy = "allow-all"
  }

  viewer_certificate = {
    acm_certificate_arn      = data.aws_acm_certificate.dev_appcd_io.arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}

# route to cloudfront distribution
resource "aws_route53_record" "cloud_appcd_io_redirects" {
  zone_id = data.aws_route53_zone.dev_appcd_io.zone_id
  name    = "cloud.appcd.io"
  type    = "A"

  alias {
    name                   = module.cloud_appcd_io_redirects_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.cloud_appcd_io_redirects_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}

# playground.cloud.appcd.io redirect to cloud.stackgen.com
module "playground_cloud_appcd_io_redirects" {
  source = "terraform-aws-modules/s3-bucket/aws"
  bucket = "playground.cloud.appcd.io"
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::playground.cloud.appcd.io/*"
      }
    ]
  }
  EOF
  website = {
    redirect_all_requests_to = {
      host_name = "cloud.stackgen.com"
      protocol  = "https"
    }
  }
}

# cloudfront to redirect https traffic from playground.cloud.appcd.io to cloud.stackgen.com
module "playground_cloud_appcd_io_redirects_cloudfront" {
  aliases         = ["playground.cloud.appcd.io"]
  source          = "terraform-aws-modules/cloudfront/aws"
  enabled         = true
  is_ipv6_enabled = true
  price_class     = "PriceClass_100"

  origin = {
    "playground.cloud.appcd.io.s3-website-us-west-2.amazonaws.com" = {
      domain_name           = module.playground_cloud_appcd_io_redirects.s3_bucket_website_endpoint
      origin_access_control = "playground.cloud.appcd.io.s3-website-us-west-2.amazonaws.com"
      custom_origin_config = {
        http_port                = 80
        https_port               = 443
        origin_keepalive_timeout = 5
        origin_protocol_policy   = "http-only"
        origin_read_timeout      = 30
        origin_ssl_protocols = [
          "SSLv3",
          "TLSv1",
          "TLSv1.1",
          "TLSv1.2",
        ]
      }
    }
  }

  default_cache_behavior = {
    compress               = true
    target_origin_id       = "playground.cloud.appcd.io.s3-website-us-west-2.amazonaws.com"
    viewer_protocol_policy = "allow-all"
  }

  viewer_certificate = {
    acm_certificate_arn      = data.aws_acm_certificate.dev_appcd_io.arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}

# route to cloudfront distribution
resource "aws_route53_record" "playground_cloud_appcd_io_redirects" {
  zone_id = data.aws_route53_zone.dev_appcd_io.zone_id
  name    = "playground.cloud.appcd.io"
  type    = "A"

  alias {
    name                   = module.playground_cloud_appcd_io_redirects_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.playground_cloud_appcd_io_redirects_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}
