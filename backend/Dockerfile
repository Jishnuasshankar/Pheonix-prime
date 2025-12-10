# ==============================================================================
# MasterX Backend - Production-Ready Multi-Stage Dockerfile
# ==============================================================================

# ==============================================================================
# STAGE 1: Builder - Install dependencies and build environment
# ==============================================================================
FROM python:3.11-slim AS builder

LABEL maintainer="MasterX Team"

WORKDIR /build

# Build arguments
ARG PRELOAD_ML_MODELS=true

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    curl \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install UV - ultra-fast Python package installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies using UV (10-100x faster than pip)
RUN uv pip sync --python /opt/venv/bin/python requirements.txt

# Pre-download ML models (Conditional)
RUN mkdir -p /opt/ml_cache && \
    if [ "$PRELOAD_ML_MODELS" = "true" ]; then \
        TRANSFORMERS_CACHE=/opt/ml_cache \
        HF_HOME=/opt/ml_cache \
        python -c "from transformers import AutoModel, AutoTokenizer; \
            AutoModel.from_pretrained('SamLowe/roberta-base-go_emotions'); \
            AutoTokenizer.from_pretrained('SamLowe/roberta-base-go_emotions')" && \
        echo '✅ ML models pre-loaded successfully'; \
    else \
        echo '⏭️ ML model pre-loading skipped (PRELOAD_ML_MODELS=false)'; \
    fi

# ==============================================================================
# STAGE 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim AS runtime

LABEL maintainer="MasterX Team"
LABEL description="MasterX AI-Powered Platform - Backend Runtime"
LABEL version="1.0.0"

# Build arguments for User ID consistency
ARG APP_USER=masterx
ARG APP_UID=1000
ARG APP_GID=1000

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -m -u ${APP_UID} -g ${APP_GID} -s /bin/bash ${APP_USER}

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# Copy ML models
COPY --from=builder --chown=${APP_USER}:${APP_USER} /opt/ml_cache /home/${APP_USER}/.cache

# Set path
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# ------------------------------------------------------------------------------
# 🔴 CRITICAL FIX HERE
# We explicitly create /app/logs so Docker doesn't fail trying to create 
# the mount point on a Read-Only Filesystem.
# ------------------------------------------------------------------------------
RUN mkdir -p /app/temp /app/data /app/logs && \
    chown -R ${APP_USER}:${APP_USER} /app && \
    chmod -R 755 /app/temp /app/data /app/logs

# Cleanup
RUN rm -rf /app/.git /app/.gitignore /app/__pycache__ \
    /app/*.md /app/.env* /app/Dockerfile* /app/docker-compose* \
    /app/.dockerignore /app/tests /app/.pytest_cache 2>/dev/null || true

# Switch to non-root user
USER ${APP_USER}

# Expose port
EXPOSE 8001

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LOG_LEVEL=INFO \
    WORKERS=4 \
    MAX_WORKERS=8 \
    TIMEOUT=120 \
    GRACEFUL_TIMEOUT=30 \
    KEEP_ALIVE=5 \
    HOST=0.0.0.0 \
    PORT=8001 \
    TRANSFORMERS_CACHE=/home/masterx/.cache \
    HF_HOME=/home/masterx/.cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/api/health || exit 1

# Entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]

# Command
CMD ["sh", "-c", "uvicorn server:app --host ${HOST} --port ${PORT} --workers ${WORKERS} --timeout-keep-alive ${KEEP_ALIVE} --limit-concurrency 100 --limit-max-requests 10000"]