locals {
  # We have the option to route the CDN to multiple origins based on the origin id.
  # We do not currently do this, though.
  default_origin_id        = "default"
  ssl_protocols            = ["TLSv1.2"]
  minimum_protocol_version = "TLSv1.2_2021"
  enable_cdn               = var.enable_alb_cdn || var.enable_s3_cdn

  # The domain name of the CDN, ie. URL people use in order to access the CDN.
  # Null outputs here result in the CDN content being served from the CDN's default domain name.
  #   - If the origin is an ALB, and the ALB's domain name is not null,
  #     then use the domain name of the ALB
  #   - If the origin is an ALB, and the ALB's domain name is null,
  #     then return null
  #   - If the origin is an S3 bucket, and the S3 bucket's desired domain name is not null,
  #     then use the domain name of the S3 bucket
  #   - If the origin is an S3 bucket, and the S3 bucket's desired domain name is null,
  #     then return null
  cdn_domain_name         = var.enable_alb_cdn && var.domain != null ? var.domain : var.enable_s3_cdn && var.s3_cdn_domain_name != null ? var.s3_cdn_domain_name : null
  cdn_domain_name_env_var = local.cdn_domain_name != null ? local.cdn_domain_name : aws_cloudfront_distribution.cdn[0].domain_name

  # The domain name of the origin, ie. where the content is being served from.
  #   - If the origin is an ALB, this is the DNS name of the ALB
  #   - If the origin is an S3 bucket, this is the regional domain name of the S3 bucket.
  origin_domain_name = var.enable_alb_cdn ? aws_lb.alb[0].dns_name : var.enable_s3_cdn ? aws_s3_bucket.s3_buckets[var.s3_cdn_bucket_name].bucket_regional_domain_name : null
}

resource "aws_cloudfront_origin_access_identity" "cdn" {
  count = local.enable_cdn ? 1 : 0

  comment = "Origin Access Identity for CloudFront to access S3 bucket"
}

resource "aws_cloudfront_cache_policy" "default" {
  count = local.enable_cdn ? 1 : 0

  name = var.service_name

  # Default to caching for 1 hour.
  # The default TTL can be overriden by the `Cache-Control max-age` or `Expires` headers
  # There's also a `max_ttl` option, which can be used to override the above headers.
  min_ttl     = 0
  default_ttl = 3600

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "all"
    }
    headers_config {
      # The only options are "none" and "whitelist", there is no "all" option
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "all"
    }
  }
}

resource "aws_cloudfront_distribution" "cdn" {
  count = local.enable_cdn ? 1 : 0

  enabled = local.enable_cdn ? true : false
  aliases = local.cdn_domain_name == null ? null : [local.cdn_domain_name]

  origin {
    domain_name = local.origin_domain_name
    origin_id   = local.default_origin_id
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = var.cert_arn == null ? "http-only" : "https-only"

      # See possible values here:
      # https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginSslProtocols.html
      origin_ssl_protocols = local.ssl_protocols
    }
    # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html
    dynamic "origin_shield" {
      for_each = var.cert_arn == null ? [1] : []
      content {
        enabled              = true
        origin_shield_region = data.aws_region.current.name
      }
    }
  }

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cdn[0].bucket_domain_name
  }

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    target_origin_id       = local.default_origin_id
    cache_policy_id        = aws_cloudfront_cache_policy.default[0].id
    compress               = true
    viewer_protocol_policy = var.cert_arn == null ? "allow-all" : "redirect-to-https"

    # Default to caching for 1 hour.
    # The default TTL can be overriden by the `Cache-Control max-age` or `Expires` headers
    # There's also a `max_ttl` option, which can be used to override the above headers.
    min_ttl     = 0
    default_ttl = 3600
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = var.cert_arn == null ? null : var.cert_arn
    cloudfront_default_certificate = var.cert_arn == null ? true : false
    minimum_protocol_version       = local.minimum_protocol_version
    ssl_support_method             = "sni-only"
  }

  depends_on = [
    aws_s3_bucket_public_access_block.cdn[0],
    aws_s3_bucket_policy.cdn[0],
    aws_s3_bucket.cdn[0],
  ]

  #checkov:skip=CKV2_AWS_46:We sometimes use a ALB origin
  #checkov:skip=CKV_AWS_174:False positive
  #checkov:skip=CKV_AWS_310:Configure a failover in future work
  #checkov:skip=CKV_AWS_68:Configure WAF in future work
  #checkov:skip=CKV2_AWS_47:Configure WAF in future work
  #checkov:skip=CKV2_AWS_32:Configure response headers policy in future work
  #checkov:skip=CKV_AWS_374:Ignore the geo restriction
  #checkov:skip=CKV_AWS_305:We don't need a default root object... we don't need to redirect / to index.html.
}
