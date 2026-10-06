# ============================================================
# terraform/main.tf
# DevTrack AI Infrastructure as Code (IaC) for AWS
#
# PROVISIONS:
# 1. VPC + Public Subnet + Internet Gateway + Route Table
# 2. Security Group (Firewall for SSH, HTTP, K3s NodePorts)
# 3. Ubuntu 22.04 LTS EC2 Instance (for K3s Kubernetes host)
# 4. AWS Elastic IP (Static IP allocation)
# ============================================================

# ──────────────────────────────────────────────
# 1. NETWORKING: VPC, Subnet, Internet Gateway
# ──────────────────────────────────────────────

resource "aws_vpc" "devtrack_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "devtrack-vpc"
  }
}

resource "aws_subnet" "devtrack_public_subnet" {
  vpc_id                  = aws_vpc.devtrack_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "devtrack-public-subnet"
  }
}

resource "aws_internet_gateway" "devtrack_igw" {
  vpc_id = aws_vpc.devtrack_vpc.id

  tags = {
    Name = "devtrack-igw"
  }
}

resource "aws_route_table" "devtrack_public_rt" {
  vpc_id = aws_vpc.devtrack_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.devtrack_igw.id
  }

  tags = {
    Name = "devtrack-public-rt"
  }
}

resource "aws_route_table_association" "devtrack_public_assoc" {
  subnet_id      = aws_subnet.devtrack_public_subnet.id
  route_table_id = aws_route_table.devtrack_public_rt.id
}

# ──────────────────────────────────────────────
# 2. SECURITY GROUP (FIREWALL RULES)
# ──────────────────────────────────────────────

resource "aws_security_group" "devtrack_sg" {
  name        = "devtrack-security-group"
  description = "Security group for DevTrack AI K3s host on AWS"
  vpc_id      = aws_vpc.devtrack_vpc.id

  # SSH Access
  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # HTTP Web Traffic
  ingress {
    description = "HTTP Traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # FastAPI Backend Port
  ingress {
    description = "FastAPI Backend Port"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes NodePort Range (for K3s Services, Prometheus 30090, Grafana 30030)
  ingress {
    description = "Kubernetes NodePort Range"
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound internet traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    ="-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "devtrack-sg"
  }
}

# ──────────────────────────────────────────────
# 2.5 AUTOMATED SSH KEY PAIR GENERATION
# ──────────────────────────────────────────────

resource "tls_private_key" "devtrack_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "devtrack_key_pair" {
  key_name   = var.key_name
  public_key = tls_private_key.devtrack_key.public_key_openssh
}

resource "local_file" "private_key" {
  content  = tls_private_key.devtrack_key.private_key_pem
  filename = "${path.module}/id_rsa_devtrack.pem"
}

# ──────────────────────────────────────────────
# 3. AMI LOOKUP & EC2 INSTANCE PROVISIONING
# ──────────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical AWS Account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "devtrack_k3s_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.devtrack_public_subnet.id
  vpc_security_group_ids = [aws_security_group.devtrack_sg.id]
  key_name               = aws_key_pair.devtrack_key_pair.key_name

  root_block_device {
    volume_size           = 20 # GB
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # User Data Script: Initial system setup on boot
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y curl git docker.io
              systemctl enable docker
              systemctl start docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "devtrack-k3s-server"
  }
}

# ──────────────────────────────────────────────
# 4. ELASTIC IP (STATIC PUBLIC IP)
# ──────────────────────────────────────────────

resource "aws_eip" "devtrack_eip" {
  instance = aws_instance.devtrack_k3s_server.id
  domain   = "vpc"

  tags = {
    Name = "devtrack-elastic-ip"
  }
}
