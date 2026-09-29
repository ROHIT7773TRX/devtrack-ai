# ============================================================
# terraform/variables.tf
# Input variable definitions for AWS Infrastructure
# ============================================================

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS Region to provision resources (e.g., us-east-1, ap-south-1)"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment name"
}

variable "instance_type" {
  type        = string
  default     = "t3.small"
  description = "EC2 Instance type (t2.micro is Free-tier eligible; t3.small ~ $0.02/hr recommended for running K3s + monitoring)"
}

variable "key_name" {
  type        = string
  default     = "devtrack-ec2-key"
  description = "Name of existing AWS SSH Key Pair for EC2 access"
}

variable "allowed_ssh_cidr" {
  type        = string
  default     = "0.0.0.0/0"
  description = "CIDR block permitted for SSH access (Restrict to your IP for enhanced security)"
}
