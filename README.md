# Udemy Scraper Project
## Overview
A cloud-native, serverless application designed to scrape metadata and certificate text from Udemy courses, transform the information into structured JSON objects, and store them in AWS cloud storage. This project demonstrates web scraping, OCR processing, serverless architecture, IaC with Terraform and CI/CD Pipeline.
## Table of Contents
1. [Features](#features)
1. [Quick Start](#quick-start)
1. [Business Requirements](#business-requirements)
1. [Functional Requirements](#functional-requirements)
1. [Non-Functional Requirements](#non-functional-requirements)
1. [Lessons Learned](#lessons-learned)
1. [Areas for Improvement](#areas-for-improvement)
1. [License](#license)
## Features
- **Automated Udemy Course Scraping**  
  Extracts course statistics and metadata from all owned Udemy courses.
- **Certificate OCR Extraction**  
  Uses Tesseract OCR to read and convert text from Udemy certificate images.
- **JSON Data Generation**  
  Produces structured, machine-readable JSON objects for both courses and certificates.
- **Serverless Architecture**  
  Runs as a containerized AWS Lambda function for high scalability and low cost.
- **CI/CD Pipeline with AWS ECR**  
  Automates building, containerizing, and pushing images to Amazon ECR for continuous deployment to AWS Lambda.
- **Infrastructure as Code (IaC)**  
  Uses Terraform to provision all resources: Lambda, ECR, S3, IAM roles, etc.
- **AWS Cloud Storage Integration**  
  Automatically uploads scraped JSON files to an S3 bucket.
## Quick Start
**try in <5 minutes**
### Prerequisites
- Docker Engine/Docker Desktop -> [Installation](https://docs.docker.com/engine/install/)
- Terraform -> [Installation](https://developer.hashicorp.com/terraform/)
- AWS CLI -> [Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
### Install
Clone the repository:
```bash
git clone https://github.com/axel-stage/udemy-scraper
```
Navigate to the project's iac directory:
```bash
cd udemy-scraper/iac
```
Change the provider setup in iac/providors.tf:
```hcl
provider "aws" {
  region                   = var.region
  profile                  = "default"
  shared_config_files      = ["<add path to your AWS config file>"]
  shared_credentials_files = ["<add path to your AWS credentials file>"]
  ...
  }
}
```

Use Terraform to deploy infrastructure on AWS:
```bash
terraform init
```
```bash
terraform plan
```
```bash
terraform apply
```
### Run
Invoke lambda functions:
```bash
../bin/invoke_lambda_udemy.sh https://www.udemy.com/course/python-3-deep-dive-part-1/
```
```bash
../bin/invoke_lambda_certificate.sh
```
### Result
Parsed data from a certificate:
```json
{
    "owner": "My name",
    "certificate_id": "UC-0f533ce1-a75f-4696-8507-7a2...",
    "instructors": "James Spurin (Docker Captain / CNCF Ambassador / Kubestronaut), Divelnto Training",
    "title": "Kubernetes Introduction - Docker, Kubernetes + Hands On Labs",
    "course_length": "4",
    "course_end": "July 3, 2025",
    "reference_number": "0004",
    "created": "2025-12-10"
}
```

Parsed data from course web page:
```json
{
    "url": "https://www.udemy.com/course/python-3-deep-dive-part-1/",
    "slug": "python-3-deep-dive-part-1",
    "title": "Python 3: Deep Dive (Part 1 - Functional)",
    "headline": "Variables, Functions and Functional Programming, Closures, Decorators, Modules and Packages",
    "instructors": ["Dr. Fred Baptiste"],
    "topics": ["Development", "Programming Languages", "Python"],
    "students_num": "69,520",
    "rating": "4.8",
    "language": "English",
    "created": "2025-12-10"
}
```
## Business Requirements
### 1. Web Scraping
- Use a web scraping library.
- Scrape statistics and metadata from each Udemy course owned by the user.
- Generate a structured data object for each course.
- Store each data object as a JSON file in cloud storage.
### 2. Image Scraping
- Use an OCR library.
- Extract text from Udemy certificate images.
- Generate a structured data object for each certificate.
- Store each data object as a JSON file in cloud storage
## Functional Requirements
### Development
- Use **GitHub** as the Version Control System.
- Use **Python** as the primary programming language.
- Use **Tesseract OCR** for image scraping.
- Use **BeautifulSoup** for web scraping.
- Required libraries:
  - **UV** – Python package manager
  - **BeautifulSoup** – Web scraping
  - **Pytesseract** – Python wrapper for Tesseract
  - **boto3** – AWS SDK
### Deployment
- Use **AWS** as the cloud service provider.
- Use **Terraform** for Infrastructure as Code (IaC)
- Required providers:
  - aws
  - docker
  - random
- Build the application as a **serverless AWS Lambda** function.
- CI/CD pipeline:
  - Containerize the application using **Docker**.
  - Push the Docker image to **Amazon Elastic Container Registry (ECR)**.
## Non-Functional Requirements
- Design with Serverless architecture for high scalability and low cost.
- Built using IaC methodology for state management and version control.
- Fully automated CI/CD Pipeline.
## Lessons Learned
- It was a nightmare to install tesseract on a amazon linux 2023 container. As workaround, I had to use a ubuntu container and awslambdaric library instead.
- Used uv as package manager the first time in a project and I really enjoyed to learn it, especially the speed and the integration with AWS lambda is great.
## Areas for Improvement
- Install tesseract on a amazon linux 2023 container
## License
This project is licensed under the MIT license.
See [LICENSE](LICENSE) for more information.