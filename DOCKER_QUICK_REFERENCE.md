# 🐳 Docker Quick Reference - MasterX

**One-page cheat sheet for daily use**

---

## 🚀 QUICK START (3 Commands)

```bash
# 1. Navigate to project folder
cd /path/to/MasterX

# 2. Start everything
docker-compose -f docker-compose.dev.yml up -d

# 3. Open browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001/docs
```

**That's it! Everything is running.** ✅

---

## ⚡ DAILY COMMANDS

### Start & Stop
```bash
# Start (background)
docker-compose -f docker-compose.dev.yml up -d

# Stop (keep containers)
docker-compose -f docker-compose.dev.yml stop

# Stop & remove
docker-compose -f docker-compose.dev.yml down

# Restart all
docker-compose -f docker-compose.dev.yml restart

# Restart one service
docker-compose -f docker-compose.dev.yml restart backend
```

---

### View Logs
```bash
# All logs (live)
docker-compose -f docker-compose.dev.yml logs -f

# One service
docker-compose -f docker-compose.dev.yml logs -f backend

# Last 50 lines
docker-compose -f docker-compose.dev.yml logs --tail=50 backend
```

---

### Check Status
```bash
# View all services
docker-compose -f docker-compose.dev.yml ps

# Should show:
# ✅ masterx-mongodb-dev   Up (healthy)
# ✅ masterx-backend-dev   Up (healthy)
# ✅ masterx-frontend-dev  Up (healthy)
```

---

### Rebuild
```bash
# Rebuild all
docker-compose -f docker-compose.dev.yml build

# Rebuild without cache (clean)
docker-compose -f docker-compose.dev.yml build --no-cache

# Build and start
docker-compose -f docker-compose.dev.yml up -d --build
```

---

## 🔧 TROUBLESHOOTING

### Service Not Starting?
```bash
# View logs
docker-compose -f docker-compose.dev.yml logs backend

# Restart service
docker-compose -f docker-compose.dev.yml restart backend

# Rebuild service
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d backend
```

---

### Changes Not Showing?
```bash
# Backend: Should auto-reload
docker-compose -f docker-compose.dev.yml logs -f backend

# Frontend: Refresh browser
# Press: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

# If still not working, restart
docker-compose -f docker-compose.dev.yml restart frontend
```

---

### Clean Up
```bash
# Remove containers
docker-compose -f docker-compose.dev.yml down

# Remove containers + volumes (⚠️ DELETES DATA)
docker-compose -f docker-compose.dev.yml down -v

# Clean up Docker
docker system prune
```

---

### Port Already in Use?
```bash
# Mac/Linux: Kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Windows: Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## 🌐 ACCESS URLS

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main app UI |
| API Docs | http://localhost:8001/docs | Test APIs |
| Backend Health | http://localhost:8001/api/health | Health check |

---

## 📦 CONTAINER COMMANDS

### Execute Command Inside Container
```bash
# Backend bash
docker-compose -f docker-compose.dev.yml exec backend bash

# Frontend shell
docker-compose -f docker-compose.dev.yml exec frontend sh

# Run Python command
docker-compose -f docker-compose.dev.yml exec backend python -c "print('Hello')"
```

---

### Install Package
```bash
# Backend: Add to requirements.txt, then:
docker-compose -f docker-compose.dev.yml build backend
docker-compose -f docker-compose.dev.yml up -d backend

# Frontend: Enter container and install
docker-compose -f docker-compose.dev.yml exec frontend yarn add <package>
```

---

## 🆘 EMERGENCY COMMANDS

### Nothing Works? Nuclear Reset:
```bash
# 1. Stop everything
docker-compose -f docker-compose.dev.yml down -v

# 2. Clean Docker
docker system prune -a

# 3. Start fresh
docker-compose -f docker-compose.dev.yml up -d --build
```

---

### Docker Desktop Not Running?
```bash
# Check Docker is running
docker ps

# If error, start Docker Desktop app
# Windows: Open from Start Menu
# Mac: Open from Applications
# Linux: sudo systemctl start docker
```

---

## 💡 PRO TIPS

### Aliases (Add to ~/.bashrc or ~/.zshrc)
```bash
alias dcu="docker-compose -f docker-compose.dev.yml up -d"
alias dcd="docker-compose -f docker-compose.dev.yml down"
alias dcr="docker-compose -f docker-compose.dev.yml restart"
alias dcl="docker-compose -f docker-compose.dev.yml logs -f"
alias dcp="docker-compose -f docker-compose.dev.yml ps"
alias dcb="docker-compose -f docker-compose.dev.yml build"
```

Then use: `dcu` to start, `dcl` to view logs, etc.

---

### VSCode Integration
1. Install "Docker" extension by Microsoft
2. View containers in sidebar
3. Right-click for actions
4. Click container to view logs

---

### Check Resource Usage
```bash
# Docker disk usage
docker system df

# Container resource usage
docker stats
```

---

## 📋 PRODUCTION MODE

```bash
# Build production
docker-compose -f docker-compose.prod.yml build

# Start production
docker-compose -f docker-compose.prod.yml up -d

# View status
docker-compose -f docker-compose.prod.yml ps

# Stop production
docker-compose -f docker-compose.prod.yml down
```

**Production URLs:**
- Frontend: http://localhost (port 80)
- Backend: http://localhost/api
- With Nginx reverse proxy

---

## 🔍 DEBUGGING

### View Container Details
```bash
# Inspect container
docker inspect masterx-backend-dev

# View environment variables
docker-compose -f docker-compose.dev.yml exec backend env

# Test network connection
docker-compose -f docker-compose.dev.yml exec backend curl http://mongodb:27017
```

---

### Database Access
```bash
# MongoDB shell
docker-compose -f docker-compose.dev.yml exec mongodb mongosh

# In mongosh:
> show dbs
> use masterx
> show collections
> db.users.find()
```

---

## 📞 GET HELP

**Issues?**
1. Check logs: `docker-compose -f docker-compose.dev.yml logs -f`
2. Read: `DOCKER_BEGINNER_GUIDE.md` (detailed guide)
3. Check: Section 9 (Common Issues & Solutions)
4. Ask: Create GitHub issue with logs

**Quick Help:**
```bash
# Docker help
docker --help
docker-compose --help

# Service-specific help
docker-compose -f docker-compose.dev.yml logs backend
```

---

## ✅ HEALTH CHECK

Run these to verify everything works:

```bash
# 1. Check services running
docker-compose -f docker-compose.dev.yml ps
# All should show "Up (healthy)"

# 2. Test backend
curl http://localhost:8001/api/health
# Should return: {"status":"ok",...}

# 3. Test frontend
curl -I http://localhost:3000
# Should return: HTTP/1.1 200 OK

# 4. View logs for errors
docker-compose -f docker-compose.dev.yml logs --tail=50
```

---

## 🎯 COMMON WORKFLOWS

### Morning: Start Work
```bash
cd MasterX
docker-compose -f docker-compose.dev.yml up -d
# Open http://localhost:3000
```

### During Work: View Logs
```bash
docker-compose -f docker-compose.dev.yml logs -f backend
```

### Code Change: Verify Hot Reload
```bash
# Save file, check logs:
docker-compose -f docker-compose.dev.yml logs backend
# Should see: "Reloading..."
```

### Evening: Stop Work
```bash
docker-compose -f docker-compose.dev.yml stop
```

### Weekly: Clean Up
```bash
docker system prune
```

---

**🎉 You're all set! Keep this handy for daily reference.**

**Full Guide:** `DOCKER_BEGINNER_GUIDE.md`  
**Detailed Docs:** `DOCKER_SETUP_DOCUMENTATION.md`
