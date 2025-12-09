###############################################################################
# module: root
###############################################################################

# Get authorization credentials from ECR
data "aws_ecr_authorization_token" "token" {}

locals {
  image_repo_url = replace(data.aws_ecr_authorization_token.token.proxy_endpoint, "https://", "")
}

resource "aws_ecr_repository" "lambda" {
  name                 = "lambda"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

resource "docker_image" "udemy_web_scraper" {
  name = "${local.image_repo_url}/${aws_ecr_repository.lambda.name}:${var.udemy_function_name}"
  build {
    context    = "../${path.root}"
    dockerfile = "Dockerfile"
    tag        = ["${var.udemy_function_name}:v0.1"]
    build_args = {
      SRC_PATH : "./src/web_scraper"
      PYTHON_VERSION : var.python_version
      AUTHOR : "dataengineer24"
      DESCRIPTION : "AWS lambda function to scrape udemy course data"
    }
  }
  #   triggers = {
  #     #dir_sha1 = sha1(join("", [for f in fileset(path.module, "src/**") : filesha1(f)]))
  #     dir_sha1 = sha1("../${path.root}/src/web_scraper")
  #   }
}

resource "docker_image" "udemy_image_scraper" {
  name = "${local.image_repo_url}/${aws_ecr_repository.lambda.name}:${var.certificate_function_name}"
  build {
    context    = "../${path.root}"
    dockerfile = "Dockerfile.ubuntu"
    tag        = ["${var.certificate_function_name}:v0.1"]
    build_args = {
      SRC_PATH : "./src/image_scraper"
      PYTHON_VERSION : var.python_version
      AUTHOR : "dataengineer24"
      DESCRIPTION : "AWS lambda function to scrape certificate data"
    }
  }
}

# push image to ecr repo
resource "docker_registry_image" "upload_udemy_web_scraper" {
  name = docker_image.udemy_web_scraper.name
}

resource "docker_registry_image" "upload_udemy_image_scraper" {
  name = docker_image.udemy_image_scraper.name
}
