resource "aws_s3_bucket" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket_prefix = "${var.service_name}-cdn-access-logs"
  force_destroy = false
  # checkov:skip=CKV2_AWS_62:Event notification not necessary for this bucket especially due to likely use of lifecycle rules
  # checkov:skip=CKV_AWS_18:Access logging was not considered necessary for this bucket
  # checkov:skip=CKV_AWS_144:Not considered critical to the point of cross region replication
  # checkov:skip=CKV_AWS_300:Known issue where Checkov gets confused by multiple rules
  # checkov:skip=CKV_AWS_21:Bucket versioning is not worth it in this use case
  # checkov:skip=CKV_AWS_145:Use KMS in future work
  # checkov:skip=CKV2_AWS_65:We need ACLs for Cloudfront
  # checkov:skip=CKV2_AWS_6:False positive
  # checkov:skip=CKV2_AWS_61:False positive
}

resource "aws_s3_bucket_ownership_controls" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket = aws_s3_bucket.cdn[0].id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
  # checkov:skip=CKV2_AWS_65:We need ACLs for Cloudfront
}

resource "aws_s3_bucket_acl" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket = aws_s3_bucket.cdn[0].id

  acl = "log-delivery-write"

  depends_on = [aws_s3_bucket_ownership_controls.cdn[0]]
}

resource "aws_s3_bucket_public_access_block" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket = aws_s3_bucket.cdn[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "cdn" {
  count = local.enable_cdn ? 1 : 0

  statement {
    actions = [
      "s3:GetObject",
    ]

    resources = [
      "${aws_s3_bucket.cdn[0].arn}/*",
    ]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.cdn[0].iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket = aws_s3_bucket.cdn[0].id
  policy = data.aws_iam_policy_document.cdn[0].json
}

resource "aws_s3_bucket_lifecycle_configuration" "cdn" {
  count = local.enable_cdn ? 1 : 0

  bucket = aws_s3_bucket.cdn[0].id

  rule {
    id     = "AbortIncompleteUpload"
    status = "Enabled"
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # checkov:skip=CKV_AWS_300:There is a known issue where this check brings up false positives
}
