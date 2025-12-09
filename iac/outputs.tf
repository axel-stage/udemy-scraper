###############################################################################
# module: root
###############################################################################
# dev
output "cwd_path" {
  description = "path"
  value       = path.cwd
}

###############################################################################
# project

output "bucket_id" {
  description = "Bucket ID"
  value       = aws_s3_bucket.udemy.id
}

output "image_id" {
  description = "The name of the image"
  value       = docker_image.udemy_web_scraper.image_id
}

output "role_arn" {
  description = "Lambda role arn"
  value       = aws_iam_role.lambda_role.arn
}

output "udemy_function_name" {
  description = "Name of the Lambda function."
  value       = var.udemy_function_name
}

output "certificate_function_name" {
  description = "Name of the Lambda function."
  value       = var.certificate_function_name
}