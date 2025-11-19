# 🖼️ Docker Visual Setup Guide - MasterX

**Step-by-step guide with visual explanations**

---

## 📸 BEFORE YOU START

### What You'll See After Setup

**Frontend (http://localhost:3000):**
```
┌─────────────────────────────────────────────────────────┐
│  🎓 MasterX           Features  Pricing  Testimonials   │
│                                          Log in Sign up  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│           ✨ Powered by Advanced ML                      │
│                                                          │
│         Learn with AI that                               │
│         understands your emotions                        │
│                                                          │
│    Join 10,000+ learners experiencing 35% faster        │
│    improvement with real-time emotion detection         │
│                                                          │
│      [Get Started for Free]  [Watch Demo]               │
│                                                          │
│  ⭐ 4.8/5      👥 10,000+      ❤️ 27                    │
│   1,247 reviews  Active learners  Emotions detected     │
│                                                          │
│         [Image: Students collaborating]                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**API Docs (http://localhost:8001/docs):**
```
┌─────────────────────────────────────────────────────────┐
│  MasterX API - Swagger UI                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📗 default                                              │
│    GET  /                                                │
│    GET  /api/health                                      │
│    GET  /api/health/detailed                             │
│                                                          │
│  🔐 Authentication                                       │
│    POST /api/auth/register                               │
│    POST /api/auth/login                                  │
│    POST /api/auth/logout                                 │
│    GET  /api/auth/me                                     │
│    ...                                                   │
│                                                          │
│  💬 Chat & Learning                                      │
│    POST /api/v1/chat                                     │
│    GET  /api/v1/chat/history/{session_id}               │
│    ...                                                   │
│                                                          │
│  🎮 Gamification                                         │
│    GET  /api/v1/gamification/stats/{user_id}            │
│    ...                                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎬 STEP-BY-STEP VISUAL GUIDE

### STEP 1: Install Docker Desktop

#### Windows Installation

**1. Download:**
```
Browser → https://www.docker.com/products/docker-desktop
        ↓
┌─────────────────────────────────────┐
│  Docker Desktop                      │
│                                      │
│  [Download for Windows]              │
│                                      │
│  System Requirements:                │
│  • Windows 10/11 64-bit              │
│  • WSL 2 feature enabled             │
│  • 4GB RAM minimum                   │
└─────────────────────────────────────┘
```

**2. Install:**
```
Double-click Docker Desktop Installer.exe
        ↓
┌─────────────────────────────────────┐
│  Docker Desktop Setup                │
│                                      │
│  ☑ Enable WSL 2 (Recommended)       │
│  ☑ Add shortcut to desktop           │
│                                      │
│  [Install]                           │
└─────────────────────────────────────┘
        ↓
Restart Computer
```

**3. Verify:**
```
Open PowerShell or Command Prompt
        ↓
C:\> docker --version
        ↓
✅ Docker version 24.0.0, build abc123
```

#### Mac Installation

**1. Download:**
```
Browser → https://www.docker.com/products/docker-desktop
        ↓
Choose your Mac type:
• Intel Chip → Docker Desktop Intel.dmg
• Apple Silicon (M1/M2/M3) → Docker Desktop Apple Silicon.dmg
```

**2. Install:**
```
Open .dmg file
        ↓
┌─────────────────────────────────────┐
│  Docker.app → Applications folder    │
│  [Drag and drop]                     │
└─────────────────────────────────────┘
        ↓
Applications → Double-click Docker
        ↓
Allow permissions when prompted
```

**3. Verify:**
```
Terminal (⌘ + Space, type "Terminal")
        ↓
$ docker --version
        ↓
✅ Docker version 24.0.0, build abc123
```

---

### STEP 2: Get the Project

#### Option A: Using Git (Recommended)

**Terminal/Command Prompt:**
```
# Navigate to where you want the project
cd Desktop
        ↓
# Clone repository
git clone https://github.com/vishnuas22/MasterX.git
        ↓
┌─────────────────────────────────────┐
│  Cloning into 'MasterX'...          │
│  remote: Enumerating objects...     │
│  remote: Counting objects... 100%   │
│  Receiving objects... 100%          │
│  Resolving deltas... 100%           │
│  ✅ Done                             │
└─────────────────────────────────────┘
        ↓
# Enter project folder
cd MasterX
```

#### Option B: Download Zip

**Browser:**
```
GitHub → https://github.com/vishnuas22/MasterX
        ↓
┌─────────────────────────────────────┐
│  Code ▼                              │
│  ├─ Clone                            │
│  ├─ Open with GitHub Desktop        │
│  └─ Download ZIP  👈 Click here      │
└─────────────────────────────────────┘
        ↓
Extract ZIP to Desktop/MasterX
        ↓
Terminal: cd Desktop/MasterX
```

---

### STEP 3: Verify Files

**Check you have these files:**
```
Terminal in MasterX folder:
$ ls -la
        ↓
✅ backend/
✅ frontend/
✅ docker-compose.dev.yml    👈 Important!
✅ docker-compose.prod.yml
✅ README.md
✅ DOCKER_BEGINNER_GUIDE.md
```

**Verify environment files:**
```
$ ls backend/.env
✅ backend/.env   (exists)

$ ls frontend/.env
✅ frontend/.env  (exists)
```

---

### STEP 4: Start Docker Desktop

#### Windows & Mac

**Look for Docker icon in system tray/menu bar:**
```
Windows (System Tray):        Mac (Menu Bar):
┌──────────────┐             ┌──────────────┐
│  🐳 Docker   │             │  🐳 Docker   │
└──────────────┘             └──────────────┘

Status:
❌ Docker is starting...  → Wait
✅ Docker is running      → Ready!
```

**Check in Docker Desktop app:**
```
┌─────────────────────────────────────────┐
│  🐳 Docker Desktop                       │
├─────────────────────────────────────────┤
│  Containers     Images     Volumes      │
│                                          │
│  Status: ✅ Docker is running           │
│                                          │
│  Engine: Running                         │
│  Kubernetes: Disabled                    │
│                                          │
└─────────────────────────────────────────┘
```

---

### STEP 5: Build & Start Services

**Terminal in MasterX folder:**

**Command 1 - Start Services:**
```bash
$ docker-compose -f docker-compose.dev.yml up -d
```

**What you'll see (first time):**
```
Creating network "masterx-network" ... done
        ↓
Pulling mongodb (mongo:7.0)...
7.0: Pulling from library/mongo
████████████████████████████ 100%
        ↓
Pulling backend (python:3.11-slim)...
████████████████████████████ 100%
        ↓
Pulling frontend (node:20-alpine)...
████████████████████████████ 100%
        ↓
Building backend...
Step 1/10 : FROM python:3.11-slim
Step 2/10 : WORKDIR /app
Step 3/10 : COPY requirements.txt .
Step 4/10 : RUN pip install -r requirements.txt
[████████████████████] 150/150 packages
        ↓
Building frontend...
Step 1/8 : FROM node:20-alpine
Step 2/8 : WORKDIR /app
Step 3/8 : COPY package.json yarn.lock .
Step 4/8 : RUN yarn install
[████████████████████] 70/70 packages
        ↓
Creating masterx-mongodb-dev  ... done ✅
Creating masterx-backend-dev  ... done ✅
Creating masterx-frontend-dev ... done ✅
```

**⏱️ Time Estimate:**
- First time: 5-10 minutes (downloading & building)
- Next times: 30-60 seconds (everything cached)

---

### STEP 6: Check Status

**Command:**
```bash
$ docker-compose -f docker-compose.dev.yml ps
```

**Expected Output:**
```
┌──────────────────────────────────────────────────────────┐
│ NAME                    STATUS           PORTS            │
├──────────────────────────────────────────────────────────┤
│ masterx-mongodb-dev     Up (healthy)     27017/tcp       │
│ masterx-backend-dev     Up (healthy)     8001/tcp        │
│ masterx-frontend-dev    Up (healthy)     3000/tcp        │
└──────────────────────────────────────────────────────────┘
```

**✅ All services should show "Up (healthy)"**

**❌ If any show "Restarting" or "unhealthy":**
```
Wait 1-2 minutes (ML models loading)
        ↓
Still failing?
        ↓
Check logs:
$ docker-compose -f docker-compose.dev.yml logs backend
```

---

### STEP 7: View Logs (Optional)

**To see what's happening:**

**Command:**
```bash
$ docker-compose -f docker-compose.dev.yml logs -f
```

**What you'll see:**
```
┌─────────────────────────────────────────────────────────┐
│ MongoDB Logs:                                            │
│ ✅ Waiting for connections on port 27017               │
│                                                          │
│ Backend Logs:                                            │
│ ⚠️  No GPU available, using CPU                         │
│ ✅ Emotion engine initialized                           │
│ ✅ Application startup complete                         │
│ ✅ Uvicorn running on http://0.0.0.0:8001              │
│                                                          │
│ Frontend Logs:                                           │
│ ✅ VITE ready in 214 ms                                 │
│ ✅ Local:   http://localhost:3000/                      │
└─────────────────────────────────────────────────────────┘

Press Ctrl+C to exit log view
```

---

### STEP 8: Access Application

#### Open Browser - Frontend

**URL:** http://localhost:3000

**What you should see:**
```
┌─────────────────────────────────────────────────────────┐
│  Browser Address Bar:                                    │
│  http://localhost:3000                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🎓 MasterX - AI Learning Platform                      │
│                                                          │
│  Dark background with purple gradient text:              │
│  "Learn with AI that understands your emotions"         │
│                                                          │
│  Two buttons:                                            │
│  ┌────────────────────┐  ┌───────────────┐            │
│  │ Get Started (white) │  │ Watch Demo    │            │
│  └────────────────────┘  └───────────────┘            │
│                                                          │
│  Stats: ⭐ 4.8/5  👥 10,000+  ❤️ 27                    │
│                                                          │
│  [Hero image with students]                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**✅ If you see this → Success!**

---

#### Open Browser - API Documentation

**URL:** http://localhost:8001/docs

**What you should see:**
```
┌─────────────────────────────────────────────────────────┐
│  Browser Address Bar:                                    │
│  http://localhost:8001/docs                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MasterX API - Swagger UI                               │
│                                                          │
│  Collapsible sections with colored boxes:               │
│                                                          │
│  📗 default                                              │
│  └─ GET /api/health (green)                             │
│  └─ GET /api/health/detailed (green)                    │
│                                                          │
│  🔐 Authentication                                       │
│  └─ POST /api/auth/register (blue)                      │
│  └─ POST /api/auth/login (blue)                         │
│  └─ GET /api/auth/me (green)                            │
│                                                          │
│  💬 Chat & Learning                                      │
│  └─ POST /api/v1/chat (blue)                            │
│  └─ GET /api/v1/chat/history/{session_id} (green)       │
│                                                          │
│  [... 51 total endpoints ...]                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**✅ If you see this → API is working!**

---

#### Test API Endpoint

**In Swagger UI (http://localhost:8001/docs):**

**Step 1:** Find `/api/health` endpoint
```
┌─────────────────────────────────────┐
│ GET /api/health                      │
│ [Click to expand]                    │
└─────────────────────────────────────┘
```

**Step 2:** Click "Try it out"
```
┌─────────────────────────────────────┐
│ GET /api/health                      │
│                                      │
│ [Try it out]  👈 Click this          │
└─────────────────────────────────────┘
```

**Step 3:** Click "Execute"
```
┌─────────────────────────────────────┐
│ Parameters                           │
│ (No parameters)                      │
│                                      │
│ [Execute]  👈 Click this             │
└─────────────────────────────────────┘
```

**Step 4:** See Response
```
┌─────────────────────────────────────┐
│ Server response                      │
│ Code: 200  ✅                        │
│                                      │
│ Response body:                       │
│ {                                    │
│   "status": "ok",                    │
│   "timestamp": "2025-11-19T...",    │
│   "version": "1.0.0"                 │
│ }                                    │
└─────────────────────────────────────┘
```

**✅ If you see this → Backend is working perfectly!**

---

### STEP 9: Test From Terminal

**Open new terminal window (keep services running):**

**Test backend health:**
```bash
$ curl http://localhost:8001/api/health
```

**Expected output:**
```json
{"status":"ok","timestamp":"2025-11-19T05:00:00.000000","version":"1.0.0"}
```

**Test frontend:**
```bash
$ curl -I http://localhost:3000
```

**Expected output:**
```
HTTP/1.1 200 OK
Content-Type: text/html
...
```

**✅ Both should return successful responses**

---

## 🎨 MAKING YOUR FIRST CHANGE

### Edit Frontend (See Live Changes)

**Step 1:** Open code editor
```
VSCode or Cursor:
File → Open Folder → Select MasterX
        ↓
File tree on left shows:
├─ backend/
├─ frontend/  👈 Expand this
│  └─ src/
│     └─ pages/
│        └─ Landing.tsx  👈 Open this
```

**Step 2:** Find the heading (around line 100)
```typescript
<h1 className="text-5xl">
  Learn with AI that
  <br />
  <span className="gradient-text">
    understands your emotions
  </span>
</h1>
```

**Step 3:** Change the text
```typescript
<h1 className="text-5xl">
  Learn with AI that
  <br />
  <span className="gradient-text">
    understands your emotions perfectly! 🎉
  </span>
</h1>
```

**Step 4:** Save file (Ctrl+S / Cmd+S)

**Step 5:** Watch browser auto-refresh!
```
Browser at http://localhost:3000
        ↓
[Auto-refreshing in 1-2 seconds...]
        ↓
✅ New text appears!
"understands your emotions perfectly! 🎉"
```

**🎉 That's hot reload in action!**

---

### Edit Backend (See Live Changes)

**Step 1:** Open backend file
```
File tree:
├─ backend/
│  └─ server.py  👈 Open this
```

**Step 2:** Find health endpoint (around line 470)
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**Step 3:** Add a message
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "Hello from MasterX! 👋"  # 👈 Add this
    }
```

**Step 4:** Save file (Ctrl+S / Cmd+S)

**Step 5:** Check logs (backend auto-restarts)
```
Terminal:
$ docker-compose -f docker-compose.dev.yml logs -f backend
        ↓
✅ Reloading...
✅ Application startup complete
```

**Step 6:** Test the change
```
Browser: http://localhost:8001/api/health
        ↓
{
  "status": "ok",
  "timestamp": "2025-11-19T...",
  "version": "1.0.0",
  "message": "Hello from MasterX! 👋"  ✅
}
```

**🎉 Backend hot reload works too!**

---

## 🛑 STOPPING THE APPLICATION

### Quick Stop (Keep Containers)

**Terminal:**
```bash
$ docker-compose -f docker-compose.dev.yml stop
```

**Visual feedback:**
```
Stopping masterx-frontend-dev  ... done ✅
Stopping masterx-backend-dev   ... done ✅
Stopping masterx-mongodb-dev   ... done ✅
```

**Docker Desktop:**
```
┌─────────────────────────────────────┐
│  Containers                          │
├─────────────────────────────────────┤
│  masterx-mongodb-dev    ⏸️ Stopped   │
│  masterx-backend-dev    ⏸️ Stopped   │
│  masterx-frontend-dev   ⏸️ Stopped   │
└─────────────────────────────────────┘
```

**To restart:**
```bash
$ docker-compose -f docker-compose.dev.yml start
```

---

### Complete Stop (Remove Containers)

**Terminal:**
```bash
$ docker-compose -f docker-compose.dev.yml down
```

**Visual feedback:**
```
Stopping masterx-frontend-dev  ... done
Stopping masterx-backend-dev   ... done
Stopping masterx-mongodb-dev   ... done
Removing masterx-frontend-dev  ... done ✅
Removing masterx-backend-dev   ... done ✅
Removing masterx-mongodb-dev   ... done ✅
Removing network masterx-network ... done ✅
```

**Docker Desktop:**
```
┌─────────────────────────────────────┐
│  Containers                          │
├─────────────────────────────────────┤
│  (Empty - all containers removed)    │
│                                      │
│  To start again:                     │
│  docker-compose up -d                │
└─────────────────────────────────────┘
```

---

## 📊 MONITORING IN DOCKER DESKTOP

### View Containers

**Docker Desktop → Containers:**
```
┌─────────────────────────────────────────────────────────┐
│  Containers / Apps                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📦 masterx                                              │
│  ├─ masterx-mongodb-dev     🟢 Running   27017:27017   │
│  ├─ masterx-backend-dev     🟢 Running   8001:8001     │
│  └─ masterx-frontend-dev    🟢 Running   3000:3000     │
│                                                          │
│  Actions: [Stop] [Restart] [Delete]                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Click any container to:**
- View logs (live streaming)
- Open terminal (bash/sh)
- View stats (CPU, memory)
- Inspect configuration

---

### View Logs in Docker Desktop

**Click container → Logs tab:**
```
┌─────────────────────────────────────────────────────────┐
│  masterx-backend-dev - Logs                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [2025-11-19 05:00:00] INFO: Starting MasterX...       │
│  [2025-11-19 05:00:01] INFO: Connecting to MongoDB...  │
│  [2025-11-19 05:00:02] INFO: Loading ML models...      │
│  [2025-11-19 05:00:15] INFO: ✅ Emotion engine ready   │
│  [2025-11-19 05:00:16] INFO: ✅ Application started    │
│  [2025-11-19 05:00:17] INFO: Uvicorn running on 8001   │
│                                                          │
│  [Auto-scrolling logs...]                               │
│                                                          │
│  ⏸️ [Pause]  📋 [Copy]  🗑️ [Clear]                      │
└─────────────────────────────────────────────────────────┘
```

---

### View Stats

**Click container → Stats tab:**
```
┌─────────────────────────────────────────────────────────┐
│  masterx-backend-dev - Stats                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CPU Usage:    [████░░░░░░] 40%                         │
│  Memory:       [████████░░] 4.2 GB / 8.0 GB            │
│  Network I/O:  ↓ 1.2 MB  ↑ 0.8 MB                      │
│  Block I/O:    Read: 245 MB  Write: 89 MB              │
│                                                          │
│  [Live updating graphs]                                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 DAILY WORKFLOW

### Morning - Start Work

**1. Open Docker Desktop**
```
Windows: Start Menu → Docker Desktop
Mac: Applications → Docker
        ↓
Wait for: "Docker is running" ✅
```

**2. Open Terminal**
```
Navigate to project:
$ cd ~/Desktop/MasterX
```

**3. Start Services**
```
$ docker-compose -f docker-compose.dev.yml up -d
        ↓
✅ Creating masterx-mongodb-dev  ... done
✅ Creating masterx-backend-dev  ... done
✅ Creating masterx-frontend-dev ... done
```

**4. Open Browser**
```
Frontend: http://localhost:3000
API Docs: http://localhost:8001/docs
```

**5. Open Code Editor**
```
$ code .   # VSCode
or
$ cursor . # Cursor
```

**✅ Ready to code!**

---

### During Work - Make Changes

**1. Edit files in VSCode/Cursor**
```
Save file (Ctrl+S / Cmd+S)
        ↓
Hot reload activates (1-3 seconds)
        ↓
Browser refreshes automatically
```

**2. View logs if needed**
```
$ docker-compose -f docker-compose.dev.yml logs -f backend
```

**3. Test API changes**
```
Browser: http://localhost:8001/docs
        ↓
Try out endpoint
        ↓
See response
```

---

### Evening - Stop Work

**Option 1: Keep running (resume tomorrow)**
```
Just close editor
Leave Docker running
Tomorrow: Containers auto-start
```

**Option 2: Stop containers**
```
$ docker-compose -f docker-compose.dev.yml stop
        ↓
✅ Stopped all services
Tomorrow: docker-compose start
```

**Option 3: Complete shutdown**
```
$ docker-compose -f docker-compose.dev.yml down
Docker Desktop → Quit
```

---

## 🚨 TROUBLESHOOTING VISUALS

### Problem: Services Won't Start

**Check Docker Desktop:**
```
┌─────────────────────────────────────┐
│  🐳 Docker Desktop                   │
├─────────────────────────────────────┤
│  Status: ❌ Docker is not running   │
│                                      │
│  [Start Docker]  👈 Click this       │
└─────────────────────────────────────┘
        ↓
Wait for green icon
        ↓
✅ Docker is running
        ↓
Try starting services again
```

---

### Problem: Port Already in Use

**Symptom:**
```
$ docker-compose -f docker-compose.dev.yml up -d
        ↓
❌ Error: bind: address already in use (port 3000)
```

**Solution - Find Process:**
```
Mac/Linux:
$ lsof -i :3000
        ↓
node    12345  user  ...
        ↓
$ kill -9 12345
        ↓
✅ Port freed

Windows:
> netstat -ano | findstr :3000
  TCP  0.0.0.0:3000  ...  12345
        ↓
> taskkill /PID 12345 /F
        ↓
✅ Port freed
```

---

### Problem: Backend Shows Unhealthy

**Check logs:**
```
$ docker-compose -f docker-compose.dev.yml logs backend
        ↓
Look for:
❌ Error: ... (error message)
        ↓
Common causes:
1. ML models still downloading → Wait 2 min
2. MongoDB not ready → Wait 1 min
3. Missing environment variable → Check .env
```

**View in Docker Desktop:**
```
Containers → masterx-backend-dev
        ↓
Status: 🔴 Unhealthy
        ↓
Logs tab: See error messages
        ↓
Restart: Right-click → Restart
```

---

## ✅ SUCCESS INDICATORS

### All Working Correctly

**Terminal check:**
```
$ docker-compose -f docker-compose.dev.yml ps
        ↓
All services: ✅ Up (healthy)
```

**Browser check:**
```
http://localhost:3000  → ✅ Shows landing page
http://localhost:8001/docs → ✅ Shows API docs
```

**Docker Desktop check:**
```
Containers: All 🟢 Running
Logs: No red errors
```

**Hot reload check:**
```
Edit file → Save → Browser updates (3 sec)
✅ Works!
```

---

## 🎉 CONGRATULATIONS!

You've successfully:
- ✅ Installed Docker
- ✅ Started MasterX with Docker
- ✅ Accessed frontend and backend
- ✅ Made code changes with hot reload
- ✅ Learned Docker Desktop interface
- ✅ Troubleshot common issues

**You're ready to develop with Docker!** 🚀

---

**Need more help?**
- Detailed guide: `DOCKER_BEGINNER_GUIDE.md`
- Quick commands: `DOCKER_QUICK_REFERENCE.md`
- Full docs: `DOCKER_SETUP_DOCUMENTATION.md`
