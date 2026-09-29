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

*No errors recorded yet. This document will grow as we encounter and solve issues during development.*

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
