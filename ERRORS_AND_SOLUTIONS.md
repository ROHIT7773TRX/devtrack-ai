# ERRORS_AND_SOLUTIONS.md
# DevTrack AI — Troubleshooting Handbook

> **This document records every significant error encountered during the project.**
> For every error: what happened, why it happened, how we diagnosed it, how we fixed it, and what I learned.
> This becomes my DevOps troubleshooting handbook and viva material.

---

## HOW TO USE THIS DOCUMENT

Every time something goes wrong during this project:
1. **Don't panic** — errors are expected and normal in DevOps
2. **Read the error message carefully** — it usually tells you exactly what's wrong
3. **Document it here** using the template below
4. **Diagnose before fixing** — understand the cause, don't just try random solutions
5. **Verify the fix** — confirm it actually worked before moving on

---

## ERROR TEMPLATE

```
─────────────────────────────────────────────────────
ERROR #XX

Phase:         (Phase 1, 2, 3... which phase were we in?)
Date:          
Category:      (Git / Docker / Terraform / Kubernetes / Python / AWS / CI/CD / Testing)

Problem:
(Describe what we were trying to do when the error happened)

Actual Error Message:
(Copy the exact error text — never paraphrase error messages)

Where It Happened:
(Terminal / GitHub Actions / AWS Console / Kubernetes)

Root Cause:
(What actually caused the error, after investigation)

How We Diagnosed It:
(What steps we took to understand the problem)

Solution:
(Exactly what we changed or ran to fix it)

Commands/Changes:
(The specific commands or code changes)

Verification:
(How we confirmed the fix worked)

Lesson Learned:
(What to remember for next time)

Viva Question:
(A question about this type of error)

Viva Answer:
(The answer based on our actual experience)
─────────────────────────────────────────────────────
```

---

## ERRORS RECORDED SO FAR

---

```
─────────────────────────────────────────────────────
ERROR #01

Phase:         Phase 2 — FastAPI Backend Setup
Date:          2026-09-29
Category:      Python / Package Installation

Problem:
Installing backend dependencies on Windows using:
  pip install -r requirements.txt
The package 'psycopg2-binary==2.9.9' failed to install.

Actual Error Message:
  Error: pg_config executable not found.
  pg_config is required to build psycopg2 from source.
  Getting requirements to build wheel did not run successfully.
  exit code: 1

Where It Happened:
  Windows PowerShell terminal, inside the Python virtual environment (.venv)
  Running: .venv\Scripts\pip install -r requirements.txt

Root Cause:
  psycopg2-binary on PyPI provides pre-compiled wheels for Linux and macOS,
  but on Windows it sometimes falls back to building from source.
  Building from source requires PostgreSQL development headers (pg_config),
  which are part of a full PostgreSQL installation.
  Since we only have Docker Desktop on this machine (not a local PostgreSQL
  installation), pg_config is not in the PATH.

How We Diagnosed It:
  1. Read the error: "pg_config executable not found"
  2. Understood that pg_config is part of PostgreSQL's dev tools
  3. Realized our machine has no local PostgreSQL installed (we use Docker for that)
  4. Searched pip for Windows-compatible PostgreSQL drivers

Solution:
  For local development and testing, we don't actually need psycopg2 at all.
  Our pytest tests use SQLite (in-memory database), which doesn't need psycopg2.
  psycopg2 is only needed when the app connects to a real PostgreSQL server
  (Docker container or AWS RDS).

  Fix 1 - For local testing: Install all other packages; add aiosqlite for SQLite
  Fix 2 - For Docker: psycopg2-binary installs fine inside a Linux Docker image
  Fix 3 - Updated requirements.txt with platform-conditional install

Commands/Changes:
  # Install everything except psycopg2 for local dev
  .venv\Scripts\pip install fastapi uvicorn[standard] sqlalchemy alembic \
    pydantic pydantic-settings python-dotenv httpx pytest pytest-cov \
    prometheus-fastapi-instrumentator

  # When running in Docker (Linux), psycopg2-binary works perfectly:
  # psycopg2-binary==2.9.9  (in requirements.txt, installed in Dockerfile)

  # For tests: SQLite needs no driver — it's built into Python

Verification:
  pytest tests/unit/ -v   → All tests pass using SQLite
  Docker build → psycopg2-binary installs correctly in Linux container

Lesson Learned:
  psycopg2 on Windows requires either:
  1. A full PostgreSQL installation on the machine
  2. Skipping local install and relying on Docker/Linux for psycopg2
  The best practice for local development is to use SQLite for unit tests
  and Docker Compose for integration tests against real PostgreSQL.
  This is a common real-world pattern: "test with SQLite locally,
  run with PostgreSQL in production."

Viva Question:
  Why did your tests use SQLite instead of PostgreSQL?

Viva Answer:
  Our unit tests use SQLite (in-memory) instead of PostgreSQL for three reasons:
  1. Speed: SQLite runs in memory with no server — tests start instantly
  2. Isolation: each test gets a fresh empty database — no test pollution
  3. Portability: SQLite is built into Python — no installation required anywhere
  SQLAlchemy abstracts the database, so our models and queries work
  identically with both SQLite and PostgreSQL. In Docker and production,
  we always use real PostgreSQL.
─────────────────────────────────────────────────────
```

---

## COMMON DEVOPS ERRORS — REFERENCE SECTION

This section serves as a reference guide for common types of errors in each area.
Actual errors from our project will be added above.

---

### GIT COMMON ERRORS

**"fatal: not a git repository"**
- Cause: Running git commands outside a git repository
- Fix: `git init` or navigate to the correct folder

**"error: failed to push some refs"**
- Cause: Remote has commits your local doesn't have (someone else pushed, or you pushed from another machine)
- Fix: `git pull --rebase` then `git push`

**"Your branch is behind 'origin/main'"**
- Cause: Remote repository has newer commits
- Fix: `git pull`

**Accidentally committed a secret file:**
- Fix: `git rm --cached filename` then commit the removal, then add to .gitignore
- Warning: If already pushed to GitHub, rotate the credentials immediately — Git history is permanent

---

### DOCKER COMMON ERRORS

**"docker: Cannot connect to the Docker daemon"**
- Cause: Docker Desktop is not running
- Fix: Start Docker Desktop

**"port is already allocated"**
- Cause: Another process is using the same port
- Fix: `docker ps` to find conflicting container, `docker stop CONTAINER_ID`

**"image not found"**
- Cause: Image name is wrong, or image hasn't been pulled/built
- Fix: `docker pull IMAGE_NAME` or `docker build`

**Container exits immediately:**
- Cause: Application crash on startup (missing env vars, DB connection failure, etc.)
- Fix: `docker logs CONTAINER_ID` to see the error

---

### PYTHON / FASTAPI COMMON ERRORS

**"ModuleNotFoundError"**
- Cause: Package not installed
- Fix: `pip install PACKAGE` and add to requirements.txt

**"422 Unprocessable Entity"**
- Cause: Request body doesn't match what the API expects
- Fix: Check the request body matches the Pydantic model schema

**"sqlalchemy.exc.OperationalError: could not connect to server"**
- Cause: PostgreSQL not running or wrong connection string
- Fix: Check DATABASE_URL, ensure PostgreSQL is running

---

### TERRAFORM COMMON ERRORS

**"Error: No valid credential sources found"**
- Cause: AWS credentials not configured
- Fix: `aws configure` or set environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

**"Error: Error acquiring the state lock"**
- Cause: Previous terraform operation didn't finish cleanly (state is locked)
- Fix: `terraform force-unlock LOCK_ID` (get lock ID from error message)

**"Error: InvalidAMIID.NotFound"**
- Cause: AMI ID is region-specific; using an AMI ID from a different region
- Fix: Find the correct AMI ID for your region in AWS Console

---

### KUBERNETES COMMON ERRORS

**"ImagePullBackOff"**
- Cause: Kubernetes can't pull the Docker image (wrong image name, not pushed, or private without credentials)
- Fix: `kubectl describe pod POD_NAME` to see details; verify image name and Docker Hub login

**"CrashLoopBackOff"**
- Cause: Container starts but immediately crashes; Kubernetes keeps retrying
- Fix: `kubectl logs POD_NAME` to see application crash reason

**"Pending" pod never starts:**
- Cause: Insufficient resources on the node (CPU/RAM) — common with t2.micro
- Fix: `kubectl describe pod POD_NAME` → look at "Events" section; may need larger EC2 instance

**"connection refused" to service:**
- Cause: Service port or selector is wrong; pod not running
- Fix: `kubectl get endpoints SERVICE_NAME` to see if pods are attached

---

### AWS COMMON ERRORS

**"UnauthorizedOperation"**
- Cause: IAM user/role doesn't have permission for that action
- Fix: Add the required IAM policy to the user or role

**"VpcLimitExceeded"**
- Cause: AWS default limit is 5 VPCs per region; you've hit the limit
- Fix: Delete unused VPCs or request a limit increase

**"InsufficientInstanceCapacity"**
- Cause: AWS doesn't have available instances of that type in that availability zone
- Fix: Try a different AZ or a different instance type

---

### GITHUB ACTIONS COMMON ERRORS

**"Error: Process completed with exit code 1"**
- Cause: One of the pipeline steps failed
- Fix: Click on the failed step in GitHub Actions UI to see the exact error

**"Error: secrets.DOCKER_PASSWORD is not set"**
- Cause: GitHub Secret not configured
- Fix: Go to Repository Settings → Secrets and variables → Actions → Add secret

**"ssh: connect to host ... port 22: Connection timed out"**
- Cause: Security group doesn't allow SSH on port 22, or wrong IP
- Fix: Check Terraform security group rules for port 22 access

---

*As we encounter real errors during this project, they will be documented above with full detail.*
