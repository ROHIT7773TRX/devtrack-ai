# DevTrack AI — Complete Teacher & Viva Demonstration Guide

> **This guide provides exact step-by-step commands and talking points to demonstrate DevTrack AI both LOCALLY (on your laptop) and on the CLOUD (AWS + Kubernetes).**

---

## 📌 TABLE OF CONTENTS

1. [Prerequisites Checklist](#1-prerequisites-checklist)
2. [Option A: Local Demonstration (Docker Desktop)](#2-option-a-local-demonstration-docker-desktop)
3. [Option B: Cloud Demonstration (AWS + Terraform + K3s Kubernetes)](#3-option-b-cloud-demonstration-aws--terraform--k3s-kubernetes)
4. [Monitoring Demonstration (Prometheus & Grafana)](#4-monitoring-demonstration-prometheus--grafana)
5. [Automated CI/CD Pipeline Demonstration (GitHub Actions)](#5-automated-cicd-pipeline-demonstration-github-actions)
6. [Automated Testing Demonstration (Pytest)](#6-automated-testing-demonstration-pytest)
7. [Teacher Script & Viva Talking Points (What to Say & Show)](#7-teacher-script--viva-talking-points-what-to-say--show)
8. [AWS Emergency Cost Cleanup (Crucial)](#8-aws-emergency-cost-cleanup-crucial)

---

## 1. PREREQUISITES CHECKLIST

Before starting the demonstration:

### For Local Demo:
- [ ] Open **Docker Desktop** on Windows and ensure it says *"Engine Running"* (green status at bottom left).
- [ ] Open **PowerShell** or VS Code Terminal as Administrator.
- [ ] Move into your project directory:
  ```powershell
  cd D:\synopsis
  ```

### For Cloud Demo:
- [ ] AWS Account with IAM Access Key and Secret Key configured (`aws configure` or environment variables).
- [ ] Terraform installed (`terraform -v`).

---

## 2. OPTION A: LOCAL DEMONSTRATION (DOCKER DESKTOP)

This is the fastest, 100% reliable demonstration method on your laptop without using cloud credits.

### Step 1: Open PowerShell / Terminal
Open VS Code terminal or PowerShell inside `D:\synopsis`:

```powershell
cd D:\synopsis
```

### Step 2: Run Automated Tests First (Impression Point)
Show your teacher that you follow Test-Driven Development (TDD) before running the app:

```powershell
# Run the helper script
.\scripts\dev.ps1 test
```
*Alternative raw command:*
```powershell
.\app\backend\.venv\Scripts\python.exe -m pytest tests/ -v
```

> 🗣️ **What to tell your teacher:**  
> *"Sir/Ma'am, before starting our application, we run our automated test suite (11 unit and integration tests) using pytest. This ensures our backend APIs, schema validations, and database CRUD operations are 100% functional."*

---

### Step 3: Launch Multi-Container Stack using Docker Compose

```powershell
# Launch Postgres, Backend, and Frontend containers simultaneously
.\scripts\dev.ps1 compose-up
```
*Alternative raw command:*
```powershell
docker compose -f docker/docker-compose.yml up --build -d
```

---

### Step 4: Verify Running Containers
Show your teacher the isolated microservices running in Docker:

```powershell
docker ps
```

You will see 3 running containers:
1. `devtrack-frontend` (React + Nginx on Port 3000)
2. `devtrack-backend` (FastAPI Python on Port 8000)
3. `devtrack-db` (PostgreSQL 15 on Port 5432)

---

### Step 5: Open Browser URLs to Show the Live Demo

Open your browser (Chrome/Edge) and navigate to these links:

| URL | What it shows | What to explain |
|---|---|---|
| **`http://localhost:3000`** | **React.js Dashboard UI** | Add a job application (e.g., Company: "Google", Role: "DevOps Engineer", Status: "Applied"). Show status cards and analytics updating instantly. |
| **`http://localhost:8000/docs`** | **FastAPI Interactive OpenAPI Docs** | Show the REST API endpoints (`/applications`, `/dashboard`, `/health`). Click "Try it out" on `GET /applications`. |
| **`http://localhost:8000/health`** | **Kubernetes Liveness Endpoint** | Returns `{"status":"healthy"}`. Explain that Kubernetes uses this for container self-healing. |
| **`http://localhost:8000/metrics`** | **Prometheus Raw Metrics** | Show raw request counts, latency, and system memory metrics exposed for Prometheus. |

---

### Step 6: Stop Local Stack After Demo
```powershell
.\scripts\dev.ps1 compose-down
```

---

## 3. OPTION B: CLOUD DEMONSTRATION (AWS + TERRAFORM + K3s KUBERNETES)

Demonstrate real Infrastructure as Code (IaC) and Cloud Kubernetes deployment on AWS.

---

### Step 1: Provision AWS Infrastructure with Terraform

Open PowerShell inside `D:\synopsis\terraform`:

```powershell
cd D:\synopsis\terraform

# 1. Initialize Terraform plugins
terraform init

# 2. Preview resources to be created (VPC, Security Group, EC2, Elastic IP)
terraform plan

# 3. Create AWS Infrastructure (Type 'yes' when prompted)
terraform apply
```

> 📝 **Take note of the output variables:**
> - `ec2_public_ip` (e.g., `54.210.12.34`)
> - `ssh_connection_command`

---

### Step 2: Connect to AWS EC2 Instance via SSH

```bash
ssh -i ~/.ssh/devtrack-ec2-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

### Step 3: Install K3s Lightweight Kubernetes on EC2

Inside the EC2 SSH terminal, run:

```bash
# Install K3s Kubernetes single-node cluster
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

# Verify Kubernetes node status
kubectl get nodes
```

---

### Step 4: Deploy DevTrack AI Kubernetes Manifests

Clone your GitHub repository directly onto the EC2 instance and apply Kubernetes manifests:

```bash
# Clone repo on EC2
git clone https://github.com/ROHIT7773TRX/devtrack-ai.git
cd devtrack-ai

# Apply all Kubernetes manifests
kubectl apply -f kubernetes/00-namespace.yaml
kubectl apply -f kubernetes/01-configmap.yaml
kubectl apply -f kubernetes/02-secret.yaml
kubectl apply -f kubernetes/03-postgres.yaml
kubectl apply -f kubernetes/04-backend.yaml
kubectl apply -f kubernetes/05-frontend.yaml
kubectl apply -f kubernetes/06-hpa.yaml
kubectl apply -f kubernetes/monitoring/
```

---

### Step 5: Verify Kubernetes Cluster & Pod Status

Show your teacher real Kubernetes Pods, Services, and Auto-scaling running on AWS:

```bash
# Check all pods in devtrack namespace
kubectl get pods -n devtrack

# Check services & NodePorts
kubectl get svc -n devtrack

# Check Horizontal Pod Autoscaler (HPA)
kubectl get hpa -n devtrack
```

> 🗣️ **What to tell your teacher:**  
> *"Sir/Ma'am, Kubernetes manages 2 backend pod replicas and 2 frontend pod replicas. If one pod crashes, Kubernetes self-heals by restarting it. If CPU load exceeds 70%, the Horizontal Pod Autoscaler automatically scales the backend up to 5 replicas."*

---

## 4. MONITORING DEMONSTRATION (PROMETHEUS & GRAFANA)

Demonstrate real-time Observability & Monitoring tools.

### Accessing Prometheus & Grafana on AWS

Using your **AWS EC2 Public IP** (`<EC2_PUBLIC_IP>`):

| Tool | Cloud URL | Default Credentials | Demonstration Steps |
|---|---|---|---|
| **Prometheus** | **`http://<EC2_PUBLIC_IP>:30090`** | None | 1. Open URL.<br>2. In search bar, type `http_requests_total` and click **Execute**.<br>3. Click **Graph** tab to show HTTP traffic metrics over time. |
| **Grafana** | **`http://<EC2_PUBLIC_IP>:30030`** | User: `admin`<br>Pass: `admin` | 1. Log in.<br>2. Go to **Dashboards** → **New Dashboard**.<br>3. Select Prometheus data source (`http://prometheus-service:9090`).<br>4. Show real-time CPU & HTTP latency graphs. |

> 🗣️ **What to tell your teacher:**  
> *"Prometheus continuously scrapes metrics exposed by our FastAPI `/metrics` endpoint every 15 seconds. Grafana visualizes these metrics into interactive dashboards to monitor server health, HTTP status codes (200s vs 500s), and memory usage."*

---

## 5. AUTOMATED CI/CD PIPELINE DEMONSTRATION (GITHUB ACTIONS)

Demonstrate automated deployment whenever code is pushed.

1. Open your GitHub Repository:  
   👉 **[https://github.com/ROHIT7773TRX/devtrack-ai](https://github.com/ROHIT7773TRX/devtrack-ai)**
2. Click on the **Actions** tab.
3. Show your teacher the **"DevTrack AI CI/CD Pipeline"** workflow.
4. Explain the 3 automated jobs:
   - **Job 1: Run Automated Tests (`pytest`)** — Ensures broken code is never built.
   - **Job 2: Build & Push Docker Images** — Builds multi-stage Docker images and pushes to Docker Hub.
   - **Job 3: Deploy to K3s on AWS EC2** — SSHs into EC2 and executes `kubectl rollout restart`.

---

## 6. AUTOMATED TESTING DEMONSTRATION (PYTEST)

Show how test failures block pipeline execution (Controlled Failure Demo):

1. Open `tests/unit/test_applications.py`.
2. Temporarily change an assertion in `test_health_check`:
   ```python
   # Change from 200 to 500 to demonstrate failure
   assert response.status_code == 500
   ```
3. Run `.\scripts\dev.ps1 test` in terminal.
4. Show the red `FAILED` error message.
5. Revert the line back to `200` and re-run to show `PASSED` (green).

---

## 7. TEACHER SCRIPT & VIVA TALKING POINTS (WHAT TO SAY & SHOW)

Follow this structure during your 5-minute presentation:

### 1. Introduction (30 seconds)
> *"Good morning Sir/Ma'am. My project is **DevTrack AI**, a cloud-native Job Application and Career Management Platform. Beyond building a full-stack React and FastAPI application, the primary goal of this project is demonstrating modern DevOps architecture — Containerization with Docker, Infrastructure as Code with Terraform, Kubernetes Orchestration with K3s, CI/CD with GitHub Actions, and Monitoring with Prometheus and Grafana."*

### 2. Live Application Demo (1 minute)
> *"First, let me show the working application running locally in Docker Desktop. Here on the React frontend (`localhost:3000`), users can log job applications, update application statuses from Applied to Interview or Offer, and view automated dashboard analytics. On `localhost:8000/docs`, FastAPI automatically generates OpenAPI documentation."*

### 3. Automated Testing (30 seconds)
> *"Before any code goes to production, our test suite runs 11 unit and integration tests using pytest (`.\scripts\dev.ps1 test`). This validates database models, response schemas, and REST endpoints."*

### 4. Infrastructure as Code & AWS Deployment (1 minute)
> *"For cloud hosting, we avoid manual AWS console clicking by writing Infrastructure as Code in Terraform. Terraform provisions a custom VPC, Subnet, Security Groups with open NodePorts, an EC2 instance, and an Elastic IP in a single command (`terraform apply`)."*

### 5. Kubernetes Orchestration & Scaling (1 minute)
> *"On AWS, we run K3s Kubernetes. We created manifests for Namespace isolation, ConfigMaps, Secrets for base64 credentials, PostgreSQL PVC storage, and 2-replica Deployments for backend and frontend. If a pod crashes, Kubernetes self-heals by restarting it. We also configured Horizontal Pod Autoscaling (HPA) based on CPU load."*

### 6. Observability & Monitoring (30 seconds)
> *"Finally, for operational observability, our FastAPI backend exposes metrics at `/metrics`. Prometheus scrapes these metrics, and Grafana visualizes CPU, RAM, and HTTP request metrics on NodePort 30030."*

---

## 8. AWS EMERGENCY COST CLEANUP (CRUCIAL)

> ⚠️ **IMPORTANT:** Immediately after completing your cloud presentation, destroy all AWS resources to avoid any unwanted charges on your AWS account/credits!

Open PowerShell in `D:\synopsis\terraform`:

```powershell
cd D:\synopsis\terraform

# Destroy all AWS resources (EC2, Elastic IP, VPC, Security Group)
terraform destroy
```
*Type `yes` when prompted.*

Output will confirm:  
`Destroy complete! Resources: 7 destroyed.`  
**Your AWS cost returns to \$0 immediately.**
