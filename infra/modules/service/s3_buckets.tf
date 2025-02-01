resource "aws_s3_bucket" "s3_buckets" {
  for_each = var.s3_buckets

  bucket_prefix = "${var.service_name}-${each.key}-"
  force_destroy = false
  # checkov:skip=CKV2_AWS_62:Event notification not necessary for this bucket especially due to likely use of lifecycle rules
  # checkov:skip=CKV_AWS_18:Access logging was not considered necessary for this bucket
  # checkov:skip=CKV_AWS_144:Not considered critical to the point of cross region replication
  # checkov:skip=CKV_AWS_300:Known issue where Checkov gets confused by multiple rules
  # checkov:skip=CKV_AWS_21:Bucket versioning is not worth it in this use case
  # checkov:skip=CKV_AWS_145:Use KMS in future work
  # checkov:skip=CKV2_AWS_6:False positive
  # checkov:skip=CKV2_AWS_61:False positive
}

resource "aws_s3_bucket_public_access_block" "s3_buckets" {
  for_each = var.s3_buckets

  bucket = aws_s3_bucket.s3_buckets[each.key].id

  block_public_acls       = !each.value.public
  block_public_policy     = !each.value.public
  ignore_public_acls      = !each.value.public
  restrict_public_buckets = !each.value.public

  #checkov:skip=CKV_AWS_56:Some buckets are public on purpose
  #checkov:skip=CKV_AWS_55:Some buckets are public on purpose
  #checkov:skip=CKV_AWS_54:Some buckets are public on purpose
  #checkov:skip=CKV_AWS_53:Some buckets are public on purpose
}

data "aws_iam_policy_document" "s3_buckets_put_access" {
  for_each = var.s3_buckets

  statement {
    effect = "Allow"
    resources = [
      aws_s3_bucket.s3_buckets[each.key].arn,
      "${aws_s3_bucket.s3_buckets[each.key].arn}/*"
    ]
    actions = ["s3:*"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.app_service.arn]
    }
  }

  statement {
    sid    = "AllowSSLRequestsOnly"
    effect = "Deny"
    resources = [
      aws_s3_bucket.s3_buckets[each.key].arn,
      "${aws_s3_bucket.s3_buckets[each.key].arn}/*"
    ]
    actions = ["s3:*"]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = [false]
    }
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }

  dynamic "statement" {
    for_each = (each.value.public) ? [1] : []
    content {
      sid    = "AllowPublicRead"
      effect = "Allow"
      resources = [
        "${aws_s3_bucket.s3_buckets[each.key].arn}/*"
      ]
      actions = ["s3:GetObject"]
      principals {
        type        = "AWS"
        identifiers = ["*"]
      }
    }
  }

  dynamic "statement" {
    for_each = (var.enable_s3_cdn && each.key == var.s3_cdn_bucket_name) ? [1] : []
    content {
      sid       = "AllowCloudFrontIngress"
      effect    = "Allow"
      resources = ["${aws_s3_bucket.s3_buckets[each.key].arn}/*"]
      actions   = ["s3:GetObject"]
      principals {
        type        = "Service"
        identifiers = ["cloudfront.amazonaws.com"]
      }
      condition {
        test     = "StringEquals"
        variable = "AWS:SourceArn"
        values   = [aws_cloudfront_distribution.cdn[0].arn]
      }
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "s3_buckets" {
  for_each = var.s3_buckets

  bucket = aws_s3_bucket.s3_buckets[each.key].id
  rule {
    id     = "AbortIncompleteUpload"
    status = "Enabled"
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # checkov:skip=CKV_AWS_300:There is a known issue where this check brings up false positives
}


resource "aws_s3_bucket_server_side_encryption_configuration" "s3_buckets" {
  for_each = {
    for key, values in var.s3_buckets :
    key => values
    if values.public == false
  }

  bucket = aws_s3_bucket.s3_buckets[each.key].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_policy" "s3_buckets" {
  for_each = var.s3_buckets
  bucket   = aws_s3_bucket.s3_buckets[each.key].id
  policy   = data.aws_iam_policy_document.s3_buckets_put_access[each.key].json
}

resource "aws_ssm_parameter" "s3_bucket_arns" {
  for_each = var.s3_buckets

  name  = "/buckets/${var.service_name}/${each.key}/arn"
  type  = "SecureString"
  value = aws_s3_bucket.s3_buckets[each.key].arn
  # checkov:skip=CKV_AWS_337: KMS encryption is overkill here
}

resource "aws_ssm_parameter" "s3_bucket_ids" {
  for_each = var.s3_buckets

  name  = "/buckets/${var.service_name}/${each.key}/id"
  type  = "SecureString"
  value = aws_s3_bucket.s3_buckets[each.key].id
  # checkov:skip=CKV_AWS_337: KMS encryption is overkill here
}
