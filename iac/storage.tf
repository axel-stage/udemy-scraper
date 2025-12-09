###############################################################################
# module: root
###############################################################################

resource "aws_s3_bucket" "udemy" {
  bucket        = "${var.bucket_name}-${local.suffix}"
  force_destroy = var.force_destroy_bucket
}

resource "aws_s3_bucket_versioning" "bucket_versioning" {
  bucket = aws_s3_bucket.udemy.id
  versioning_configuration {
    status = var.bucket_versioning
  }
}

resource "aws_s3_object" "bucket_zones" {
  for_each = toset(var.bucket_zones)
  bucket   = aws_s3_bucket.udemy.id
  key      = each.key
  source   = "/dev/null"

  depends_on = [
    aws_s3_bucket.udemy
  ]
}
