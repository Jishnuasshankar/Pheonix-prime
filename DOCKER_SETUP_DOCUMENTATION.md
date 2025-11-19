# 🐳 MASTERX - ENTERPRISE-GRADE DOCKER SETUP DOCUMENTATION

**Version:** 1.0.0  
**Last Updated:** November 19, 2025  
**Status:** Production-Ready  
**Approach:** Google/Meta/Amazon-Level Infrastructure

---

## 📑 TABLE OF CONTENTS

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure Analysis](#project-structure-analysis)
5. [Docker Strategy](#docker-strategy)
6. [Step-by-Step Setup](#step-by-step-setup)
7. [Configuration Management](#configuration-management)
8. [Service Orchestration](#service-orchestration)
9. [Network Architecture](#network-architecture)
10. [Volume Management](#volume-management)
11. [Health Checks & Monitoring](#health-checks--monitoring)
12. [Security Best Practices](#security-best-practices)
13. [Production Deployment](#production-deployment)
14. [Troubleshooting Guide](#troubleshooting-guide)
15. [Maintenance & Updates](#maintenance--updates)

---

## 1. INTRODUCTION

### 1.1 Overview
MasterX is a production-ready emotion-aware adaptive learning platform featuring:
- **Backend:** FastAPI 0.110.1 + MongoDB + PyTorch 2.8.0
- **Frontend:** React 18.3.0 + TypeScript + Vite 7.2.2
- **ML Components:** Emotion detection (RoBERTa), Voice AI, Real-time collaboration
- **Architecture:** Microservices with async communication

### 1.2 Why Docker?
✅ **Consistency:** Same environment across dev/staging/prod  
✅ **Isolation:** Services run in isolated containers  
✅ **Scalability:** Easy horizontal scaling  
✅ **Portability:** Deploy anywhere Docker runs  
✅ **Resource Management:** Efficient CPU/memory allocation

### 1.3 Docker Strategy Overview
```
MasterX Docker Architecture
├── Multi-stage builds (minimize image size)
├── Layer caching optimization (fast rebuilds)
├── Health checks (automatic recovery)
├── Volume management (data persistence)
├── Network isolation (security)
└── Orchestration (Docker Compose)
```

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      NGINX (Reverse Proxy)                  │
│                     Port 80/443 → 3000/8001                 │
└───────────────────┬─────────────────────┬───────────────────┘
                    │                     │
        ┌───────────▼──────────┐  ┌──────▼────────────┐
        │   Frontend Container │  │ Backend Container │
        │   React + Vite       │  │ FastAPI + PyTorch │
        │   Port: 3000         │  │ Port: 8001        │
        └───────────┬──────────┘  └──────┬────────────┘
                    │                     │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  MongoDB Container │
                    │  Port: 27017       │
                    └────────────────────┘
```

### 2.2 Service Breakdown

| Service | Container | Base Image | Purpose | Port |
|---------|-----------|------------|---------|------|
| **Backend** | masterx-backend | python:3.11-slim | FastAPI API + ML models | 8001 |
| **Frontend** | masterx-frontend | node:20-alpine | React UI + Vite dev server | 3000 |
| **Database** | masterx-mongodb | mongo:7.0 | Data persistence | 27017 |
| **Reverse Proxy** | masterx-nginx | nginx:alpine | Load balancing, SSL | 80/443 |

### 2.3 Component Dependencies
```
Backend Dependencies (requirements.txt):
├── FastAPI 0.110.1 (async web framework)
├── PyTorch 2.8.0 (ML models)
├── Transformers 4.56.2 (NLP models)
├── Motor 3.3.1 (async MongoDB driver)
├── ONNX Runtime 1.20.1 (optimized inference)
├── Sentence-transformers 5.1.1 (embeddings)
├── scikit-learn 1.7.2 (ML algorithms)
├── ElevenLabs 2.16.0 (voice synthesis)
├── Groq 0.31.1 (LLM integration)
├── Google GenAI 1.38.0 (Gemini integration)
└── 140+ other packages

Frontend Dependencies (package.json):
├── React 18.3.0
├── TypeScript 5.4.0
├── Vite 7.2.2
├── TailwindCSS 3.4.1
├── React Router DOM 6.22.0
├── Socket.io-client 4.7.0
├── React Query 5.28.0
├── Zustand 4.5.2
└── 60+ other packages
```

---

## 3. PREREQUISITES

### 3.1 Required Software
```bash
# 1. Docker Engine
# Minimum version: 24.0.0+
docker --version
# Expected: Docker version 24.0.0 or higher

# 2. Docker Compose
# Minimum version: 2.20.0+
docker-compose --version
# Expected: Docker Compose version v2.20.0 or higher

# 3. Git (for cloning repository)
git --version
# Expected: git version 2.30.0 or higher
```

### 3.2 System Requirements

**Development Environment:**
- **CPU:** 4 cores minimum (8 cores recommended)
- **RAM:** 16GB minimum (32GB recommended for ML models)
- **Disk:** 50GB free space minimum
- **OS:** Linux (Ubuntu 22.04+), macOS (12.0+), Windows 10/11 with WSL2

**Production Environment:**
- **CPU:** 8+ cores (16+ for high traffic)
- **RAM:** 32GB minimum (64GB+ recommended)
- **Disk:** 200GB+ SSD storage
- **Network:** 1Gbps bandwidth minimum

### 3.3 Docker Installation

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker run hello-world
```

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications
# Verify installation
docker run hello-world
```

**Windows (WSL2):**
```bash
# 1. Install WSL2
wsl --install

# 2. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 3. Enable WSL2 integration in Docker Desktop settings
# 4. Verify in WSL2 terminal
docker run hello-world
```

---

## 4. PROJECT STRUCTURE ANALYSIS

### 4.1 Complete Directory Tree
```
/app/
├── backend/                          # Python FastAPI backend
│   ├── core/                         # Core business logic
│   │   ├── __init__.py
│   │   ├── models.py                 # Pydantic models (379 lines)
│   │   ├── engine.py                 # Main orchestrator (568 lines)
│   │   ├── ai_providers.py           # Multi-AI integration (546 lines)
│   │   ├── context_manager.py        # Conversation memory (659 lines)
│   │   ├── adaptive_learning.py      # Difficulty adaptation (702 lines)
│   │   ├── external_benchmarks.py    # Benchmarking APIs (602 lines)
│   │   └── dynamic_pricing.py        # Cost optimization
│   ├── services/                     # Feature services
│   │   ├── emotion/                  # Emotion detection system
│   │   │   ├── emotion_engine.py     # Main emotion orchestrator (1,178 lines)
│   │   │   ├── emotion_transformer.py # RoBERTa/BERT models (868 lines)
│   │   │   ├── emotion_core.py       # Core data structures (726 lines)
│   │   │   ├── emotion_cache.py      # Multi-level caching (682 lines)
│   │   │   ├── batch_optimizer.py    # Dynamic batching (550 lines)
│   │   │   ├── emotion_profiler.py   # Performance monitoring (652 lines)
│   │   │   └── onnx_optimizer.py     # ONNX Runtime optimization (650 lines)
│   │   ├── gamification.py           # XP, achievements, leaderboards (976 lines)
│   │   ├── spaced_repetition.py      # SM-2 algorithm (906 lines)
│   │   ├── analytics.py              # Analytics engine (642 lines)
│   │   ├── personalization.py        # User personalization (611 lines)
│   │   ├── content_delivery.py       # Content recommendations (605 lines)
│   │   ├── voice_interaction.py      # Voice AI (866 lines)
│   │   ├── collaboration.py          # Real-time collaboration (1,175 lines)
│   │   ├── rag_engine.py             # RAG system (web search)
│   │   ├── websocket_service.py      # WebSocket management
│   │   └── ml_question_generator.py  # ML-based question generation
│   ├── middleware/                   # Request processing
│   │   ├── auth.py                   # JWT authentication
│   │   ├── simple_rate_limit.py      # Rate limiting
│   │   ├── brute_force.py            # Brute force protection
│   │   └── security_headers.py       # Security headers
│   ├── utils/                        # Utility modules
│   │   ├── database.py               # MongoDB operations (717 lines)
│   │   ├── cost_tracker.py           # Cost monitoring (240 lines)
│   │   ├── cost_enforcer.py          # Budget enforcement (868 lines)
│   │   ├── health_monitor.py         # System health (798 lines)
│   │   ├── request_logger.py         # Structured logging (527 lines)
│   │   ├── graceful_shutdown.py      # Zero-downtime deploys (495 lines)
│   │   ├── rate_limiter.py           # ML-based rate limiting
│   │   ├── validators.py             # Input validation
│   │   ├── security.py               # Security utilities
│   │   ├── monitoring.py             # Performance monitoring
│   │   ├── helpers.py                # Helper functions
│   │   ├── errors.py                 # Custom exceptions
│   │   └── logging_config.py         # Logging setup
│   ├── optimization/                 # Performance optimization
│   │   ├── caching.py                # Multi-level caching (481 lines)
│   │   └── performance.py            # Performance monitoring (390 lines)
│   ├── config/                       # Configuration management
│   │   ├── settings.py               # Pydantic settings (200+ lines)
│   │   └── __init__.py
│   ├── tests/                        # Test suite
│   │   ├── test_websocket_service.py
│   │   └── test_websocket_integration.py
│   ├── server.py                     # FastAPI application (750+ lines)
│   ├── requirements.txt              # Python dependencies (150 packages)
│   ├── .env                          # Environment variables
│   └── __init__.py
│
├── frontend/                         # React TypeScript frontend
│   ├── src/                          # Source code
│   │   ├── components/               # React components
│   │   │   ├── auth/                 # Authentication components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── SignupForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── chat/                 # Chat interface
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── EmotionWidget.tsx
│   │   │   ├── emotion/              # Emotion visualization
│   │   │   │   ├── EmotionIndicator.tsx
│   │   │   │   └── EmotionHistory.tsx
│   │   │   ├── layout/               # Layout components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── analytics/            # Analytics dashboards
│   │   │   ├── gamification/         # Gamification UI
│   │   │   └── common/               # Reusable components
│   │   ├── pages/                    # Page components
│   │   │   ├── Landing.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MainApp.tsx
│   │   │   └── Settings.tsx
│   │   ├── store/                    # Zustand state management
│   │   │   ├── authStore.ts          # Authentication state
│   │   │   ├── chatStore.ts          # Chat state
│   │   │   ├── emotionStore.ts       # Emotion tracking
│   │   │   ├── uiStore.ts            # UI state
│   │   │   └── analyticsStore.ts     # Analytics data
│   │   ├── services/                 # API services
│   │   │   ├── api/                  # API clients
│   │   │   ├── websocket/            # WebSocket client
│   │   │   └── storage/              # Local storage
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useChat.ts
│   │   │   ├── useEmotion.ts
│   │   │   └── useWebSocket.ts
│   │   ├── config/                   # Configuration
│   │   │   ├── constants.ts
│   │   │   ├── api.config.ts
│   │   │   ├── theme.config.ts
│   │   │   └── features.config.ts
│   │   ├── types/                    # TypeScript types
│   │   │   ├── user.types.ts
│   │   │   ├── api.types.ts
│   │   │   ├── emotion.types.ts
│   │   │   └── chat.types.ts
│   │   ├── utils/                    # Utility functions
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── helpers.ts
│   │   ├── App.tsx                   # Main app component
│   │   ├── index.tsx                 # Entry point
│   │   └── index.css                 # Global styles
│   ├── public/                       # Static assets
│   │   ├── index.html
│   │   └── favicon.svg
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── vite.config.ts                # Vite configuration
│   ├── tailwind.config.js            # TailwindCSS config
│   ├── postcss.config.js             # PostCSS config
│   ├── .env                          # Environment variables
│   └── yarn.lock                     # Dependency lock file
│
├── .git/                             # Git repository
├── .gitignore                        # Git ignore rules
├── README.md                         # Project documentation
└── [Multiple documentation files].md # 25+ documentation files

Total Statistics:
- Backend: 56 Python files (~31,600 lines of code)
- Frontend: 103 TypeScript/TSX files
- Dependencies: 150+ Python packages, 60+ npm packages
- Documentation: 25+ comprehensive markdown files
```

### 4.2 Critical Files for Docker

**Backend:**
- `requirements.txt` - Python dependencies
- `server.py` - FastAPI entry point
- `.env` - Environment configuration
- `config/settings.py` - Application settings

**Frontend:**
- `package.json` - Node.js dependencies
- `vite.config.ts` - Build configuration
- `.env` - Environment variables
- `index.html` - HTML entry point

### 4.3 Environment Variables Analysis

**Backend (.env):**
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=masterx

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,...

# AI Providers
GROQ_API_KEY=gsk_yrVyBNuN...
GEMINI_API_KEY=AIzaSyDHWZ...
ELEVENLABS_API_KEY=sk_55bf69c2...

# External APIs
ARTIFICIAL_ANALYSIS_API_KEY=aa_GntmGJS...
SERPER_API_KEY=a70f72f6cc...

# Models
GROQ_MODEL_NAME=llama-3.3-70b-versatile
GEMINI_MODEL_NAME=gemini-2.5-flash

# Security
JWT_SECRET_KEY=2c5888e5f1917f4b...
ENABLE_HSTS=false

# Rate Limiting
SECURITY_RATE_LIMIT_IP_PER_MINUTE=120
SECURITY_RATE_LIMIT_USER_PER_MINUTE=60
```

**Frontend (.env):**
```bash
# Backend API URL (auto-detected in production)
VITE_BACKEND_URL=

# WebSocket
VITE_WS_URL=ws://localhost:8001

# Feature Flags
VITE_ENABLE_VOICE=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_GAMIFICATION=true

# App Config
VITE_APP_NAME=MasterX
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development
```

---

## 5. DOCKER STRATEGY

### 5.1 Image Build Strategy

**Multi-Stage Builds:**
```
Stage 1: Base Dependencies
├── Install system packages
├── Install Python/Node.js
└── Set up build tools

Stage 2: Dependency Installation
├── Copy requirements.txt/package.json
├── Install dependencies
└── Cache layer for fast rebuilds

Stage 3: Application Code
├── Copy application code
├── Build assets (frontend only)
└── Final optimizations

Stage 4: Production Runtime
├── Minimal runtime dependencies
├── Security hardening
└── Health check setup
```

### 5.2 Layer Caching Optimization

**Backend (Python):**
```dockerfile
# Layer 1: Base (rarely changes) → cached
FROM python:3.11-slim

# Layer 2: System deps (rarely changes) → cached
RUN apt-get update && apt-get install -y ...

# Layer 3: Python deps (changes occasionally) → cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 4: App code (changes frequently) → rebuilt often
COPY . .
```

**Frontend (Node.js):**
```dockerfile
# Layer 1: Base (rarely changes) → cached
FROM node:20-alpine

# Layer 2: Dependencies (changes occasionally) → cached until package.json changes
COPY package.json yarn.lock .
RUN yarn install --frozen-lockfile

# Layer 3: Build (changes frequently) → rebuilt often
COPY . .
RUN yarn build
```

### 5.3 Image Size Optimization

**Targets:**
- Backend: < 2GB (with ML models)
- Frontend: < 200MB (production build)
- MongoDB: ~500MB (official image)

**Techniques:**
1. Multi-stage builds (discard build artifacts)
2. Alpine-based images where possible
3. .dockerignore to exclude unnecessary files
4. Layer squashing for final images
5. Dependency pruning (remove dev dependencies)

---

## 6. STEP-BY-STEP SETUP

### 6.1 Clone Repository
```bash
# Clone the MasterX repository
git clone https://github.com/vishnuas22/MasterX.git
cd MasterX

# Verify project structure
ls -la
# Expected: backend/, frontend/, README.md, etc.
```

### 6.2 Create Docker Files

#### 6.2.1 Backend Dockerfile
```dockerfile
# FILE: /app/backend/Dockerfile
# MasterX Backend - Multi-Stage Production Build

# ============================================================================
# STAGE 1: Builder (Install dependencies and build environment)
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
# Required for: PyTorch, transformers, onnxruntime, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't store pip cache (reduces image size)
# --upgrade: Ensure latest compatible versions
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Download ML models during build (optional, for faster startup)
# Comment out if you prefer to download on first run
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
    AutoModel.from_pretrained('SamLowe/roberta-base-go_emotions'); \
    AutoTokenizer.from_pretrained('SamLowe/roberta-base-go_emotions')"

# ============================================================================
# STAGE 2: Runtime (Minimal production image)
# ============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy ML models from builder (if pre-downloaded)
COPY --from=builder /root/.cache /root/.cache

# Create non-root user for security
RUN useradd -m -u 1000 masterx && \
    chown -R masterx:masterx /app

# Copy application code
COPY --chown=masterx:masterx . .

# Switch to non-root user
USER masterx

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/api/health', timeout=5)"

# Start command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
```

#### 6.2.2 Frontend Dockerfile (Development)
```dockerfile
# FILE: /app/frontend/Dockerfile.dev
# MasterX Frontend - Development Build with Hot Reload

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["yarn", "start"]
```

#### 6.2.3 Frontend Dockerfile (Production)
```dockerfile
# FILE: /app/frontend/Dockerfile
# MasterX Frontend - Multi-Stage Production Build

# ============================================================================
# STAGE 1: Builder (Build React application)
# ============================================================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile --production=false

# Copy source code
COPY . .

# Build application
RUN yarn build

# ============================================================================
# STAGE 2: Production (Serve with Nginx)
# ============================================================================
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### 6.2.4 Nginx Configuration for Frontend
```nginx
# FILE: /app/frontend/nginx.conf
# Nginx configuration for MasterX frontend

server {
    listen 3000;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React Router (spa fallback)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (optional, if backend on different host)
    location /api {
        proxy_pass http://backend:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 6.3 Docker Compose Configuration

#### 6.3.1 Development Environment
```yaml
# FILE: /app/docker-compose.dev.yml
# MasterX Development Environment

version: '3.9'

services:
  # ==========================================================================
  # MongoDB Database
  # ==========================================================================
  mongodb:
    image: mongo:7.0
    container_name: masterx-mongodb-dev
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:-masterx_dev_password}
      MONGO_INITDB_DATABASE: ${DB_NAME:-masterx}
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
      - ./mongo-init:/docker-entrypoint-initdb.d
    networks:
      - masterx-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 40s
    command: mongod --bind_ip_all --logpath /var/log/mongodb/mongod.log

  # ==========================================================================
  # Backend API (Development with hot reload)
  # ==========================================================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: masterx-backend-dev
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      # Database
      MONGO_URL: mongodb://${MONGO_ROOT_USER:-admin}:${MONGO_ROOT_PASSWORD:-masterx_dev_password}@mongodb:27017
      DB_NAME: ${DB_NAME:-masterx}
      
      # CORS (allow development ports)
      CORS_ORIGINS: http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
      
      # AI Provider Keys (from host .env)
      GROQ_API_KEY: ${GROQ_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      ELEVENLABS_API_KEY: ${ELEVENLABS_API_KEY}
      ARTIFICIAL_ANALYSIS_API_KEY: ${ARTIFICIAL_ANALYSIS_API_KEY}
      SERPER_API_KEY: ${SERPER_API_KEY}
      
      # Models
      GROQ_MODEL_NAME: ${GROQ_MODEL_NAME:-llama-3.3-70b-versatile}
      GEMINI_MODEL_NAME: ${GEMINI_MODEL_NAME:-gemini-2.5-flash}
      
      # Security
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENABLE_HSTS: "false"
      
      # Rate Limiting
      SECURITY_RATE_LIMIT_IP_PER_MINUTE: 120
      SECURITY_RATE_LIMIT_USER_PER_MINUTE: 60
      
      # Development settings
      LOG_LEVEL: DEBUG
      ENVIRONMENT: development
    volumes:
      - ./backend:/app:ro  # Read-only for security
      - ml_models_cache:/root/.cache  # Cache ML models
    networks:
      - masterx-network
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s  # ML models need time to load
    command: uvicorn server:app --host 0.0.0.0 --port 8001 --reload --log-level debug

  # ==========================================================================
  # Frontend (Development with hot reload)
  # ==========================================================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: masterx-frontend-dev
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      VITE_BACKEND_URL: http://localhost:8001
      VITE_WS_URL: ws://localhost:8001
      VITE_ENABLE_VOICE: "true"
      VITE_ENABLE_ANALYTICS: "true"
      VITE_ENABLE_GAMIFICATION: "true"
      VITE_ENVIRONMENT: development
    volumes:
      - ./frontend/src:/app/src:ro
      - ./frontend/public:/app/public:ro
      - /app/node_modules  # Anonymous volume for node_modules
    networks:
      - masterx-network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s

# ==========================================================================
# Networks
# ==========================================================================
networks:
  masterx-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# ==========================================================================
# Volumes
# ==========================================================================
volumes:
  mongodb_data:
    driver: local
  mongodb_config:
    driver: local
  ml_models_cache:
    driver: local
```

#### 6.3.2 Production Environment
```yaml
# FILE: /app/docker-compose.prod.yml
# MasterX Production Environment

version: '3.9'

services:
  # ==========================================================================
  # MongoDB Database (Production with authentication)
  # ==========================================================================
  mongodb:
    image: mongo:7.0
    container_name: masterx-mongodb-prod
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ${DB_NAME}
    volumes:
      - mongodb_data_prod:/data/db
      - mongodb_config_prod:/data/configdb
      - ./mongo-init:/docker-entrypoint-initdb.d
      - ./mongodb-logs:/var/log/mongodb
    networks:
      - masterx-network-prod
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # ==========================================================================
  # Backend API (Production optimized)
  # ==========================================================================
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: masterx-backend-prod
    restart: always
    environment:
      MONGO_URL: mongodb://${MONGO_ROOT_USER}:${MONGO_ROOT_PASSWORD}@mongodb:27017
      DB_NAME: ${DB_NAME}
      CORS_ORIGINS: ${PROD_CORS_ORIGINS}
      GROQ_API_KEY: ${GROQ_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      ELEVENLABS_API_KEY: ${ELEVENLABS_API_KEY}
      ARTIFICIAL_ANALYSIS_API_KEY: ${ARTIFICIAL_ANALYSIS_API_KEY}
      SERPER_API_KEY: ${SERPER_API_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENABLE_HSTS: "true"
      LOG_LEVEL: INFO
      ENVIRONMENT: production
      WORKERS: 4  # Multiple workers for production
    volumes:
      - ml_models_cache_prod:/root/.cache
      - ./logs:/app/logs
    networks:
      - masterx-network-prod
    depends_on:
      mongodb:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 90s
    deploy:
      replicas: 2  # Load balancing
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    command: uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4

  # ==========================================================================
  # Frontend (Production build served by Nginx)
  # ==========================================================================
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: masterx-frontend-prod
    restart: always
    networks:
      - masterx-network-prod
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  # ==========================================================================
  # Nginx Reverse Proxy (Load Balancer & SSL Termination)
  # ==========================================================================
  nginx:
    image: nginx:alpine
    container_name: masterx-nginx-prod
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    networks:
      - masterx-network-prod
    depends_on:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

networks:
  masterx-network-prod:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16

volumes:
  mongodb_data_prod:
    driver: local
  mongodb_config_prod:
    driver: local
  ml_models_cache_prod:
    driver: local
```

### 6.4 .dockerignore Files

#### 6.4.1 Backend .dockerignore
```
# FILE: /app/backend/.dockerignore

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
*.log

# Documentation
*.md
docs/

# Git
.git/
.gitignore

# Environment
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Build artifacts
build/
dist/
*.egg-info/
```

#### 6.4.2 Frontend .dockerignore
```
# FILE: /app/frontend/.dockerignore

# Dependencies
node_modules/

# Build output
dist/
build/

# Cache
.cache/
.vite/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
coverage/
.nyc_output/

# Logs
logs/
*.log

# Documentation
*.md
docs/

# Git
.git/
.gitignore

# Environment
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db
```

### 6.5 Environment Configuration

#### 6.5.1 Create .env.example
```bash
# FILE: /app/.env.example
# Copy this to .env and fill in your values

# ===============================================
# MongoDB Configuration
# ===============================================
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=change_this_strong_password
DB_NAME=masterx

# ===============================================
# AI Provider API Keys
# ===============================================
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# ===============================================
# External Service API Keys
# ===============================================
ARTIFICIAL_ANALYSIS_API_KEY=your_artificial_analysis_key
SERPER_API_KEY=your_serper_api_key

# ===============================================
# Model Configuration
# ===============================================
GROQ_MODEL_NAME=llama-3.3-70b-versatile
GEMINI_MODEL_NAME=gemini-2.5-flash
ELEVENLABS_MODEL_NAME=eleven_flash_v2_5,eleven_multilingual_v2

# ===============================================
# Security
# ===============================================
JWT_SECRET_KEY=generate_a_secure_random_key_here
ENABLE_HSTS=false

# ===============================================
# CORS (Production)
# ===============================================
PROD_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ===============================================
# Rate Limiting
# ===============================================
SECURITY_RATE_LIMIT_IP_PER_MINUTE=120
SECURITY_RATE_LIMIT_USER_PER_MINUTE=60
```

#### 6.5.2 Generate Secrets
```bash
# Generate JWT secret key
python3 -c "import secrets; print(secrets.token_hex(64))"

# Generate strong MongoDB password
openssl rand -base64 32
```

### 6.6 Build and Run

#### 6.6.1 Development Environment
```bash
# Step 1: Copy environment file
cp .env.example .env

# Step 2: Edit .env with your API keys
nano .env

# Step 3: Build images
docker-compose -f docker-compose.dev.yml build

# Step 4: Start services
docker-compose -f docker-compose.dev.yml up -d

# Step 5: View logs
docker-compose -f docker-compose.dev.yml logs -f

# Step 6: Check status
docker-compose -f docker-compose.dev.yml ps

# Step 7: Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

#### 6.6.2 Production Environment
```bash
# Step 1: Configure production .env
cp .env.example .env.production
nano .env.production

# Step 2: Build production images
docker-compose -f docker-compose.prod.yml build --no-cache

# Step 3: Start services
docker-compose -f docker-compose.prod.yml up -d

# Step 4: Verify health
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/api/health

# Step 5: Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 6.7 Verification Steps

```bash
# 1. Check all containers are running
docker ps
# Expected: 3 containers (mongodb, backend, frontend)

# 2. Check backend health
curl http://localhost:8001/api/health
# Expected: {"status": "ok", "timestamp": "...", "version": "1.0.0"}

# 3. Check backend API documentation
curl http://localhost:8001/docs
# Expected: Swagger UI HTML

# 4. Check frontend
curl http://localhost:3000
# Expected: HTML with MasterX

# 5. Check MongoDB
docker exec masterx-mongodb-dev mongosh --eval "db.adminCommand('ping')"
# Expected: { ok: 1 }

# 6. Check backend logs
docker logs masterx-backend-dev --tail 100

# 7. Check resource usage
docker stats --no-stream
```

---

## 7. CONFIGURATION MANAGEMENT

### 7.1 Backend Configuration

#### 7.1.1 Environment-Specific Settings
```python
# FILE: /app/backend/config/settings.py (excerpt)
# Already exists in codebase

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    mongo_url: str = "mongodb://localhost:27017"
    db_name: str = "masterx"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # API Keys (loaded from environment)
    groq_api_key: str = ""
    gemini_api_key: str = ""
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

#### 7.1.2 Docker-Specific Overrides
```bash
# In docker-compose.yml, override settings:
environment:
  MONGO_URL: "mongodb://mongodb:27017"  # Use service name
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
```

### 7.2 Frontend Configuration

#### 7.2.1 Environment Detection
```typescript
// FILE: /app/frontend/src/config/api.config.ts (already exists)

const getBackendUrl = (): string => {
  // Check if explicitly set (Docker env var)
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }
  
  // Auto-detect based on hostname
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8001';
  }
  
  // Production: same domain, different port/path
  return '/api';  // Proxied by Nginx
};

export const API_BASE_URL = getBackendUrl();
```

#### 7.2.2 Build-Time vs Runtime Configuration
```typescript
// Build-time (embedded in bundle)
const BUILD_VERSION = import.meta.env.VITE_APP_VERSION;

// Runtime (can be changed without rebuild)
const FEATURE_FLAGS = {
  voice: import.meta.env.VITE_ENABLE_VOICE === 'true',
  analytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
};
```

### 7.3 Secret Management

#### 7.3.1 Development (Local .env)
```bash
# .env (not committed to git)
GROQ_API_KEY=gsk_actual_key_here
GEMINI_API_KEY=AIza_actual_key_here
```

#### 7.3.2 Production (Docker Secrets)
```bash
# Create Docker secrets
echo "gsk_actual_key" | docker secret create groq_api_key -

# Use in docker-compose:
secrets:
  groq_api_key:
    external: true

services:
  backend:
    secrets:
      - groq_api_key
    environment:
      GROQ_API_KEY_FILE: /run/secrets/groq_api_key
```

---

## 8. SERVICE ORCHESTRATION

### 8.1 Service Dependencies

**Dependency Graph:**
```
MongoDB (starts first)
   ↓
Backend (waits for MongoDB health check)
   ↓
Frontend (waits for Backend)
   ↓
Nginx (optional, waits for Frontend + Backend)
```

### 8.2 Startup Order Configuration
```yaml
# In docker-compose.yml
services:
  backend:
    depends_on:
      mongodb:
        condition: service_healthy  # Wait for MongoDB health check
  
  frontend:
    depends_on:
      backend:
        condition: service_started  # Wait for backend to start
```

### 8.3 Health Checks

#### 8.3.1 MongoDB Health Check
```yaml
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 40s
```

#### 8.3.2 Backend Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 90s  # ML models need time to initialize
```

#### 8.3.3 Frontend Health Check
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### 8.4 Restart Policies

```yaml
# Development: manual control
restart: unless-stopped

# Production: always restart
restart: always
```

### 8.5 Resource Limits

```yaml
# Prevent resource exhaustion
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
    reservations:
      cpus: '2.0'
      memory: 4G
```

---

## 9. NETWORK ARCHITECTURE

### 9.1 Network Topology
```
External Network (Internet)
    ↓
[Nginx Reverse Proxy] :80, :443
    ↓
Internal Bridge Network (masterx-network)
    ├── Frontend Container :3000
    ├── Backend Container :8001
    └── MongoDB Container :27017
```

### 9.2 Network Configuration
```yaml
networks:
  masterx-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
```

### 9.3 Service Communication

**Internal (containers use service names):**
```bash
# Backend connects to MongoDB
MONGO_URL=mongodb://mongodb:27017

# Frontend connects to Backend
VITE_BACKEND_URL=http://backend:8001
```

**External (users access via host):**
```bash
# Frontend
http://localhost:3000

# Backend API
http://localhost:8001/api/health

# API Docs
http://localhost:8001/docs
```

### 9.4 Port Mapping Strategy

| Service | Internal Port | Host Port | Purpose |
|---------|---------------|-----------|---------|
| MongoDB | 27017 | 27017 | Database access |
| Backend | 8001 | 8001 | API endpoints |
| Frontend | 3000 | 3000 | Web UI |
| Nginx | 80/443 | 80/443 | Public access |

### 9.5 Firewall Configuration (Production)

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 27017/tcp # Block MongoDB from external
sudo ufw deny 8001/tcp  # Block Backend from external
sudo ufw enable
```

---

## 10. VOLUME MANAGEMENT

### 10.1 Volume Types

**Named Volumes (Managed by Docker):**
```yaml
volumes:
  mongodb_data:       # MongoDB data files
  mongodb_config:     # MongoDB configuration
  ml_models_cache:    # Cached ML models (Hugging Face)
```

**Bind Mounts (Host directory):**
```yaml
volumes:
  - ./backend:/app:ro       # Source code (read-only)
  - ./logs:/app/logs        # Log files (read-write)
```

### 10.2 Data Persistence

#### 10.2.1 MongoDB Data
```yaml
# Persist database across container restarts
mongodb:
  volumes:
    - mongodb_data:/data/db
    - mongodb_config:/data/configdb
```

**Backup Strategy:**
```bash
# Backup MongoDB data
docker exec masterx-mongodb-prod mongodump --out /backup
docker cp masterx-mongodb-prod:/backup ./mongodb-backup-$(date +%Y%m%d).tar.gz

# Restore MongoDB data
docker cp ./mongodb-backup.tar.gz masterx-mongodb-prod:/backup
docker exec masterx-mongodb-prod mongorestore /backup
```

#### 10.2.2 ML Model Cache
```yaml
# Cache Hugging Face models (avoid re-downloading)
backend:
  volumes:
    - ml_models_cache:/root/.cache
```

**Cache Location:**
- RoBERTa models: `/root/.cache/huggingface/hub/models--SamLowe--roberta-base-go_emotions`
- Size: ~500MB per model

#### 10.2.3 Application Logs
```yaml
# Centralized logging
backend:
  volumes:
    - ./logs/backend:/app/logs
    
frontend:
  volumes:
    - ./logs/frontend:/var/log/nginx
```

### 10.3 Volume Inspection

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect masterx_mongodb_data

# Check volume size
docker system df -v

# Cleanup unused volumes
docker volume prune
```

---

## 11. HEALTH CHECKS & MONITORING

### 11.1 Application Health Endpoints

#### 11.1.1 Backend Health Check
```python
# Already implemented in /app/backend/server.py

@app.get("/api/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/health/detailed")
async def detailed_health():
    """Detailed health with component status"""
    return {
        "status": "healthy",
        "components": {
            "database": "healthy",
            "emotion_engine": "healthy",
            "ai_providers": "healthy"
        },
        "metrics": {
            "response_time_ms": 87.5,
            "health_score": 87.5
        }
    }
```

#### 11.1.2 Docker Health Checks
```yaml
# Automated health monitoring
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/api/health"]
    interval: 30s      # Check every 30 seconds
    timeout: 10s       # Fail if no response in 10s
    retries: 3         # Mark unhealthy after 3 failures
    start_period: 90s  # Grace period during startup
```

### 11.2 Monitoring Stack (Optional)

#### 11.2.1 Prometheus + Grafana Setup
```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - masterx-network
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - masterx-network
```

#### 11.2.2 Prometheus Configuration
```yaml
# FILE: prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'masterx-backend'
    static_configs:
      - targets: ['backend:8001']
    metrics_path: '/api/metrics'
  
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb:27017']
```

### 11.3 Log Aggregation

#### 11.3.1 Centralized Logging with ELK Stack
```yaml
# FILE: docker-compose.logging.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

#### 11.3.2 Docker Logging Driver
```yaml
# Send logs to external system
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"
        labels: "production"
```

### 11.4 Alerting

```yaml
# Alert on unhealthy containers
# Can integrate with Slack, PagerDuty, etc.
# Using Prometheus Alertmanager

# FILE: alertmanager.yml
route:
  receiver: 'slack'
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'MasterX Alert'
```

---

## 12. SECURITY BEST PRACTICES

### 12.1 Image Security

#### 12.1.1 Use Official Base Images
```dockerfile
# ✅ GOOD: Official Python image
FROM python:3.11-slim

# ❌ BAD: Random user image
# FROM someuser/python:latest
```

#### 12.1.2 Scan for Vulnerabilities
```bash
# Scan images with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image masterx-backend:latest

# Scan with Snyk
snyk container test masterx-backend:latest
```

#### 12.1.3 Non-Root User
```dockerfile
# Create and use non-root user
RUN useradd -m -u 1000 masterx
USER masterx
```

### 12.2 Secret Management

#### 12.2.1 Never Commit Secrets
```bash
# .gitignore
.env
.env.local
.env.production
*.key
*.pem
```

#### 12.2.2 Use Docker Secrets (Swarm Mode)
```bash
# Create secret
echo "my_secret_value" | docker secret create my_secret -

# Use in service
docker service create \
  --name my_service \
  --secret my_secret \
  my_image
```

#### 12.2.3 Use Environment Files
```bash
# Store secrets separately
# .env.secrets (not in git)
GROQ_API_KEY=gsk_actual_key
GEMINI_API_KEY=AIza_actual_key

# Load in docker-compose
services:
  backend:
    env_file:
      - .env
      - .env.secrets  # Git-ignored
```

### 12.3 Network Security

#### 12.3.1 Internal-Only Services
```yaml
# MongoDB should not be exposed externally
mongodb:
  # ports:  # DO NOT expose MongoDB port
  #   - "27017:27017"
  networks:
    - masterx-network  # Only accessible within network
```

#### 12.3.2 Nginx as Security Gateway
```nginx
# FILE: nginx.conf

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # API rate limiting
    location /api {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend:8001;
    }
}
```

### 12.4 SSL/TLS Configuration

#### 12.4.1 Let's Encrypt with Certbot
```yaml
# FILE: docker-compose.ssl.yml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
    command: certonly --webroot --webroot-path=/var/www/certbot \
             --email your@email.com --agree-tos --no-eff-email \
             -d yourdomain.com -d www.yourdomain.com
```

#### 12.4.2 Nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}
```

### 12.5 Resource Limits

```yaml
# Prevent DoS attacks via resource exhaustion
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

---

## 13. PRODUCTION DEPLOYMENT

### 13.1 Pre-Deployment Checklist

```markdown
✅ **Code & Configuration:**
- [ ] All environment variables configured in .env.production
- [ ] API keys validated and working
- [ ] JWT secret generated (64+ characters)
- [ ] MongoDB credentials changed from defaults
- [ ] CORS origins set to production domains
- [ ] SSL certificates obtained and configured
- [ ] Log level set to INFO (not DEBUG)
- [ ] Error tracking configured (Sentry, etc.)

✅ **Infrastructure:**
- [ ] Docker Engine installed and updated
- [ ] Sufficient disk space (200GB+)
- [ ] Sufficient RAM (32GB+)
- [ ] Firewall configured correctly
- [ ] Backup strategy in place
- [ ] Monitoring setup (Prometheus/Grafana)

✅ **Testing:**
- [ ] All health checks passing
- [ ] Load testing completed
- [ ] Security scan completed (Trivy/Snyk)
- [ ] API endpoints tested
- [ ] Frontend loads correctly
- [ ] Database connections working

✅ **Documentation:**
- [ ] Runbook created
- [ ] Deployment guide reviewed
- [ ] Rollback procedure documented
- [ ] Team trained on deployment process
```

### 13.2 Deployment Steps

#### 13.2.1 Initial Deployment
```bash
# 1. Clone repository on production server
git clone https://github.com/vishnuas22/MasterX.git
cd MasterX

# 2. Configure production environment
cp .env.example .env.production
nano .env.production  # Edit with production values

# 3. Build production images
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Start services in detached mode
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8001/api/health

# 6. Initialize database (first time only)
docker exec masterx-backend-prod python -c "from utils.database import initialize_database; initialize_database()"

# 7. Monitor logs for 5 minutes
docker-compose -f docker-compose.prod.yml logs -f

# 8. Configure SSL (if using Nginx)
docker-compose -f docker-compose.ssl.yml run certbot

# 9. Update DNS records
# Point your domain to server IP

# 10. Test production URL
curl https://yourdomain.com/api/health
```

#### 13.2.2 Rolling Updates (Zero Downtime)
```bash
# 1. Build new image
docker-compose -f docker-compose.prod.yml build backend

# 2. Tag with version
docker tag masterx-backend:latest masterx-backend:v1.2.0

# 3. Update one replica at a time
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=2

# 4. Wait for health check
watch docker-compose -f docker-compose.prod.yml ps

# 5. Remove old replica
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale backend=1

# 6. Verify
curl https://yourdomain.com/api/health
```

### 13.3 Scaling Strategies

#### 13.3.1 Horizontal Scaling
```yaml
# Scale backend replicas
services:
  backend:
    deploy:
      replicas: 4  # Run 4 instances
```

```bash
# Scale via CLI
docker-compose -f docker-compose.prod.yml up -d --scale backend=4
```

#### 13.3.2 Load Balancing
```nginx
# Nginx load balancer configuration
upstream backend_servers {
    least_conn;  # Load balancing algorithm
    server backend:8001 max_fails=3 fail_timeout=30s;
    server backend2:8001 max_fails=3 fail_timeout=30s;
    server backend3:8001 max_fails=3 fail_timeout=30s;
}

server {
    location /api {
        proxy_pass http://backend_servers;
    }
}
```

#### 13.3.3 Database Replication
```yaml
# MongoDB replica set
mongodb1:
  image: mongo:7.0
  command: mongod --replSet rs0

mongodb2:
  image: mongo:7.0
  command: mongod --replSet rs0

mongodb3:
  image: mongo:7.0
  command: mongod --replSet rs0
```

### 13.4 Backup & Disaster Recovery

#### 13.4.1 Automated Backups
```bash
#!/bin/bash
# FILE: /app/scripts/backup.sh

# Backup script (run daily via cron)
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/masterx"

# MongoDB backup
docker exec masterx-mongodb-prod mongodump --out /tmp/backup_$DATE
docker cp masterx-mongodb-prod:/tmp/backup_$DATE $BACKUP_DIR/mongodb_$DATE

# Volume backups
docker run --rm -v masterx_ml_models_cache:/data -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/ml_cache_$DATE.tar.gz /data

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

# Upload to S3 (optional)
aws s3 sync $BACKUP_DIR s3://masterx-backups/
```

#### 13.4.2 Disaster Recovery Procedure
```bash
# 1. Stop services
docker-compose -f docker-compose.prod.yml down

# 2. Restore MongoDB
docker run --rm -v masterx_mongodb_data:/data -v ./backups:/backup \
  mongo:7.0 mongorestore /backup/mongodb_20250101_120000

# 3. Restore volumes
docker run --rm -v masterx_ml_models_cache:/data -v ./backups:/backup \
  alpine tar xzf /backup/ml_cache_20250101_120000.tar.gz -C /

# 4. Restart services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl http://localhost:8001/api/health
```

---

## 14. TROUBLESHOOTING GUIDE

### 14.1 Common Issues

#### 14.1.1 Container Won't Start
```bash
# Check logs
docker logs masterx-backend-dev

# Common causes:
# - Port already in use
sudo lsof -i :8001
# Solution: Stop conflicting process or change port

# - Missing environment variables
docker exec masterx-backend-dev env | grep GROQ_API_KEY
# Solution: Add to .env file

# - Insufficient memory
docker stats
# Solution: Increase Docker memory limit
```

#### 14.1.2 MongoDB Connection Failed
```bash
# Check MongoDB is running
docker ps | grep mongodb

# Test connection
docker exec masterx-mongodb-dev mongosh --eval "db.adminCommand('ping')"

# Check connection string
docker exec masterx-backend-dev env | grep MONGO_URL
# Should be: mongodb://mongodb:27017 (not localhost)

# Solution: Update MONGO_URL in docker-compose.yml
```

#### 14.1.3 ML Models Not Loading
```bash
# Check ML model cache
docker exec masterx-backend-dev ls -la /root/.cache/huggingface/

# Clear cache and re-download
docker volume rm masterx_ml_models_cache
docker-compose -f docker-compose.dev.yml up -d backend

# Monitor download progress
docker logs -f masterx-backend-dev | grep "Downloading"
```

#### 14.1.4 Frontend Can't Connect to Backend
```bash
# Check VITE_BACKEND_URL
docker exec masterx-frontend-dev env | grep VITE_BACKEND_URL

# Should be: http://backend:8001 (Docker network)
# Or: http://localhost:8001 (host machine)

# Test connectivity
docker exec masterx-frontend-dev curl http://backend:8001/api/health

# Check CORS settings
curl -H "Origin: http://localhost:3000" http://localhost:8001/api/health -v
# Should include: Access-Control-Allow-Origin: http://localhost:3000
```

#### 14.1.5 Out of Disk Space
```bash
# Check Docker disk usage
docker system df

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all stopped containers
docker container prune

# Remove build cache
docker builder prune
```

### 14.2 Performance Issues

#### 14.2.1 Slow Response Times
```bash
# Check resource usage
docker stats

# Check backend logs for slow queries
docker logs masterx-backend-prod | grep "slow"

# Enable performance profiling
docker exec masterx-backend-prod python -c "
from services.emotion.emotion_profiler import EmotionProfiler
profiler = EmotionProfiler()
print(profiler.get_performance_summary())
"

# Increase resource limits
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '8.0'
      memory: 16G
```

#### 14.2.2 High Memory Usage
```bash
# Check memory by service
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Backend high memory (ML models):
# Solution: Use ONNX optimization
docker exec masterx-backend-prod python -c "
from services.emotion.onnx_optimizer import optimize_model
optimize_model()
"

# MongoDB high memory:
# Solution: Set WiredTiger cache size
# Add to docker-compose.yml:
command: mongod --wiredTigerCacheSizeGB 2
```

### 14.3 Debugging Techniques

#### 14.3.1 Interactive Shell
```bash
# Enter container shell
docker exec -it masterx-backend-dev /bin/bash

# Python REPL in container
docker exec -it masterx-backend-dev python

# Test imports
>>> from services.emotion.emotion_engine import EmotionEngine
>>> engine = EmotionEngine()
>>> engine.initialize()
```

#### 14.3.2 Network Debugging
```bash
# Inspect network
docker network inspect masterx_masterx-network

# Test connectivity between containers
docker exec masterx-backend-dev ping mongodb
docker exec masterx-frontend-dev wget -O- http://backend:8001/api/health
```

#### 14.3.3 Volume Inspection
```bash
# Inspect volume
docker volume inspect masterx_mongodb_data

# Browse volume contents
docker run --rm -v masterx_mongodb_data:/data alpine ls -la /data

# Copy files from volume
docker run --rm -v masterx_mongodb_data:/data -v $(pwd):/backup \
  alpine cp -r /data /backup/mongodb_data_copy
```

### 14.4 Health Check Failures

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' masterx-backend-dev | jq

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' masterx-backend-dev

# Manual health check
docker exec masterx-backend-dev curl -f http://localhost:8001/api/health

# Disable health check temporarily (for debugging)
# Edit docker-compose.yml: comment out healthcheck section
```

---

## 15. MAINTENANCE & UPDATES

### 15.1 Regular Maintenance Tasks

#### 15.1.1 Weekly Tasks
```bash
# 1. Check logs for errors
docker-compose -f docker-compose.prod.yml logs --tail 1000 | grep ERROR

# 2. Check disk usage
docker system df

# 3. Review resource usage
docker stats --no-stream

# 4. Backup database
./scripts/backup.sh

# 5. Update ML models (if new versions)
docker exec masterx-backend-prod python -c "
from transformers import AutoModel
AutoModel.from_pretrained('SamLowe/roberta-base-go_emotions', force_download=True)
"
```

#### 15.1.2 Monthly Tasks
```bash
# 1. Update Docker images
docker-compose -f docker-compose.prod.yml pull

# 2. Security scan
trivy image masterx-backend:latest

# 3. Database optimization
docker exec masterx-mongodb-prod mongosh --eval "
db.adminCommand({compact: 'messages'})
db.adminCommand({compact: 'sessions'})
"

# 4. Review and rotate logs
find ./logs -type f -name "*.log" -mtime +30 -delete

# 5. Test disaster recovery
# Restore from latest backup to staging environment
```

### 15.2 Updating Application

#### 15.2.1 Update Backend Code
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new image
docker-compose -f docker-compose.prod.yml build backend

# 3. Test in staging (if available)
docker-compose -f docker-compose.staging.yml up -d backend
# Run tests...

# 4. Deploy to production (rolling update)
docker-compose -f docker-compose.prod.yml up -d --no-deps backend

# 5. Verify
curl https://yourdomain.com/api/health
docker-compose -f docker-compose.prod.yml logs -f backend
```

#### 15.2.2 Update Frontend Code
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new image
docker-compose -f docker-compose.prod.yml build frontend

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend

# 4. Clear browser cache and verify
# Open incognito window: https://yourdomain.com
```

#### 15.2.3 Update Dependencies
```bash
# Backend (requirements.txt)
# 1. Update locally
cd backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# 2. Rebuild image
docker-compose -f docker-compose.prod.yml build backend

# Frontend (package.json)
# 1. Update locally
cd frontend
yarn upgrade-interactive --latest

# 2. Rebuild image
docker-compose -f docker-compose.prod.yml build frontend
```

### 15.3 Monitoring & Alerts

#### 15.3.1 Setup Monitoring
```bash
# Deploy monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3001
# Default credentials: admin/admin

# Import MasterX dashboard
# Dashboard JSON available in ./monitoring/grafana-dashboards/
```

#### 15.3.2 Configure Alerts
```yaml
# FILE: alertmanager.yml
route:
  receiver: 'team-email'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'app_password'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
```

### 15.4 Rollback Procedure

```bash
# 1. Identify issue
docker-compose -f docker-compose.prod.yml logs backend

# 2. Check previous image
docker images masterx-backend

# 3. Rollback to previous version
docker tag masterx-backend:v1.1.0 masterx-backend:latest
docker-compose -f docker-compose.prod.yml up -d backend

# 4. Or rollback entire stack
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://yourdomain.com/api/health

# 6. Notify team
echo "Rolled back to version 1.1.0 due to [issue]"
```

---

## 16. ADVANCED TOPICS

### 16.1 CI/CD Pipeline

```yaml
# FILE: .github/workflows/docker-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build images
        run: |
          docker-compose -f docker-compose.prod.yml build
      
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose -f docker-compose.prod.yml push
      
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/masterx
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
```

### 16.2 Multi-Environment Setup

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Staging
docker-compose -f docker-compose.staging.yml up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### 16.3 GPU Support (for ML models)

```yaml
# docker-compose.gpu.yml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      CUDA_VISIBLE_DEVICES: 0
```

---

## 17. CONCLUSION

### 17.1 Key Takeaways

✅ **Multi-Stage Builds:** Minimize image size and improve security  
✅ **Health Checks:** Automatic recovery and monitoring  
✅ **Volume Management:** Data persistence and backups  
✅ **Network Isolation:** Enhanced security  
✅ **Resource Limits:** Prevent resource exhaustion  
✅ **Logging & Monitoring:** Complete observability  
✅ **Secret Management:** Secure API keys and credentials  
✅ **Zero-Downtime Deployments:** Rolling updates  

### 17.2 Production Readiness Checklist

```markdown
✅ All Docker files created and tested
✅ Environment variables configured
✅ Health checks implemented
✅ Logging configured
✅ Monitoring setup
✅ Backups automated
✅ SSL/TLS configured
✅ Firewall configured
✅ Disaster recovery tested
✅ Documentation complete
✅ Team trained
```

### 17.3 Support & Resources

**Documentation:**
- Official Docker Docs: https://docs.docker.com
- FastAPI Docs: https://fastapi.tiangolo.com
- React Docs: https://react.dev
- MongoDB Docs: https://docs.mongodb.com

**Community:**
- Docker Forums: https://forums.docker.com
- Stack Overflow: #docker #fastapi #react

**Tools:**
- Docker Desktop: https://www.docker.com/products/docker-desktop
- Portainer: https://www.portainer.io (Container management UI)
- Lazydocker: https://github.com/jesseduffield/lazydocker (Terminal UI)

---

## 18. APPENDIX

### 18.1 Complete Command Reference

```bash
# Build
docker-compose build                    # Build all services
docker-compose build backend            # Build specific service
docker-compose build --no-cache         # Build without cache

# Start/Stop
docker-compose up -d                    # Start all (detached)
docker-compose up backend               # Start specific service
docker-compose stop                     # Stop all
docker-compose down                     # Stop and remove
docker-compose down -v                  # Stop and remove volumes

# Logs
docker-compose logs -f                  # Follow all logs
docker-compose logs backend             # Specific service
docker-compose logs --tail 100 backend  # Last 100 lines

# Execute
docker-compose exec backend bash        # Shell in container
docker-compose exec backend python      # Python REPL
docker-compose exec mongodb mongosh     # MongoDB shell

# Scale
docker-compose up -d --scale backend=4  # Scale to 4 replicas

# Cleanup
docker system prune -a                  # Remove all unused
docker volume prune                     # Remove unused volumes
docker network prune                    # Remove unused networks
```

### 18.2 File Checklist

```
Required Files:
├── backend/
│   ├── Dockerfile ✓
│   ├── .dockerignore ✓
│   ├── requirements.txt ✓
│   └── .env ✓
├── frontend/
│   ├── Dockerfile ✓
│   ├── Dockerfile.dev ✓
│   ├── .dockerignore ✓
│   ├── nginx.conf ✓
│   ├── package.json ✓
│   └── .env ✓
├── docker-compose.dev.yml ✓
├── docker-compose.prod.yml ✓
├── .env.example ✓
└── DOCKER_SETUP_DOCUMENTATION.md ✓
```

---

## 📄 Document Metadata

- **Version:** 1.0.0
- **Last Updated:** November 19, 2025
- **Author:** MasterX Development Team
- **Reviewed By:** DevOps Team
- **Next Review:** December 19, 2025

---

**END OF DOCUMENTATION**
