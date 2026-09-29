# ============================================================
# app/backend/Dockerfile
# Docker packaging for FastAPI Backend
#
# MULTI-STAGE / SLIM PATTERN:
# Uses python:3.11-slim to minimize image size and attack surface.
# ============================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer stdout/stderr for logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building C extensions (e.g. psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY . .

# Expose FastAPI server port
EXPOSE 8000

# Health check instruction for Docker engine
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start Uvicorn ASGI server listening on 0.0.0.0 for container access
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
