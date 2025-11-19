# 🐳 MasterX - Docker Quick Start Guide

**Production-Ready Setup | Following Big Tech Standards (Google/Meta/Amazon)**

---

## 📋 Prerequisites

### Required Software
```bash
# 1. Docker Engine (24.0.0+)
docker --version

# 2. Docker Compose (2.20.0+)
docker-compose --version

# 3. Git
git --version
```

### System Requirements
- **CPU:** 4+ cores (8+ recommended)
- **RAM:** 16GB minimum (32GB recommended for ML models)
- **Disk:** 50GB+ free space
- **OS:** Linux (Ubuntu 22.04+), macOS (12.0+), Windows 10/11 with WSL2

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Environment Setup
```bash
# Create .env file from template
cp .env.docker.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**CRITICAL:** Add these required keys in `.env`:
- `GROQ_API_KEY` - Get from https://console.groq.com/
- `GEMINI_API_KEY` - Get from https://ai.google.dev/
- `JWT_SECRET_KEY` - Generate with: `python3 -c "import secrets; print(secrets.token_hex(64))"`
- `MONGO_ROOT_PASSWORD` - Generate with: `openssl rand -base64 32`

### Step 2: Start Services
```bash
# Start all services in development mode
./docker-dev.sh start

# View logs (Ctrl+C to exit)
./docker-dev.sh logs
```

### Step 3: Access Application
```
✅ Frontend:  http://localhost:3000
✅ Backend:   http://localhost:8001
✅ API Docs:  http://localhost:8001/docs
✅ MongoDB:   mongodb://localhost:27017
```

### Step 4: Verify Health
```bash
./docker-dev.sh health
```

---

## 📁 Docker Files Overview

### Backend Files
```
backend/
├── Dockerfile         # Production-optimized multi-stage build
├── .dockerignore     # Excludes unnecessary files
└── requirements.txt  # Python dependencies (150+ packages)
```

### Frontend Files
```
frontend/
├── Dockerfile        # Production build (React + Nginx)
├── Dockerfile.dev    # Development build (Vite with HMR)
├── nginx.conf        # Nginx configuration for SPA
├── .dockerignore     # Excludes unnecessary files
└── package.json      # Node.js dependencies (60+ packages)
```

### Compose Files
```
├── docker-compose.dev.yml   # Development environment
├── docker-compose.prod.yml  # Production environment
└── .env                     # Environment variables (DO NOT COMMIT)
```

---

## 🛠️ Development Commands

### Basic Operations
```bash
# Start services
./docker-dev.sh start

# Stop services
./docker-dev.sh stop

# Restart services
./docker-dev.sh restart

# View status
./docker-dev.sh status
```

### Logs & Debugging
```bash
# View all logs
./docker-dev.sh logs

# View specific service logs
./docker-dev.sh logs backend
./docker-dev.sh logs frontend
./docker-dev.sh logs mongodb

# Open shell in container
./docker-dev.sh shell backend
./docker-dev.sh shell frontend
```

### Build & Rebuild
```bash
# Build images (first time or after Dockerfile changes)
./docker-dev.sh build

# Rebuild everything from scratch
./docker-dev.sh rebuild

# Clean up (removes volumes - DATA LOSS WARNING)
./docker-dev.sh clean
```

---

## 🔧 Manual Docker Compose Commands

If you prefer direct `docker-compose` commands:

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild specific service
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d backend
```

---

## 🏭 Production Deployment

### Step 1: Configure Production Environment
```bash
# Edit .env with production values
nano .env
```

**CRITICAL Production Settings:**
```bash
# Strong secrets (REQUIRED)
JWT_SECRET_KEY=<64+ character random string>
MONGO_ROOT_PASSWORD=<32+ character password>

# Production domains
PROD_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Enable security
ENABLE_HSTS=true

# Production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Step 2: Start Production Services
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify health
docker-compose -f docker-compose.prod.yml ps
```

### Step 3: Production Monitoring
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check service health
curl https://yourdomain.com/health
curl https://yourdomain.com/api/health

# Monitor resources
docker stats
```

---

## 🐛 Troubleshooting

### Issue: Services Won't Start
```bash
# Check logs
./docker-dev.sh logs

# Verify environment
cat .env | grep -v "PASSWORD\|SECRET\|KEY"

# Restart services
./docker-dev.sh restart
```

### Issue: Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Find process using port 8001
lsof -i :8001

# Kill process or change port in docker-compose.dev.yml
```

### Issue: Database Connection Failed
```bash
# Check MongoDB status
docker-compose -f docker-compose.dev.yml ps mongodb

# View MongoDB logs
docker-compose -f docker-compose.dev.yml logs mongodb

# Restart MongoDB
docker-compose -f docker-compose.dev.yml restart mongodb
```

### Issue: Backend ML Models Not Loading
```bash
# Check backend logs
./docker-dev.sh logs backend

# ML models download on first run (may take 5-10 minutes)
# Look for: "✅ Emotion engine initialized"

# If stuck, restart backend
docker-compose -f docker-compose.dev.yml restart backend
```

### Issue: Frontend Not Updating
```bash
# Rebuild frontend
docker-compose -f docker-compose.dev.yml build frontend
docker-compose -f docker-compose.dev.yml up -d frontend

# Clear browser cache (Ctrl+Shift+R)
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Host                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │   MongoDB    │  │
│  │  React/Vite  │  │   FastAPI    │  │   Database   │  │
│  │  Port: 3000  │  │  Port: 8001  │  │  Port: 27017 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                    masterx-network                       │
│                    (Bridge Network)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Checklist

### Development
- ✅ Use `.env` file for secrets
- ✅ Never commit `.env` to git
- ✅ Use `localhost` for database
- ✅ Relaxed CORS for development

### Production
- ✅ Strong JWT secret (64+ chars)
- ✅ Strong MongoDB password (32+ chars)
- ✅ Specific CORS origins (no wildcards)
- ✅ Enable HSTS (requires HTTPS)
- ✅ Disable debug mode
- ✅ Set LOG_LEVEL=INFO
- ✅ Use production database (not localhost)
- ✅ Enable rate limiting
- ✅ Regular security updates

---

## 📈 Performance Optimization

### Resource Limits
Adjust in `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Maximum CPU cores
      memory: 8G       # Maximum RAM
    reservations:
      cpus: '2.0'      # Guaranteed CPU
      memory: 4G       # Guaranteed RAM
```

### Scaling Services
```bash
# Scale backend to 3 replicas
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale frontend to 2 replicas
docker-compose -f docker-compose.prod.yml up -d --scale frontend=2
```

---

## 📚 Additional Resources

- **Full Documentation:** `DOCKER_SETUP_DOCUMENTATION.md`
- **API Documentation:** http://localhost:8001/docs
- **Health Monitoring:** http://localhost:8001/api/health/detailed
- **Project README:** `README.md`

---

## 🆘 Getting Help

1. **Check logs first:** `./docker-dev.sh logs`
2. **View health status:** `./docker-dev.sh health`
3. **Review documentation:** `DOCKER_SETUP_DOCUMENTATION.md`
4. **Check GitHub issues:** [Repository Issues]
5. **Contact support:** [Support Email]

---

**Status:** ✅ Production Ready | **Version:** 1.0.0 | **Last Updated:** November 2025
