# DevTrack AI

> **Cloud-Native Job Application & Career Management Platform**  
> Built with React.js · FastAPI · PostgreSQL · Docker · Kubernetes · Terraform · AWS · GitHub Actions · Prometheus · Grafana

---

## 📌 Project Overview

DevTrack AI is a full-stack, cloud-native web platform designed to help users manage and track their job search activities from a single dashboard. Users can log job applications, track company details, manage interview stages, and visualize their career progress through analytics.

This project is simultaneously:
- A **functional web application**
- A **complete DevOps implementation** demonstrating industry-standard practices
- A **portfolio/CV project** with end-to-end CI/CD, containerization, Kubernetes orchestration, and cloud deployment

---

## 🎯 Problem Statement

Job seekers applying to multiple companies simultaneously have no centralized system to:
- Track which companies they've applied to and when
- Monitor application status across different stages
- Manage interview rounds, schedules, and outcomes
- Visualize progress and identify patterns

DevTrack AI solves this with a centralized, cloud-hosted tracking platform.

---

## 🧩 Core Features

| Feature | Description |
|---|---|
| **Job Application Management** | Create, update, delete, and organize job applications |
| **Company & Role Tracking** | Company name, role, location, source, and notes |
| **Status & Interview Tracking** | Application stages, interview rounds, schedules, and outcomes |
| **Dashboard & Analytics** | Application progress charts, summary statistics, visual reports |

---

## 🏗️ Architecture

```
Developer → GitHub → GitHub Actions (CI/CD)
                          │
                ┌─────────┼─────────┐
                ↓         ↓         ↓
           Run Tests  Docker Build  SSH to AWS
                          │
                    Docker Hub Registry
                          │
              AWS EC2 (Terraform-provisioned)
                          │
                  K3s Kubernetes Cluster
              ┌───────────┼───────────┐
              ↓           ↓           ↓
        React Pods   FastAPI Pods  PostgreSQL
                          │
                  Prometheus + Grafana
                          │
                     End Users
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React.js | User-facing web interface |
| **Backend** | FastAPI (Python) | REST API server |
| **Database** | PostgreSQL | Persistent data storage |
| **Testing** | pytest + httpx | Unit and API integration tests |
| **Containerization** | Docker + Docker Compose | Package and run services |
| **Registry** | Docker Hub | Store Docker images |
| **Orchestration** | Kubernetes / K3s | Container orchestration on AWS |
| **IaC** | Terraform | AWS infrastructure provisioning |
| **Cloud** | AWS EC2 + VPC | Cloud hosting |
| **CI/CD** | GitHub Actions | Automated build, test, deploy |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Source Control** | Git + GitHub | Version control |

---

## 📁 Repository Structure

```
devtrack-ai/
│
├── README.md
├── PROJECT_JOURNEY.md
├── ERRORS_AND_SOLUTIONS.md
│
├── app/
│   ├── backend/          ← FastAPI Python application
│   └── frontend/         ← React.js web application
│
├── tests/
│   ├── unit/             ← pytest unit tests
│   └── integration/      ← pytest API integration tests
│
├── docker/               ← docker-compose for local dev
│
├── terraform/            ← AWS infrastructure as code
│
├── kubernetes/           ← K8s manifests + monitoring
│
├── .github/workflows/    ← GitHub Actions CI/CD pipeline
│
└── docs/                 ← Architecture diagrams, screenshots
```

---

## 🚀 Quick Start — Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- Git

### Run Locally with Docker Compose

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/devtrack-ai.git
cd devtrack-ai

# Copy environment file
cp .env.example .env
# Edit .env with your values

# Start all services
docker compose -f docker/docker-compose.yml up --build

# Application is now running at:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Run Backend Without Docker

```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install -r app/backend/requirements.txt

# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run with coverage report
pytest tests/ --cov=app/backend --cov-report=html
```

---

## 🐳 Docker

```bash
# Build backend image
docker build -t devtrack-backend:latest ./app/backend

# Build frontend image
docker build -t devtrack-frontend:latest ./app/frontend

# Run everything with docker-compose
docker compose -f docker/docker-compose.yml up -d

# Check running containers
docker ps

# View logs
docker compose -f docker/docker-compose.yml logs -f

# Stop everything
docker compose -f docker/docker-compose.yml down
```

---

## 🏗️ Terraform — AWS Infrastructure

```bash
cd terraform/

# Initialize Terraform (download providers)
terraform init

# Preview what will be created
terraform plan

# Create AWS infrastructure
terraform apply

# DESTROY everything when done (avoids charges)
terraform destroy
```

> ⚠️ Always run `terraform destroy` after demonstrations to avoid unnecessary AWS costs.

---

## ☸️ Kubernetes

```bash
# Apply all manifests
kubectl apply -f kubernetes/

# Check pods
kubectl get pods -n devtrack

# Check services
kubectl get services -n devtrack

# View logs
kubectl logs -f deployment/devtrack-backend -n devtrack

# Scale backend
kubectl scale deployment devtrack-backend --replicas=3 -n devtrack
```

---

## 🔄 CI/CD Pipeline

The pipeline runs automatically on every push to `main`:

```
Push to main
    ↓
Checkout code
    ↓
Run pytest (unit + integration tests)  ← Stops if tests fail
    ↓
Build Docker images
    ↓
Push to Docker Hub
    ↓
SSH to AWS EC2
    ↓
kubectl apply (deploy to K3s)
    ↓
Verify pods are running
```

---

## 📊 Monitoring

- **Prometheus:** `http://EC2_IP:30090` — Metrics collection
- **Grafana:** `http://EC2_IP:30030` — Dashboards and visualization
- Default Grafana credentials: `admin` / `admin` (change on first login)

---

## 🔐 Security

- All secrets stored in GitHub Secrets (never in code)
- Kubernetes Secrets for database credentials
- AWS IAM: least-privilege access
- Terraform state: local (not committed to Git)
- `.gitignore` protects `.env`, `*.pem`, `*.tfstate`

---

## 🌐 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/devtrack` |
| `POSTGRES_DB` | Database name | `devtrack` |
| `POSTGRES_USER` | Database user | `devtrack_user` |
| `POSTGRES_PASSWORD` | Database password | (use strong password) |
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |

---

## 💰 AWS Cost Considerations

| Resource | Cost | Notes |
|---|---|---|
| EC2 t2.micro | Free Tier (750 hrs/month) | First 12 months of AWS account |
| EC2 t3.small | ~\$0.02/hr | Use AWS credits; destroy when done |
| Elastic IP | Free when attached | Release after project |
| VPC/SGs | Always free | No charge |

**Total estimated cost for demonstration: < \$1 with credits**

---

## 🧹 Cleanup

```bash
# Delete Kubernetes resources
kubectl delete namespace devtrack

# Destroy AWS infrastructure (IMPORTANT — avoids charges)
cd terraform && terraform destroy

# Remove Docker images locally
docker system prune -a
```

---

## 📚 Documentation

- [Project Journey](PROJECT_JOURNEY.md) — Step-by-step learning journal and viva preparation
- [Errors & Solutions](ERRORS_AND_SOLUTIONS.md) — Troubleshooting handbook
- [Architecture Diagrams](docs/architecture/) — Visual architecture references

---

## 🎓 Academic Information

- **Student:** Rohit | Registration No: 12322037 | Roll No: 60 | Section: K302344
- **Institution:** Department of Computer Science and Engineering, Lovely Professional University
- **Guide:** Mr. Ajay Kumar Badhan

---

## 🔮 Future Improvements

- [ ] Add user authentication (JWT/OAuth)
- [ ] Resume upload and parsing
- [ ] Email notifications for application deadlines
- [ ] AI-powered job match suggestions (hence the "AI" in DevTrack AI)
- [ ] Mobile-responsive PWA

---

*This project demonstrates end-to-end DevOps practices: containerization, infrastructure as code, Kubernetes orchestration, CI/CD automation, cloud deployment, and monitoring.*
