###############################################################################
# module: root
###############################################################################
variable "project" {
  description = "The Project name"
  type        = string
}

variable "environment" {
  description = "Active environment"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "production"], var.environment)
    error_message = "environment must be 'development' or 'production'"
  }
}

variable "region" {
  description = "Primary AWS region"
  type        = string
  default     = "eu-central-1"
}

###############################################################################
# S3 bucket

variable "bucket_name" {
  description = "AWS S3 bucket name"
  type        = string
}

variable "force_destroy_bucket" {
  description = "Forcing to delete the bucket if it is not empty"
  type        = bool
  default     = false
}

variable "bucket_versioning" {
  description = "Enables versioning of bucket objects"
  type        = string
  default     = "Disabled"
}

variable "bucket_zones" {
  description = "Bucket prefix set"
  type        = set(string)
}

###############################################################################
# IAM role

variable "role_name" {
  description = "Name of the IAM role"
  type        = string
  default     = "lambda-role"
}

###############################################################################
# lambda

variable "udemy_function_name" {
  description = "Describtive name of the AWS lambda function"
  type        = string
  default     = "unknow_name"
}

variable "certificate_function_name" {
  description = "Describtive name of the AWS lambda function"
  type        = string
  default     = "unknow_name"
}

variable "python_version" {
  description = "Version of the cpython release"
  type        = string
  default     = "3.13"
}

variable "function_timeout" {
  description = "Timeout of the lambda function"
  type        = number
  default     = 60
}

variable "function_memory_size" {
  description = "Maximum memory footprint in mb of the lambda function"
  type        = number
  default     = 256
}

variable "lambda_logging_retention" {
  description = "Maximum number of days to keep the lambda function logs"
  type        = number
  default     = 1
}

###############################################################################
# secrets