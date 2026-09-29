# ============================================================
# main.py
# FastAPI application entry point.
#
# WHAT THIS FILE DOES:
#   - Creates the FastAPI application instance
#   - Configures CORS (allows the React frontend to call the API)
#   - Creates database tables on startup (if they don't exist)
#   - Registers all routers (applications, dashboard)
#   - Exposes a /health endpoint for Kubernetes liveness probes
#   - Exposes a /metrics endpoint for Prometheus monitoring
#
# HOW TO RUN:
#   uvicorn main:app --reload --host 0.0.0.0 --port 8000
#
#   uvicorn       → ASGI server (runs FastAPI apps)
#   main          → the file (main.py)
#   app           → the FastAPI() instance inside main.py
#   --reload      → auto-restart on code changes (dev only)
#   --host 0.0.0.0→ listen on all interfaces (needed for Docker)
#   --port 8000   → listen on port 8000
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine, get_db
from routers import applications, dashboard

# Database tables are created in the startup event handler below.
# This ensures they exist before the first request is served.

# ──────────────────────────────────────────────
# CREATE FASTAPI APPLICATION
# ──────────────────────────────────────────────
app = FastAPI(
    title="DevTrack AI API",
    description="""
    ## DevTrack AI — Job Application & Career Management Platform

    A REST API for managing job applications, tracking interview rounds,
    and visualizing career progress.

    ### Features
    * **Applications** — Full CRUD for job applications
    * **Interview Rounds** — Track multiple rounds per application
    * **Dashboard** — Aggregated analytics and statistics
    * **Health** — Kubernetes liveness/readiness probe endpoint
    * **Metrics** — Prometheus metrics endpoint

    ### Academic Project
    Developed as part of a DevOps academic project demonstrating:
    Docker, Kubernetes, Terraform, GitHub Actions, and AWS.
    """,
    version="1.0.0",
    contact={
        "name": "Rohit",
        "url":  "https://github.com/YOUR_USERNAME/devtrack-ai",
    },
    license_info={
        "name": "MIT",
    },
)


# ──────────────────────────────────────────────
# CORS CONFIGURATION
# ──────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
#
# WHY IS CORS NEEDED?
# Browsers block JavaScript from calling APIs on different domains
# by default (security feature). Our React app runs on localhost:3000
# but calls the API on localhost:8000 — that's a different "origin".
#
# We must tell the browser: "yes, it's safe to call this API from
# the React app's origin."
#
# In production, replace "*" with the actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React dev server
        "http://localhost:80",      # React production build (nginx)
        "*",                        # Allow all for demo — restrict in real production
    ],
    allow_credentials=True,
    allow_methods=["*"],            # Allow GET, POST, PATCH, DELETE, OPTIONS
    allow_headers=["*"],            # Allow all headers
)


# ──────────────────────────────────────────────
# PROMETHEUS METRICS
# ──────────────────────────────────────────────
# This automatically instruments all FastAPI endpoints and exposes
# metrics at /metrics that Prometheus can scrape.
# Metrics include: request count, latency, status codes per endpoint.
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
except ImportError:
    # Prometheus instrumentation is optional — app still works without it
    pass


# ──────────────────────────────────────────────
# INCLUDE ROUTERS
# ──────────────────────────────────────────────
# Each router handles a different section of the API.
# include_router() adds all the routes from the router to the app.
app.include_router(applications.router)
app.include_router(dashboard.router)


# ──────────────────────────────────────────────
# ROOT & HEALTH ENDPOINTS
# ──────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint — confirms the API is running.
    Not a health check — use /health for that.
    """
    return {
        "message": "Welcome to DevTrack AI API",
        "docs":    "/docs",
        "health":  "/health",
        "metrics": "/metrics",
    }


@app.get("/health", tags=["Health"], response_model=dict)
def health_check():
    """
    Health check endpoint.

    WHY DO WE NEED THIS?
    Kubernetes uses this endpoint for:
    - Liveness Probe:  "Is the container alive?" → if this fails, K8s restarts the pod
    - Readiness Probe: "Is the container ready to serve traffic?" → if this fails, K8s
                       removes the pod from the load balancer until it recovers

    Without health checks, Kubernetes can't detect when your app has crashed
    and won't restart it automatically.

    Returns 200 OK when the application is healthy.
    """
    return {
        "status":  "healthy",
        "service": "devtrack-ai-backend",
        "version": "1.0.0",
    }


# ──────────────────────────────────────────────
# STARTUP EVENT (informational)
# ──────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """
    Runs once when the application starts.
    Creates database tables and logs startup info.
    """
    # Create all tables if they don't exist yet
    # This is safe to run repeatedly — SQLAlchemy skips tables that already exist
    Base.metadata.create_all(bind=engine)

    print("=" * 60)
    print("  DevTrack AI Backend Starting Up")
    print("  API Documentation: http://localhost:8000/docs")
    print("  Health Check:      http://localhost:8000/health")
    print("  Metrics:           http://localhost:8000/metrics")
    print("=" * 60)

