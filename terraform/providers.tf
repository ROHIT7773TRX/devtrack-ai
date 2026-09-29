# ============================================================
# terraform/providers.tf
# HashiCorp Terraform AWS Provider Configuration
# ============================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # NOTE ON STATE STORAGE:
  # By default, Terraform uses a local state file (terraform.tfstate).
  # For team environments or production, an S3 backend with DynamoDB locking is used.
  # For our cost-free academic project, local state is ideal and costs $0.
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "DevTrack-AI"
      Environment = "Production"
      ManagedBy   = "Terraform"
      Owner       = "Rohit"
    }
  }
}
