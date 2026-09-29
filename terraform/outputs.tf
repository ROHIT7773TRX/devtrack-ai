# ============================================================
# terraform/outputs.tf
# Terraform Output Values
# ============================================================

output "ec2_public_ip" {
  value       = aws_eip.devtrack_eip.public_ip
  description = "Public Elastic IP address of the provisioned EC2 instance"
}

output "ssh_connection_command" {
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_eip.devtrack_eip.public_ip}"
  description = "Command to SSH directly into the EC2 instance"
}

output "application_url" {
  value       = "http://${aws_eip.devtrack_eip.public_ip}"
  description = "URL to access deployed DevTrack AI frontend"
}

output "k3s_install_command" {
  value       = "curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644"
  description = "Command to execute inside EC2 to install K3s Kubernetes"
}
