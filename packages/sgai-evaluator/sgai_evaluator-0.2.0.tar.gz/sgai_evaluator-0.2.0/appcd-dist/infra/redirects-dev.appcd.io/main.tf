# main.dev.appcd.io redirects to main.dev.stackgen.com
module "main_dev_appcd_io_redirects" {
  source = "terraform-aws-modules/s3-bucket/aws"
  bucket = "main.dev.appcd.io"
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::main.dev.appcd.io/*"
      }
    ]
  }
  EOF
  website = {
    redirect_all_requests_to = {
      host_name = "main.dev.stackgen.com"
      protocol  = "https"
    }
  }
}

# cloudfront to redirect https traffic from main.dev.appcd.io to main.dev.stackgen.com
module "main_dev_appcd_io_redirects_cloudfront" {
  aliases         = ["main.dev.appcd.io"]
  source          = "terraform-aws-modules/cloudfront/aws"
  enabled         = true
  is_ipv6_enabled = true
  price_class     = "PriceClass_100"

  origin = {
    "main.dev.appcd.io.s3-website-us-west-2.amazonaws.com" = {
      domain_name           = module.main_dev_appcd_io_redirects.s3_bucket_website_endpoint
      origin_access_control = "main.dev.appcd.io.s3-website-us-west-2.amazonaws.com"
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
    target_origin_id       = "main.dev.appcd.io.s3-website-us-west-2.amazonaws.com"
    viewer_protocol_policy = "allow-all"
  }

  viewer_certificate = {
    acm_certificate_arn      = data.aws_acm_certificate.dev_appcd_io.arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}

# route to cloudfront distribution
resource "aws_route53_record" "main_dev_appcd_io_redirects" {
  zone_id = data.aws_route53_zone.dev_appcd_io.zone_id
  name    = "main.dev.appcd.io"
  type    = "A"

  alias {
    name                   = module.main_dev_appcd_io_redirects_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.main_dev_appcd_io_redirects_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}

# stage.dev.appcd.io redirects to stage.dev.stackgen.com
module "stage_dev_appcd_io_redirects" {
  source = "terraform-aws-modules/s3-bucket/aws"
  bucket = "stage.dev.appcd.io"
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::stage.dev.appcd.io/*"
      }
    ]
  }
  EOF
  website = {
    redirect_all_requests_to = {
      host_name = "stage.dev.stackgen.com"
      protocol  = "https"
    }
  }
}

# cloudfront to redirect https traffic from stage.dev.appcd.io to stage.dev.stackgen.com
module "stage_dev_appcd_io_redirects_cloudfront" {
  aliases         = ["stage.dev.appcd.io"]
  source          = "terraform-aws-modules/cloudfront/aws"
  enabled         = true
  is_ipv6_enabled = true
  price_class     = "PriceClass_100"

  origin = {
    "stage.dev.appcd.io.s3-website-us-west-2.amazonaws.com" = {
      domain_name           = module.stage_dev_appcd_io_redirects.s3_bucket_website_endpoint
      origin_access_control = "stage.dev.appcd.io.s3-website-us-west-2.amazonaws.com"
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
    target_origin_id       = "stage.dev.appcd.io.s3-website-us-west-2.amazonaws.com"
    viewer_protocol_policy = "allow-all"
  }

  viewer_certificate = {
    acm_certificate_arn      = data.aws_acm_certificate.dev_appcd_io.arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}

# route to cloudfront distribution
resource "aws_route53_record" "stage_dev_appcd_io_redirects" {
  zone_id = data.aws_route53_zone.dev_appcd_io.zone_id
  name    = "stage.dev.appcd.io"
  type    = "A"
  alias {
    name                   = module.stage_dev_appcd_io_redirects_cloudfront.cloudfront_distribution_domain_name
    zone_id                = module.stage_dev_appcd_io_redirects_cloudfront.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = false
  }
}
