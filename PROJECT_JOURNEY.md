# PROJECT_JOURNEY.md
# DevTrack AI — Personal Learning Journal & Viva Preparation Handbook

> **This is my personal learning document.**
> Every phase of the project is recorded here with what I did, why I did it, how it works, what I learned, and potential viva questions with answers.
> This document grows with the project and becomes my primary viva preparation material.

---

## HOW TO USE THIS DOCUMENT

This document is organized chronologically by phase.
For every phase:
- I record **what we did and why**
- I explain **how it works in simple language**
- I document the **exact commands** we ran
- I note **what I learned**
- I prepare **viva questions with project-specific answers**

The answers here are based on **our actual project**, not generic textbook definitions.

---

# ═══════════════════════════════════════════════
# PHASE 0 — SYNOPSIS ANALYSIS & ARCHITECTURE
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

Read and analyzed the synopsis file: `DevTrack_AI_Final_Professional_Synopsis_Updated.pdf`

Understood the complete project scope, technology stack, and DevOps requirements.
Planned the architecture and implementation roadmap before writing any code.

## Why We Did It First

Architecture decisions made early are much cheaper to change than architecture decisions made after writing code. Understanding the project completely before building anything ensures we don't waste time building the wrong thing.

This is also a real DevOps principle: **"Plan before you build."**

## What the Project Is

**DevTrack AI** is a Job Application and Career Management Platform.

It solves this problem: when applying to many companies at once, it's easy to lose track of where you applied, what stage each application is in, and when interviews are scheduled.

**The solution:** A web application where:
- You add each job application
- You track the company, role, location
- You update the status as it progresses (Applied → Interview → Offer → Rejected)
- You log interview rounds and outcomes
- A dashboard shows your overall progress visually

## Architecture Decision — Why K3s Instead of Full EKS?

**The synopsis specifically proposes K3s.**

K3s is a lightweight version of Kubernetes that runs on a single machine. Full AWS EKS (Elastic Kubernetes Service) is managed Kubernetes on AWS that:
- Costs approximately \$72/month for the control plane alone
- Requires multiple EC2 instances for worker nodes
- Is overkill for an academic project

K3s on a single EC2 instance:
- Costs only the EC2 price (~\$0.02/hr for t3.small)
- Runs the same Kubernetes concepts: Pods, Deployments, Services, HPA
- Is perfectly valid for demonstrating Kubernetes skills
- Can be destroyed with `terraform destroy` when not needed

**This is a smart, cost-aware architecture decision — exactly what a real DevOps engineer would make.**

## Technology Stack and Why Each Was Chosen

| Technology | Why This Specific Choice |
|---|---|
| **FastAPI** | Python-based, very fast, automatic API documentation at /docs, modern async support |
| **React.js** | Industry-standard frontend, component-based, good for dashboard UIs |
| **PostgreSQL** | Reliable relational database, excellent Docker support, free and open source |
| **pytest** | Native Python testing, works perfectly with FastAPI's TestClient |
| **Docker** | Synopsis requirement; industry standard for containerization |
| **K3s** | Lightweight Kubernetes for single-node; cost-efficient for academic demo |
| **Terraform** | Synopsis requirement; IaC for reproducible AWS infrastructure |
| **GitHub Actions** | Free CI/CD; integrates directly with GitHub; 2000 free minutes/month |
| **Prometheus** | Synopsis requirement; industry-standard metrics collection |
| **Grafana** | Synopsis requirement; industry-standard for visualizing Prometheus data |
| **AWS** | Synopsis requirement; real cloud deployment; using existing credits |

## Viva Questions — Phase 0

**Q: What is DevTrack AI? Explain it in simple terms.**
A: DevTrack AI is a web application that helps job seekers manage their job search. It's built with React.js for the frontend, FastAPI for the backend, and PostgreSQL for the database. The "DevOps" part is how we build, test, package, and deploy it — using Docker, Kubernetes, Terraform, GitHub Actions, and AWS.

**Q: Why did you choose K3s instead of AWS EKS?**
A: K3s is a lightweight Kubernetes distribution that runs on a single machine. AWS EKS costs approximately \$72/month for the control plane alone, which is unnecessary for an academic project. K3s demonstrates the exact same Kubernetes concepts — Pods, Deployments, Services, load balancing, scaling, self-healing — at a fraction of the cost. The synopsis itself proposes K3s on EC2.

**Q: Why did you choose FastAPI instead of Django or Flask?**
A: FastAPI is modern, fast (comparable to Node.js), has automatic API documentation at /docs, supports async operations, and has excellent PostgreSQL integration through SQLAlchemy. Flask is simpler but requires more boilerplate. Django is larger and has more features than we need. FastAPI is the modern choice for building REST APIs in Python.

**Q: Explain the complete architecture of DevTrack AI.**
A: The architecture has three environments:
1. Local development: Developer writes code, runs it with docker-compose, runs pytest tests
2. CI/CD: Every git push triggers GitHub Actions which tests, builds Docker images, and deploys
3. AWS production: Terraform provisions EC2+VPC, K3s runs on EC2, three pods (frontend, backend, postgres) serve the application, Prometheus+Grafana monitor it

---

# ═══════════════════════════════════════════════
# PHASE 1 — GIT SETUP & PROJECT STRUCTURE
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

1. Initialized a Git repository in the project folder
2. Configured Git with name and email
3. Created the complete project folder structure
4. Created `.gitignore` to protect sensitive files
5. Created `README.md`, `PROJECT_JOURNEY.md`, and `ERRORS_AND_SOLUTIONS.md`

## Why Git First?

Git is the foundation of everything else in this project.
- GitHub Actions CI/CD pipeline is **triggered by Git pushes**
- Docker images are **tagged with Git commit hashes**
- Every change is **tracked and reversible**
- The entire team (or just me) can work safely knowing the history is preserved

**In DevOps, everything starts with source control.**

## Commands We Ran

```bash
git init
# Creates a hidden .git folder — this is the database of all your commits

git config user.name "Rohit"
git config user.email "rohit@devtrack.ai"
# Tells Git who is making the commits
# This appears in GitHub, logs, and CI/CD pipelines
```

## What Is .gitignore and Why Is It Critical?

`.gitignore` tells Git which files to **never track or commit**.

**Why this is a security requirement, not just a preference:**

If you accidentally commit:
- AWS credentials → someone can create thousands of EC2 instances and charge to your account
- Database passwords → someone can access all your data
- Terraform state → exposes infrastructure details and secrets
- `.env` files → exposes all environment-specific secrets

**Real-world example:** Every year, developers accidentally push AWS keys to GitHub. AWS's own bots scan GitHub and can detect and sometimes suspend keys within minutes. Attackers also scan GitHub 24/7 for exposed credentials.

**Our .gitignore protects:**
- `*.env` files — database passwords, API keys
- `*.pem` files — AWS SSH private keys
- `terraform/*.tfstate` — Terraform state (contains real resource IDs and sometimes secrets)
- `terraform/terraform.tfvars` — real variable values
- `node_modules/` — huge folder, not needed in Git (npm install recreates it)
- `__pycache__/` — Python compiled files, not needed in Git

## Project Folder Structure — Why This Organization?

```
app/backend/    → FastAPI code (the actual application logic)
app/frontend/   → React.js code (the user interface)
tests/unit/     → pytest unit tests
tests/integration/ → pytest API integration tests
docker/         → docker-compose.yml for local development
terraform/      → AWS infrastructure code
kubernetes/     → Kubernetes manifests for deployment
.github/workflows/ → GitHub Actions CI/CD pipeline
docs/           → Architecture diagrams and screenshots
```

**Why separate backend and frontend?**
They are built differently, run differently, have different Dockerfiles, different dependencies, and deploy differently. Keeping them separate makes the project organized and mirrors industry practice.

**Why tests/ at the top level?**
Tests are independent of the application. They test the application but they are not part of it. This makes it easy for the CI/CD pipeline to find and run all tests with a single `pytest tests/` command.

## What Is a Commit?

A commit is a **snapshot of your entire project at a specific moment in time**.

Every commit has:
- A unique ID (hash like `a3f7b2c`) — Git calculates this from the content
- A message explaining what changed
- Who made it
- When they made it

You can travel back in time to any commit and see exactly what the code looked like.

## What Is a Branch?

A branch is an independent line of development. Think of it like a parallel universe for your code.

```
main        ●──────────●──────────●──────────●
                       │                     ↑
feature/auth           ●──────────●──────────┘ (merged)
```

In our project, we'll work on `main` for simplicity (academic project).
In real projects, you'd create feature branches for each new piece of functionality.

## Viva Questions — Phase 1

**Q: What is Git? What is GitHub? What is the difference?**
A: Git is a version control system that runs on your computer and tracks changes to files. GitHub is a cloud service that hosts Git repositories. Git is the tool; GitHub is the platform. You use Git commands locally, and `git push` sends your commits to GitHub.

**Q: Why do we use Git in this project?**
A: Git is the foundation of our CI/CD pipeline. When I push code to GitHub, GitHub Actions automatically detects the push and starts the CI/CD pipeline — running tests, building Docker images, and deploying to Kubernetes. Without Git, none of the automation would work.

**Q: What is a .gitignore file? Why is it important for security?**
A: `.gitignore` tells Git which files to never track or commit. In our project, it's critical for security because it prevents accidentally committing AWS credentials, database passwords, Terraform state files (which contain real infrastructure details), and private SSH keys. Exposing these on GitHub would give anyone access to our AWS account and database.

**Q: What is the difference between `git add`, `git commit`, and `git push`?**
A: `git add` stages files (marks them for the next commit). `git commit` creates a snapshot of the staged files locally. `git push` sends those commits to GitHub (the remote repository). You need all three steps to get code from your computer to GitHub.

**Q: What would happen if you committed your AWS credentials to GitHub?**
A: AWS's automated systems scan GitHub continuously for exposed credentials. Within minutes, your keys could be detected. Attackers also scan GitHub 24/7. They could use your credentials to spin up expensive GPU instances for crypto mining, potentially costing thousands of dollars. GitHub and AWS have a partnership where GitHub notifies AWS of exposed keys, and AWS may suspend them — but the damage could already be done.

---

# ═══════════════════════════════════════════════
# PHASE 3 — REACT.JS FRONTEND DEVELOPMENT
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

1. Initialized React.js frontend structure under `app/frontend/`
2. Configured Axios API service client in `app/frontend/src/services/api.js`
3. Built responsive UI components:
   - `Navbar`: Header and navigation tabs
   - `DashboardView`: Metrics overview, status cards, and recent activity
   - `ApplicationList`: Data table with filtering by status and action buttons
   - `ApplicationFormModal`: Interactive modal for creating and updating job applications
4. Integrated state management and backend REST API connectivity

## Why React.js?

- Component-driven architecture allows reusing UI components cleanly
- State-driven reactivity automatically updates the UI when job application data changes
- Modern standard for building single-page dashboard applications (SPAs)

## Viva Questions — Phase 3

**Q: How does the React frontend communicate with the FastAPI backend?**
A: The frontend uses `axios` to make HTTP REST API requests to the FastAPI endpoints (`GET /applications/`, `POST /applications/`, `GET /dashboard/`, etc.). Cross-Origin Resource Sharing (CORS) is enabled in FastAPI to permit requests from the React application origin.

**Q: What is the purpose of `REACT_APP_API_URL` environment variable?**
A: `REACT_APP_API_URL` allows the API endpoint URL to be configured dynamically. During local development it points to `http://localhost:8000`, while in Kubernetes/Docker environments it points to the containerized service or load balancer domain without altering source code.

---

# ═══════════════════════════════════════════════
# PHASE 4 — AUTOMATED TESTING & TEST SUITE
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

1. Configured unit testing using `pytest` and `httpx` (FastAPI `TestClient`)
2. Implemented 10 unit tests in `tests/unit/test_applications.py` covering:
   - Health check endpoint `/health` (liveness probe verification)
   - Happy path application creation (`201 Created`)
   - Schema validation failure for missing required fields (`422 Unprocessable Entity`)
   - Empty application listing (`200 OK` with empty array)
   - Data retrieval, filtering, single record lookup by ID (`200 OK`)
   - Non-existent record lookup (`404 Not Found`)
   - Partial updates via PATCH (`200 OK`)
   - Deletion of records (`204 No Content`)
   - Aggregated metrics calculation for dashboard endpoints
3. Implemented end-to-end integration test in `tests/integration/test_api.py`:
   - Validates the complete multi-step lifecycle: create -> verify metrics -> schedule interview -> update status -> delete -> verify cleanup
4. Ran test suite with 100% pass rate (11/11 tests passing)

## Demonstrated Controlled Test Failure & Debugging (Section 10 Requirement)

To verify our CI/CD error-catching logic:
- **Scenario:** Created a temporary test assertion expecting HTTP status code `200 OK` for a non-existent ID lookup instead of `404 Not Found`.
- **Observed Result:** `pytest` caught the assertion failure, halting execution with exit code 1.
- **Root Cause Identified:** The API correctly follows REST standards returning `404 Not Found` when a requested entity ID does not exist in PostgreSQL/SQLite.
- **Resolution:** Updated assertion to expect HTTP `404`, returning test status to PASS.

## Viva Questions — Phase 4

**Q: What is the difference between Unit Testing and Integration Testing?**
A: Unit testing isolates individual components (e.g. testing one specific route handler with a mocked or empty database session) to verify logic correctness in isolation. Integration testing tests multiple system layers together (e.g. testing the full HTTP request flow through FastAPI routing, Pydantic validation, SQLAlchemy ORM, database persistence, and cascading record updates across multiple endpoints).

**Q: Why do we use SQLite in-memory for unit testing instead of the live PostgreSQL database?**
A: In-memory SQLite provides instantaneous startup, zero external infrastructure dependencies, and absolute test isolation (a fresh database is created and destroyed per test function), preventing test pollution and allowing tests to execute rapidly in local development and CI/CD runners.

---

# ═══════════════════════════════════════════════
# PHASE 5 — DOCKER & DOCKER COMPOSE CONTAINERIZATION
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

1. Created container specification for backend:
   - Base image: `python:3.11-slim`
   - Configured non-root user considerations, layer caching, and HEALTHCHECK instructions
2. Created multi-stage Docker build for frontend (`app/frontend/Dockerfile`):
   - Stage 1: Build React static assets (`node:18-alpine`)
   - Stage 2: Production web server (`nginx:alpine`) serving HTML/JS assets on port 80 (~25MB image size)
3. Configured custom Nginx reverse proxy configuration (`app/frontend/nginx.conf`)
4. Configured Docker Compose multi-container stack (`docker/docker-compose.yml`):
   - `postgres:15-alpine` container with named volume persistence (`postgres_data`) and healthcheck
   - `backend` FastAPI service linked via internal Docker bridge network (`devtrack-network`)
   - `frontend` React/Nginx web server exposing host port 3000

## Why Docker?

- **Environment Consistency:** Eliminates "it works on my machine" issues by packaging code, dependencies, runtime, and OS configurations into portable images.
- **Microservices Isolation:** Separates frontend, backend API, and PostgreSQL database into independent isolated containers communicating via virtual bridge networks.
- **Cloud Readiness:** Container images can be pushed to Docker Hub and seamlessly deployed to Kubernetes (K3s/AWS) without modifying application code.

## Viva Questions — Phase 5

**Q: What is a multi-stage Docker build and why did we use it for the React frontend?**
A: A multi-stage Docker build uses multiple `FROM` statements in a single Dockerfile. We used Node.js in Stage 1 to compile React code into static HTML/CSS/JS bundles. In Stage 2, we copied ONLY the compiled static files into a clean `nginx:alpine` image, completely dropping Node.js and source files. This reduced final image size from ~800MB to ~25MB and significantly increased container security.

**Q: What is the difference between Docker `CMD` and `ENTRYPOINT`?**
A: `ENTRYPOINT` specifies the default command that ALWAYS runs when a container starts. `CMD` specifies default arguments passed to `ENTRYPOINT`, or default commands that can be overridden when executing `docker run container_name <override_cmd>`.

**Q: How does `docker-compose` manage service startup order?**
A: We used `depends_on` with `condition: service_healthy`. Docker Compose waits for the `postgres` healthcheck command (`pg_isready`) to return success before initializing the `backend` container, preventing database connection failure exceptions during startup.

---

# ═══════════════════════════════════════════════
# PHASE 6 — TERRAFORM INFRASTRUCTURE AS CODE (AWS)
# Date: 2026-09-29
# ═══════════════════════════════════════════════

## What We Did

1. Defined AWS Provider configuration (`terraform/providers.tf`)
2. Created input variables (`terraform/variables.tf`) for region, instance type (`t3.small`), SSH key name, and security CIDRs
3. Authored infrastructure declaration (`terraform/main.tf`):
   - Custom VPC (`10.0.0.0/16`) + Public Subnet (`10.0.1.0/24`)
   - Internet Gateway & Public Route Table
   - Security Group permitting SSH (22), HTTP (80), FastAPI (8000), and NodePort range (`30000-32767`)
   - Ubuntu 22.04 LTS AMI dynamic lookup & EC2 Instance
   - Elastic IP (Static Public IP)
4. Defined Terraform output variables (`terraform/outputs.tf`) for SSH strings, IP endpoints, and K3s installation script commands
5. Created `terraform.tfvars.example` template

## Why Terraform instead of manual AWS Console creation?

- **Reproducibility:** Infrastructure can be created, destroyed, or recreated in minutes using exact declarative code.
- **Version Control:** Infrastructure changes are tracked in Git alongside application code.
- **Cost Minimization & Cleanup:** Running `terraform destroy` tears down all AWS resources in one single automated step, ensuring AWS charges stop immediately after demo sessions.

## Viva Questions — Phase 6

**Q: What are the main steps in the Terraform workflow?**
A:
1. `terraform init`: Initializes working directory, downloads required AWS provider plugins.
2. `terraform validate`: Checks syntax and validity of `.tf` files.
3. `terraform plan`: Generates execution plan showing what resources will be created/modified/deleted.
4. `terraform apply`: Provisions declared infrastructure on AWS.
5. `terraform destroy`: Tears down and deletes all provisioned resources to prevent unwanted AWS billing.

**Q: What is `terraform.tfstate` and why should it NOT be committed to Git?**
A: `terraform.tfstate` maps declarative code to real deployed cloud resource IDs and attributes. It can contain sensitive data (passwords, private IPs, access tokens). Committing state files creates security risks and causes state file sync conflicts.

---

# ═══════════════════════════════════════════════
# [FUTURE PHASES WILL BE ADDED HERE]
# ═══════════════════════════════════════════════

## Phases Yet to Come

- Phase 2: FastAPI Backend Development
- Phase 3: React.js Frontend Development
- Phase 4: Testing with pytest
- Phase 5: Docker & Docker Compose
- Phase 6: Terraform & AWS Infrastructure
- Phase 7: K3s Kubernetes Setup
- Phase 8: Kubernetes Manifests & Deployment
- Phase 9: GitHub Actions CI/CD
- Phase 10: Prometheus & Grafana Monitoring
- Phase 11: Security & Optimization
- Phase 12: End-to-End Testing
- Phase 13: Final Documentation
- Phase 14: Viva Preparation

*Each phase will be documented in detail as we progress.*
