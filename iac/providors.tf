terraform {
  required_version = ">=1.9"
  backend "local" {
    path = "state/terraform.state"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.23.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.6.1"
    }
  }
}

provider "aws" {
  region                   = var.region
  profile                  = "default"
  shared_config_files      = ["/home/xl/.aws/config"]
  shared_credentials_files = ["/home/xl/.aws/credentials"]
  default_tags {
    tags = {
      Provisioned = "Terraform"
      Project     = var.project
      Environment = var.environment
    }
  }
}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}