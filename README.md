# Udemy Scraper Project
## Business Requirements
### Online scraping
- use web scraping libary
- scrape the stats from each udemy course I own
- generate an object for each course
- store the file as json in the cloud
### PDF scraping
- use pdf library
- access certificates PDF stored in the cloud
- scrape the stats from each certificate
- generate an object for each certificate
- store the file as json in the cloud
### image scraping
- use OCR library
- scrape text from certificate image
- generate an object for each certificate
- store the file as json in the cloud
## Requirements analysis
### Functional Requirements
- PDF scraping shows no content because pdf was created from image :-(
- change apprach to image scraping with Tesseract OCR

- Development
  - Use GitHub as Version Control System
  - Use Python for the source code
    - Use UV as the package manager

- Deployment
  - use Terraform for Infrastucture as Code
    - provider: aws, docker
  - use AWS as cloud service provider
  - build serverless as lambda app
  - build docker image
  - push the image to Elastic Container Registry (ECR)


## challenge
- install tesseract on amazon linux 2023 container