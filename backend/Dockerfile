# ==============================================================================
# MasterX Backend - Production-Ready Multi-Stage Dockerfile
# ==============================================================================
# Following Big Tech Standards: Google/Meta/Amazon
# - Multi-stage builds for minimal image size
# - Layer caching optimization for fast rebuilds
# - Security hardening (non-root user, minimal attack surface)
# - Health checks for container orchestration
# - ML model pre-caching for faster startup
# ==============================================================================

# ==============================================================================
# STAGE 1: Builder - Install dependencies and build environment
# ==============================================================================
FROM python:3.11-slim as builder

LABEL maintainer="MasterX Team"
LABEL description="MasterX AI-Powered Adaptive Learning Platform - Backend Builder"

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
# Required for: PyTorch, transformers, onnxruntime, scikit-learn, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    curl \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
# This layer is cached unless requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't store pip cache (reduces image size)
# --upgrade: Ensure latest compatible versions
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download ML models during build for faster startup (optional)
# Comment out if you prefer to download on first run
# RoBERTa model for emotion detection (~500MB)
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
    AutoModel.from_pretrained('SamLowe/roberta-base-go_emotions'); \
    AutoTokenizer.from_pretrained('SamLowe/roberta-base-go_emotions')" || \
    echo "⚠️ ML model pre-download skipped (will download on first run)"

# ==============================================================================
# STAGE 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim

LABEL maintainer="MasterX Team"
LABEL description="MasterX AI-Powered Adaptive Learning Platform - Backend Runtime"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install only runtime system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy ML models from builder (if pre-downloaded)
COPY --from=builder /root/.cache /root/.cache

# Create non-root user for security (following principle of least privilege)
RUN useradd -m -u 1000 masterx && \
    chown -R masterx:masterx /app /root/.cache

# Copy application code
# Use --chown to set ownership during copy
COPY --chown=masterx:masterx . .

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/temp && \
    chown -R masterx:masterx /app/logs /app/temp

# Switch to non-root user
USER masterx

# Expose port (8001 for FastAPI)
EXPOSE 8001

# Health check for container orchestration
# Kubernetes/Docker Swarm will use this to determine container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Environment variables (can be overridden by docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    WORKERS=1

# Start command (single worker for development, override in production)
# Production should use: --workers 4 --worker-class uvicorn.workers.UvicornWorker
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
