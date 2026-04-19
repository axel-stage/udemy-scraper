###############################################################################
# module: root
###############################################################################

locals {
  ecr_login_url = data.aws_ecr_authorization_token.this.proxy_endpoint
  ecr_repo_url  = aws_ecr_repository.lambda.repository_url
  ecr_token     = data.aws_ecr_authorization_token.this
  image_tag_api = "${local.ecr_repo_url}:${var.api_function_name}-${var.api_image_version}"
  image_tag_certificate = "${local.ecr_repo_url}:${var.certificate_function_name}-${var.certificate_image_version}"
  image_tag_pipeline    = "${local.ecr_repo_url}:${var.pipeline_function_name}-${var.pipeline_image_version}"
}

###############################################################################
# ecr

resource "aws_ecr_repository" "lambda" {
  name                 = "${var.project}-lambda"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

resource "terraform_data" "login" {

  triggers_replace = [
    var.api_image_version,
    var.certificate_image_version,
    var.pipeline_image_version
  ]

  provisioner "local-exec" {
    command = <<EOT
      docker login ${local.ecr_login_url} \
        --username ${local.ecr_token.user_name} \
        --password ${local.ecr_token.password}
    EOT
  }
}

resource "terraform_data" "build_api" {
  depends_on = [terraform_data.login]

  triggers_replace = [
    var.api_image_version
  ]

  provisioner "local-exec" {
    command = <<EOT
      docker build \
        -t ${local.image_tag_api} \
        -f ./docker/Dockerfile \
        --build-arg PYTHON_VERSION=${var.python_version} \
        --build-arg AUTHOR="dataengineer24" \
        --build-arg DESCRIPTION="AWS lambda function to fetch API data" \
        --build-arg SRC_PATH="./src/fetch_api" \
        ..
    EOT
  }
}

resource "terraform_data" "build_certificate" {
  depends_on = [terraform_data.login]

  triggers_replace = [
    var.certificate_image_version
  ]

  provisioner "local-exec" {
    command = <<EOT
      docker build \
        -t ${local.image_tag_certificate} \
        -f ./docker/Dockerfile.tesseract \
        --build-arg PYTHON_VERSION=${var.python_version} \
        --build-arg AUTHOR="dataengineer24" \
        --build-arg DESCRIPTION="AWS lambda function to scrape certificate data" \
        --build-arg SRC_PATH="./src/image_scraper" \
        ..
    EOT
  }
}

resource "terraform_data" "build_pipeline" {
  depends_on = [terraform_data.login]

  triggers_replace = [
    var.pipeline_image_version
  ]

  provisioner "local-exec" {
    command = <<EOT
      docker build \
        -t ${local.image_tag_pipeline} \
        -f ./docker/Dockerfile \
        --build-arg PYTHON_VERSION=${var.python_version} \
        --build-arg AUTHOR="dataengineer24" \
        --build-arg DESCRIPTION="AWS lambda function for ETL pipeline" \
        --build-arg SRC_PATH="./src/etl_pipeline" \
        ..
    EOT
  }
}

resource "terraform_data" "push_api" {
  depends_on = [
    terraform_data.login,
    terraform_data.build_api
  ]
  triggers_replace = [
    var.api_image_version
  ]
  provisioner "local-exec" {
    command = <<EOT
      docker image push ${local.image_tag_api}
    EOT
  }
}

resource "terraform_data" "push_certificate" {
  depends_on = [
    terraform_data.login,
    terraform_data.build_certificate
  ]
  triggers_replace = [
    var.certificate_image_version
  ]
  provisioner "local-exec" {
    command = <<EOT
      docker image push ${local.image_tag_certificate}
    EOT
  }
}

resource "terraform_data" "push_pipeline" {
  depends_on = [
    terraform_data.login,
    terraform_data.build_pipeline
  ]
  triggers_replace = [
    var.pipeline_image_version
  ]
  provisioner "local-exec" {
    command = <<EOT
      docker image push ${local.image_tag_pipeline}
    EOT
  }
}