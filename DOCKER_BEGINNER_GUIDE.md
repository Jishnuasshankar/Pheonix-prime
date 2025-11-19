# 🐳 MasterX - Complete Beginner's Guide to Docker Setup

**For:** Complete Docker beginners  
**Works with:** VSCode, Cursor, or any code editor  
**Time needed:** 15-20 minutes (first time)  
**Difficulty:** ⭐⭐☆☆☆ Easy

---

## 📚 TABLE OF CONTENTS

1. [What is Docker? (Simple Explanation)](#1-what-is-docker-simple-explanation)
2. [Installing Docker](#2-installing-docker)
3. [Understanding the Files](#3-understanding-the-files)
4. [Setting Up Your Project](#4-setting-up-your-project)
5. [Running Your Project](#5-running-your-project)
6. [Accessing Your Application](#6-accessing-your-application)
7. [Making Changes (Development)](#7-making-changes-development)
8. [Stopping Your Application](#8-stopping-your-application)
9. [Common Issues & Solutions](#9-common-issues--solutions)
10. [Useful Commands Cheat Sheet](#10-useful-commands-cheat-sheet)

---

## 1. WHAT IS DOCKER? (Simple Explanation)

### 🤔 Imagine This:
You want to run MasterX on your computer. Normally, you'd need to:
- Install Python 3.11
- Install Node.js 20
- Install MongoDB
- Install 150+ Python packages
- Install 70+ JavaScript packages
- Configure everything correctly

**With Docker:** You just run ONE command, and everything works! ✨

### 🎁 Docker is Like a Gift Box:
- The **box** contains everything your app needs (Python, Node, MongoDB, all packages)
- The **box** works the same way on ANY computer (Windows, Mac, Linux)
- You don't need to install anything except Docker itself

### 📦 Three Main Concepts:

1. **Image** = Recipe/Blueprint (how to build your app)
2. **Container** = Running instance (your app actually running)
3. **Docker Compose** = Running multiple containers together (backend + frontend + database)

**Don't worry if this seems confusing - you'll understand as we go!** 😊

---

## 2. INSTALLING DOCKER

### For Windows Users 🪟

**Step 1:** Download Docker Desktop
```
Go to: https://www.docker.com/products/docker-desktop
Click: "Download for Windows"
```

**Step 2:** Install Docker Desktop
1. Run the downloaded file (Docker Desktop Installer.exe)
2. Follow the installation wizard
3. **Important:** If asked, enable WSL 2 (Windows Subsystem for Linux)
4. Restart your computer when prompted

**Step 3:** Verify Installation
1. Open Command Prompt or PowerShell
2. Type this command and press Enter:
```bash
docker --version
```

✅ **You should see:** `Docker version 24.0.0` (or higher)

**Step 4:** Start Docker Desktop
- Open Docker Desktop from Start Menu
- Wait for it to say "Docker is running" (green icon at bottom)

---

### For Mac Users 🍎

**Step 1:** Download Docker Desktop
```
Go to: https://www.docker.com/products/docker-desktop
Click: "Download for Mac"
Choose: Intel chip or Apple Silicon (M1/M2/M3)
```

**Step 2:** Install Docker Desktop
1. Open the downloaded .dmg file
2. Drag Docker icon to Applications folder
3. Open Docker from Applications
4. Allow permissions when asked

**Step 3:** Verify Installation
1. Open Terminal (⌘ + Space, type "Terminal")
2. Type this command:
```bash
docker --version
```

✅ **You should see:** `Docker version 24.0.0` (or higher)

---

### For Linux Users 🐧

**Ubuntu/Debian:**
```bash
# 1. Update package list
sudo apt-get update

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# 4. Log out and log back in (or restart)

# 5. Verify installation
docker --version
```

✅ **You should see:** `Docker version 24.0.0` (or higher)

---

## 3. UNDERSTANDING THE FILES

Before we run anything, let's understand what each file does:

### 📁 Your Project Structure
```
MasterX/
├── backend/                    # Python/FastAPI code
│   ├── Dockerfile             # 👈 Recipe for backend container
│   ├── requirements.txt       # 👈 Python packages list
│   └── server.py              # 👈 Main backend code
│
├── frontend/                   # React/TypeScript code
│   ├── Dockerfile             # 👈 Recipe for frontend container (production)
│   ├── Dockerfile.dev         # 👈 Recipe for frontend container (development)
│   ├── package.json           # 👈 JavaScript packages list
│   └── src/                   # 👈 Frontend code
│
├── docker-compose.dev.yml     # 👈 Recipe to run ALL services (development)
├── docker-compose.prod.yml    # 👈 Recipe to run ALL services (production)
└── .env                       # 👈 Configuration (API keys, secrets)
```

### 🎯 Which File Does What?

**Dockerfile** (backend/frontend):
- Like a cooking recipe
- Lists all ingredients (packages)
- Lists all steps to prepare your app
- Creates an "image" (blueprint)

**docker-compose.yml**:
- Runs multiple Dockerfiles together
- Connects backend + frontend + database
- Like a restaurant kitchen coordinator

**.env**:
- Stores secrets (API keys, passwords)
- Never commit this to GitHub!
- We'll create this in next section

---

## 4. SETTING UP YOUR PROJECT

### Step 1: Get the Code

**Option A - If you have Git:**
```bash
# Open Terminal/Command Prompt
# Navigate to where you want the project
cd Desktop  # or any folder you prefer

# Clone the repository
git clone https://github.com/vishnuas22/MasterX.git

# Go into the project folder
cd MasterX
```

**Option B - Download Zip:**
1. Go to: https://github.com/vishnuas22/MasterX
2. Click: Green "Code" button
3. Click: "Download ZIP"
4. Extract the ZIP file
5. Open Terminal/Command Prompt in that folder

---

### Step 2: Open in Your Code Editor

**VSCode:**
```bash
# If you're in the MasterX folder in terminal:
code .
```

**Cursor:**
```bash
cursor .
```

**Or just:** Open VSCode/Cursor → File → Open Folder → Select MasterX folder

---

### Step 3: Check Your Environment Files

The project already has `.env` files configured! Let's verify:

**Check Backend .env:**
```bash
# Look at backend/.env file
# It should have these important variables:
```

Open `backend/.env` in your editor and verify you see:
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=masterx

# AI Providers (already configured with test keys)
GROQ_API_KEY=gsk_yrVy...
GEMINI_API_KEY=AIza...
ELEVENLABS_API_KEY=sk_55...

# Security
JWT_SECRET_KEY=2c58...
```

✅ **Good news:** These are already configured! You can use them as-is for testing.

**Check Frontend .env:**

Open `frontend/.env` and verify:
```bash
# Backend URL (auto-detects, leave empty)
VITE_BACKEND_URL=

# Features (all enabled)
VITE_ENABLE_VOICE=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_GAMIFICATION=true
```

✅ **Perfect!** Everything is ready.

---

## 5. RUNNING YOUR PROJECT

Now the fun part! Let's start your application. 🚀

### Method 1: Using Docker Compose (RECOMMENDED - Easiest)

**Step 1:** Open Terminal in Project Root
```bash
# Make sure you're in the MasterX folder
# You should see docker-compose.dev.yml when you type:
ls  # or 'dir' on Windows
```

**Step 2:** Start Everything with ONE Command
```bash
docker-compose -f docker-compose.dev.yml up
```

**What this command does:**
- `-f docker-compose.dev.yml` = Use the development configuration
- `up` = Start all services (backend, frontend, database)

**You'll see lots of text scrolling by - this is normal!** It's:
1. Downloading Docker images (first time only, ~5-10 min)
2. Building your backend (installing Python packages)
3. Building your frontend (installing Node packages)
4. Starting MongoDB database
5. Starting all services

**Look for these success messages:**
```
✅ masterx-mongodb-dev     | Waiting for connections on port 27017
✅ masterx-backend-dev     | Application startup complete
✅ masterx-frontend-dev    | VITE ready in 214 ms
```

**Common Questions:**

❓ *"It's taking forever!"*
- **First time:** 5-10 minutes (downloading & building)
- **Next times:** 30-60 seconds (everything is cached)

❓ *"I see warnings in red/yellow"*
- **Yellow warnings:** Usually OK, can ignore
- **Red errors:** Check section 9 (Common Issues)

❓ *"Can I stop the scrolling text?"*
- **Yes!** Press `Ctrl+C` to stop
- **Better way:** Run in background (see next section)

---

### Method 2: Running in Background (Recommended)

Instead of seeing all the logs, run services in the background:

```bash
# Start all services in background (-d = detached mode)
docker-compose -f docker-compose.dev.yml up -d
```

**You'll see:**
```
✅ Network masterx-network created
✅ Container masterx-mongodb-dev started
✅ Container masterx-backend-dev started
✅ Container masterx-frontend-dev started
```

**To see logs when needed:**
```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs

# View logs from specific service
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend

# Follow logs in real-time (like tail -f)
docker-compose -f docker-compose.dev.yml logs -f
```

---

### Method 3: Build First, Then Run (Advanced)

If you want more control:

```bash
# Step 1: Build all images
docker-compose -f docker-compose.dev.yml build

# Step 2: Start services
docker-compose -f docker-compose.dev.yml up -d
```

**When to use this:**
- After changing Dockerfile
- After changing requirements.txt or package.json
- When things seem broken

---

### Verifying Everything Started Correctly

**Check Service Status:**
```bash
docker-compose -f docker-compose.dev.yml ps
```

**You should see:**
```
NAME                    STATUS              PORTS
masterx-mongodb-dev     Up (healthy)        27017/tcp
masterx-backend-dev     Up (healthy)        8001/tcp
masterx-frontend-dev    Up (healthy)        3000/tcp
```

✅ **All services should say "Up (healthy)"**

**If status shows "(unhealthy)" or "Restarting":**
- Wait 1-2 minutes (ML models are loading)
- Check logs: `docker-compose -f docker-compose.dev.yml logs backend`
- See section 9 for troubleshooting

---

## 6. ACCESSING YOUR APPLICATION

🎉 **Congratulations! Your app is running!** Now let's use it.

### 🌐 URLs You Can Access:

| Service | URL | What You'll See |
|---------|-----|-----------------|
| **Frontend** | http://localhost:3000 | Main application UI |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| **Backend Health** | http://localhost:8001/api/health | Health check JSON |

---

### Testing the Frontend (Main App)

**Step 1:** Open your browser

**Step 2:** Go to:
```
http://localhost:3000
```

**You should see:**
- ✅ Landing page with "Learn with AI that understands your emotions"
- ✅ Dark theme with purple gradient text
- ✅ "Get Started for Free" and "Watch Demo" buttons
- ✅ Navigation: Features, Pricing, Testimonials, Log in, Sign up

**Try These:**
1. Click "Sign up" - should show registration form
2. Click "Log in" - should show login form
3. Check if page is responsive (resize browser window)

---

### Testing the Backend (API)

**Step 1:** Open your browser

**Step 2:** Go to:
```
http://localhost:8001/docs
```

**You should see:**
- ✅ Swagger UI (interactive API documentation)
- ✅ List of all API endpoints (51 endpoints)
- ✅ Green boxes (GET), blue boxes (POST), etc.

**Try Testing an API:**

1. Find the **GET** `/api/health` endpoint
2. Click on it to expand
3. Click "Try it out" button
4. Click "Execute" button
5. You should see:
```json
{
  "status": "ok",
  "timestamp": "2025-11-19T...",
  "version": "1.0.0"
}
```

**Try Another API:**

1. Find **GET** `/api/v1/providers`
2. Click "Try it out" → "Execute"
3. You should see:
```json
{
  "providers": ["groq", "gemini"],
  "count": 2
}
```

✅ **If you see these responses, your backend is working perfectly!**

---

### Quick Health Check Command

You can also test from terminal:

```bash
# Test backend health
curl http://localhost:8001/api/health

# Or on Windows PowerShell:
Invoke-WebRequest http://localhost:8001/api/health
```

---

## 7. MAKING CHANGES (Development)

One of the best things about Docker development mode: **Hot Reload!** ⚡

This means you can edit code and see changes immediately without restarting.

### Editing Backend Code

**Step 1:** Open any backend file in your editor
```bash
# Example: Open main server file
# Location: backend/server.py
```

**Step 2:** Make a change (try this):
```python
# Find the health endpoint (around line 470)
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "Hello! I edited this!"  # 👈 ADD THIS LINE
    }
```

**Step 3:** Save the file (Ctrl+S / Cmd+S)

**Step 4:** Wait 2-3 seconds (backend auto-restarts)

**Step 5:** Refresh http://localhost:8001/api/health

✅ **You should see your new message!**

**Watch the logs to see reload:**
```bash
docker-compose -f docker-compose.dev.yml logs -f backend
# You'll see: "Reloading..."
```

---

### Editing Frontend Code

**Step 1:** Open any frontend file
```bash
# Example: Open landing page
# Location: frontend/src/pages/Landing.tsx
```

**Step 2:** Make a change (try this):
```typescript
// Find the main heading (around line 100)
<h1>
  Learn with AI that
  <br />
  <span className="gradient-text">
    understands your emotions
    {/* 👈 Change this text */}
  </span>
</h1>
```

**Step 3:** Save the file

**Step 4:** Your browser should auto-refresh in 1-2 seconds!

✅ **Changes appear immediately - no manual refresh needed!**

**Note:** If auto-refresh doesn't work:
- Manually refresh browser (F5)
- Check frontend logs: `docker-compose -f docker-compose.dev.yml logs frontend`

---

### Installing New Packages

**For Backend (Python):**

```bash
# Step 1: Add package to requirements.txt
echo "requests==2.31.0" >> backend/requirements.txt

# Step 2: Rebuild backend container
docker-compose -f docker-compose.dev.yml build backend

# Step 3: Restart backend
docker-compose -f docker-compose.dev.yml up -d backend
```

**For Frontend (JavaScript):**

```bash
# Step 1: Enter the frontend container
docker-compose -f docker-compose.dev.yml exec frontend sh

# Step 2: Install package with yarn
yarn add axios

# Step 3: Exit container
exit

# Frontend will auto-reload
```

**Alternative (easier):**
```bash
# Add to package.json manually, then:
docker-compose -f docker-compose.dev.yml build frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

---

### Viewing Logs for Debugging

**View all logs:**
```bash
docker-compose -f docker-compose.dev.yml logs
```

**View specific service logs:**
```bash
# Backend logs
docker-compose -f docker-compose.dev.yml logs backend

# Frontend logs
docker-compose -f docker-compose.dev.yml logs frontend

# Database logs
docker-compose -f docker-compose.dev.yml logs mongodb
```

**Follow logs in real-time:**
```bash
# Follow all logs
docker-compose -f docker-compose.dev.yml logs -f

# Follow backend only
docker-compose -f docker-compose.dev.yml logs -f backend
```

**View last 50 lines:**
```bash
docker-compose -f docker-compose.dev.yml logs --tail=50 backend
```

---

## 8. STOPPING YOUR APPLICATION

### Graceful Stop (Recommended)

**If running in foreground:**
```bash
# Press Ctrl+C in the terminal
# Then wait for services to stop gracefully
```

**If running in background:**
```bash
# Stop all services
docker-compose -f docker-compose.dev.yml stop

# This keeps containers, just stops them
```

**You'll see:**
```
Stopping masterx-frontend-dev  ... done
Stopping masterx-backend-dev   ... done
Stopping masterx-mongodb-dev   ... done
```

---

### Complete Shutdown (Clean Up)

**To stop AND remove containers:**
```bash
docker-compose -f docker-compose.dev.yml down
```

**What this does:**
- ✅ Stops all running containers
- ✅ Removes containers
- ✅ Removes networks
- ❌ **Keeps** volumes (your database data is safe!)

**To also remove volumes (⚠️ DELETES DATABASE DATA):**
```bash
docker-compose -f docker-compose.dev.yml down -v
```

**Use this when:**
- You want a completely fresh start
- Database has corrupted data
- Testing clean installation

---

### Restarting Services

**Restart all services:**
```bash
docker-compose -f docker-compose.dev.yml restart
```

**Restart specific service:**
```bash
# Restart just backend
docker-compose -f docker-compose.dev.yml restart backend

# Restart just frontend
docker-compose -f docker-compose.dev.yml restart frontend
```

---

### Quick Command Reference

```bash
# Start everything (foreground)
docker-compose -f docker-compose.dev.yml up

# Start everything (background)
docker-compose -f docker-compose.dev.yml up -d

# Stop everything (keep containers)
docker-compose -f docker-compose.dev.yml stop

# Stop and remove everything
docker-compose -f docker-compose.dev.yml down

# Restart everything
docker-compose -f docker-compose.dev.yml restart

# View status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

---

## 9. COMMON ISSUES & SOLUTIONS

### Issue 1: "Port 3000 is already in use"

**Problem:** Another app is using port 3000 (common with React apps)

**Solution 1 - Kill the other process:**

**On Mac/Linux:**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill it (replace PID with the number from above)
kill -9 PID
```

**On Windows:**
```cmd
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill it (replace PID with the number from above)
taskkill /PID PID /F
```

**Solution 2 - Change the port:**

Edit `docker-compose.dev.yml`:
```yaml
frontend:
  ports:
    - "3001:3000"  # Change 3000 to 3001
```

Then access at: http://localhost:3001

---

### Issue 2: "docker: command not found"

**Problem:** Docker is not installed or not in PATH

**Solution:**
1. Make sure Docker Desktop is installed (see Section 2)
2. Make sure Docker Desktop is running (check system tray/menu bar)
3. Restart your terminal after installation
4. On Linux, make sure you added user to docker group and logged out/in

**Verify Docker is running:**
```bash
docker --version
docker ps
```

---

### Issue 3: "Cannot connect to Docker daemon"

**Problem:** Docker Desktop is not running

**Solution:**
1. **Windows/Mac:** Open Docker Desktop app
2. Wait for the icon to show "Docker is running" (green)
3. **Linux:** Start Docker service:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

### Issue 4: Backend shows "unhealthy" status

**Problem:** Backend is taking long to start (ML models loading)

**Solution:**
```bash
# Wait 1-2 minutes for ML models to download
# Check backend logs to see progress:
docker-compose -f docker-compose.dev.yml logs backend

# Look for:
# "✅ Emotion engine initialized"
# "Application startup complete"
```

**If still failing after 5 minutes:**
```bash
# Rebuild backend
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache backend
docker-compose -f docker-compose.dev.yml up -d
```

---

### Issue 5: "Out of disk space" error

**Problem:** Docker images/containers using too much space

**Solution:**

**Check disk usage:**
```bash
docker system df
```

**Clean up unused images/containers:**
```bash
# Remove unused images/containers
docker system prune

# Remove everything (⚠️ removes all Docker data)
docker system prune -a
```

**Then rebuild:**
```bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

---

### Issue 6: "Permission denied" error (Linux)

**Problem:** User not in docker group

**Solution:**
```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# OR restart your computer

# Verify it worked
groups | grep docker
```

---

### Issue 7: Frontend shows blank page or errors

**Problem:** JavaScript build error or network issue

**Solution 1 - Check frontend logs:**
```bash
docker-compose -f docker-compose.dev.yml logs frontend
```

**Solution 2 - Rebuild frontend:**
```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build --no-cache frontend
docker-compose -f docker-compose.dev.yml up -d
```

**Solution 3 - Clear browser cache:**
- Press Ctrl+Shift+R (or Cmd+Shift+R on Mac)
- Or open browser DevTools → Network tab → Disable cache

**Solution 4 - Check if backend is running:**
```bash
# Backend should be healthy
docker-compose -f docker-compose.dev.yml ps backend

# Test backend directly
curl http://localhost:8001/api/health
```

---

### Issue 8: "Build failed" error

**Problem:** Error during image build

**Solution:**

**For backend build errors:**
```bash
# Clean build without cache
docker-compose -f docker-compose.dev.yml build --no-cache backend

# If still failing, check requirements.txt syntax
cat backend/requirements.txt
```

**For frontend build errors:**
```bash
# Clean build without cache
docker-compose -f docker-compose.dev.yml build --no-cache frontend

# If still failing, check package.json syntax
cat frontend/package.json
```

---

### Issue 9: Database connection errors

**Problem:** Backend can't connect to MongoDB

**Solution:**

**Step 1 - Check MongoDB is running:**
```bash
docker-compose -f docker-compose.dev.yml ps mongodb
# Should show "Up (healthy)"
```

**Step 2 - Check MongoDB logs:**
```bash
docker-compose -f docker-compose.dev.yml logs mongodb
# Look for: "Waiting for connections on port 27017"
```

**Step 3 - Restart MongoDB:**
```bash
docker-compose -f docker-compose.dev.yml restart mongodb
```

**Step 4 - If still failing, recreate:**
```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

---

### Issue 10: Changes not showing (hot reload not working)

**Problem:** Code changes not reflected in running app

**For Backend:**
```bash
# Backend should auto-reload, check logs:
docker-compose -f docker-compose.dev.yml logs -f backend
# You should see "Reloading..." when you save files

# If not working, restart backend:
docker-compose -f docker-compose.dev.yml restart backend
```

**For Frontend:**
```bash
# Check if Vite is watching files:
docker-compose -f docker-compose.dev.yml logs frontend
# Look for: "VITE ready"

# Hard refresh browser:
Ctrl+Shift+R (or Cmd+Shift+R on Mac)

# If still not working, restart frontend:
docker-compose -f docker-compose.dev.yml restart frontend
```

---

## 10. USEFUL COMMANDS CHEAT SHEET

### Starting & Stopping

```bash
# Start all services (background)
docker-compose -f docker-compose.dev.yml up -d

# Start all services (see logs)
docker-compose -f docker-compose.dev.yml up

# Stop all services
docker-compose -f docker-compose.dev.yml stop

# Stop and remove containers
docker-compose -f docker-compose.dev.yml down

# Restart all services
docker-compose -f docker-compose.dev.yml restart

# Restart one service
docker-compose -f docker-compose.dev.yml restart backend
```

---

### Viewing Information

```bash
# View service status
docker-compose -f docker-compose.dev.yml ps

# View all logs
docker-compose -f docker-compose.dev.yml logs

# View logs from one service
docker-compose -f docker-compose.dev.yml logs backend

# Follow logs in real-time
docker-compose -f docker-compose.dev.yml logs -f

# View last 50 lines
docker-compose -f docker-compose.dev.yml logs --tail=50 backend
```

---

### Building & Rebuilding

```bash
# Build all images
docker-compose -f docker-compose.dev.yml build

# Build without cache (clean build)
docker-compose -f docker-compose.dev.yml build --no-cache

# Build specific service
docker-compose -f docker-compose.dev.yml build backend

# Build and start
docker-compose -f docker-compose.dev.yml up -d --build
```

---

### Executing Commands Inside Containers

```bash
# Open bash shell in backend container
docker-compose -f docker-compose.dev.yml exec backend bash

# Open shell in frontend container
docker-compose -f docker-compose.dev.yml exec frontend sh

# Run a command in backend
docker-compose -f docker-compose.dev.yml exec backend python -c "print('Hello')"

# Install package in frontend
docker-compose -f docker-compose.dev.yml exec frontend yarn add axios
```

---

### Cleaning Up

```bash
# Remove containers and networks
docker-compose -f docker-compose.dev.yml down

# Remove containers, networks, and volumes (⚠️ deletes data)
docker-compose -f docker-compose.dev.yml down -v

# Remove all unused Docker data
docker system prune

# Remove everything including images (⚠️ full cleanup)
docker system prune -a
```

---

### Debugging

```bash
# View backend logs
docker-compose -f docker-compose.dev.yml logs backend

# View frontend logs
docker-compose -f docker-compose.dev.yml logs frontend

# View database logs
docker-compose -f docker-compose.dev.yml logs mongodb

# Check which ports are in use
docker-compose -f docker-compose.dev.yml ps

# Inspect a container
docker inspect masterx-backend-dev

# View disk usage
docker system df
```

---

## 11. NEXT STEPS

### 🎉 You Did It!

You now have MasterX running locally with Docker! Here's what you can do next:

### 1. Explore the Application

**Frontend:**
- Try registering a user at http://localhost:3000
- Test the chat interface
- Check emotion detection
- Explore gamification features

**Backend:**
- Test all 51 API endpoints at http://localhost:8001/docs
- Try the interactive API testing
- Check health monitoring

---

### 2. Make Your Own Changes

**Try These Exercises:**

**Easy:**
- Change text on landing page
- Modify button colors
- Add your name to footer

**Medium:**
- Create a new API endpoint
- Add a new frontend component
- Modify emotion detection thresholds

**Advanced:**
- Add a new AI provider
- Implement new gamification feature
- Create custom analytics dashboard

---

### 3. Learn More About Docker

**Recommended Resources:**
- Docker official docs: https://docs.docker.com/get-started/
- Docker Compose docs: https://docs.docker.com/compose/
- Docker best practices: https://docs.docker.com/develop/dev-best-practices/

**Key Concepts to Learn:**
- Images vs Containers
- Volumes (data persistence)
- Networks (service communication)
- Multi-stage builds
- Docker Hub (image registry)

---

### 4. Read Project Documentation

**Start Here:**
- `README.md` - Project overview
- `1.PROJECT_SUMMARY.md` - What's been built
- `AGENTS.md` - Backend development guide
- `AGENTS_FRONTEND.md` - Frontend development guide
- `DOCKER_SETUP_DOCUMENTATION.md` - Advanced Docker info

---

### 5. Contribute to the Project

**Want to contribute?**
1. Fork the repository on GitHub
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 12. TIPS FOR WORKING WITH DOCKER

### 💡 Pro Tips

**1. Use Background Mode by Default**
```bash
# Always use -d flag for development
docker-compose -f docker-compose.dev.yml up -d
```

**2. Check Logs Regularly**
```bash
# Get in the habit of checking logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

**3. Restart When Confused**
```bash
# When something seems wrong, just restart
docker-compose -f docker-compose.dev.yml restart
```

**4. Clean Up Regularly**
```bash
# Once a week, clean up unused images
docker system prune
```

**5. Keep Docker Desktop Running**
- Always run Docker Desktop when working on the project
- Check the icon - should show "Docker is running"

---

### ⚡ Speed Tips

**1. Use Docker Compose Aliases**

**On Mac/Linux (add to ~/.bashrc or ~/.zshrc):**
```bash
alias dcu="docker-compose -f docker-compose.dev.yml up -d"
alias dcd="docker-compose -f docker-compose.dev.yml down"
alias dcr="docker-compose -f docker-compose.dev.yml restart"
alias dcl="docker-compose -f docker-compose.dev.yml logs -f"
alias dcp="docker-compose -f docker-compose.dev.yml ps"
```

**On Windows PowerShell (add to $PROFILE):**
```powershell
function dcu { docker-compose -f docker-compose.dev.yml up -d }
function dcd { docker-compose -f docker-compose.dev.yml down }
function dcr { docker-compose -f docker-compose.dev.yml restart }
function dcl { docker-compose -f docker-compose.dev.yml logs -f }
function dcp { docker-compose -f docker-compose.dev.yml ps }
```

**Then you can just type:**
```bash
dcu     # Start services
dcl     # View logs
dcd     # Stop services
```

---

**2. Use VSCode Docker Extension**
- Install "Docker" extension by Microsoft
- View containers, images, networks in sidebar
- Right-click containers for actions
- View logs without terminal

---

### 🔒 Security Tips

**1. Never commit .env files**
```bash
# Already in .gitignore, but double-check:
git status
# Should NOT show .env files
```

**2. Use different API keys for dev/prod**
- Development: Test API keys (limited quota)
- Production: Real API keys (with monitoring)

**3. Change default passwords**
```bash
# In docker-compose.dev.yml, change:
MONGO_ROOT_PASSWORD: "your_secure_password_here"
JWT_SECRET_KEY: "generate_new_secret"
```

**4. Keep Docker Desktop updated**
- Check for updates regularly
- Security patches are important

---

### 📊 Performance Tips

**1. Allocate enough RAM to Docker**
- Docker Desktop → Settings → Resources
- Recommended: 8GB RAM for development
- Minimum: 4GB RAM

**2. Enable BuildKit (faster builds)**
```bash
# Add to ~/.bashrc or ~/.zshrc
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

**3. Use Docker's built-in caching**
- Don't use `--no-cache` unless necessary
- Let Docker reuse layers when possible

---

## 13. FREQUENTLY ASKED QUESTIONS

### ❓ Do I need to install Python/Node.js?

**No!** That's the beauty of Docker. Everything runs inside containers. You only need Docker Desktop.

---

### ❓ Will Docker slow down my computer?

**It depends:**
- Docker needs 4-8GB RAM
- Backend ML models need 4-6GB RAM when running
- If your computer has 16GB+ RAM: No problem
- If your computer has 8GB RAM: Might be slow
- If your computer has 4GB RAM: Will struggle

---

### ❓ Can I use Docker with WSL2 on Windows?

**Yes! Recommended for Windows users.**
- Better performance than Hyper-V
- More Linux-compatible
- Follow Docker Desktop instructions to enable WSL2

---

### ❓ How do I update my code?

**If you're editing code locally:**
- Just save the file - hot reload will update automatically

**If you pulled new code from Git:**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

---

### ❓ Can I use this in production?

**Yes, but use production configuration:**
```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

**Changes in production:**
- No hot reload (static builds)
- 4 backend workers (vs 1 in dev)
- Nginx reverse proxy
- Strict security settings
- Resource limits

---

### ❓ Where is my database data stored?

**In Docker volumes:**
```bash
# View all volumes
docker volume ls

# Inspect volume
docker volume inspect masterx_mongodb_data
```

**To backup database:**
```bash
# Export database
docker-compose -f docker-compose.dev.yml exec mongodb mongodump --out=/tmp/backup

# Copy from container to your computer
docker cp masterx-mongodb-dev:/tmp/backup ./mongodb-backup
```

---

### ❓ Can I use a different database?

**Yes, but requires changes:**
1. Modify `docker-compose.dev.yml` (replace MongoDB service)
2. Update backend database connection code
3. Change MONGO_URL environment variable

---

### ❓ How do I debug inside a container?

**Option 1 - Use logs:**
```bash
docker-compose -f docker-compose.dev.yml logs -f backend
```

**Option 2 - Enter container:**
```bash
# Open bash in container
docker-compose -f docker-compose.dev.yml exec backend bash

# Now you can run Python commands
python
>>> import sys
>>> print(sys.version)
```

**Option 3 - Use VSCode Remote Containers:**
- Install "Remote - Containers" extension
- Attach to running container
- Debug code directly in container

---

### ❓ Can I run just one service?

**Yes:**
```bash
# Start only backend (and MongoDB dependency)
docker-compose -f docker-compose.dev.yml up -d backend

# Start only frontend
docker-compose -f docker-compose.dev.yml up -d frontend

# Start only database
docker-compose -f docker-compose.dev.yml up -d mongodb
```

---

### ❓ How do I reset everything?

**Complete reset (deletes all data):**
```bash
# Stop everything
docker-compose -f docker-compose.dev.yml down -v

# Remove all images
docker system prune -a

# Start fresh
docker-compose -f docker-compose.dev.yml up -d
```

---

## 14. GETTING HELP

### 🆘 Where to Get Help

**1. Check This Guide First**
- Review Section 9: Common Issues & Solutions
- Search for your error message (Ctrl+F)

**2. Check Logs**
```bash
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend
```

**3. Docker Documentation**
- Official docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Best practices: https://docs.docker.com/develop/

**4. Project Documentation**
- `README.md` - Project overview
- `DOCKER_SETUP_DOCUMENTATION.md` - Detailed Docker guide
- `DOCKER_QUICKSTART.md` - Quick reference

**5. Community Resources**
- Docker Community Slack
- Stack Overflow (tag: docker)
- Docker Forums: https://forums.docker.com/

**6. Ask for Help**
- Create GitHub issue with:
  - Your operating system
  - Docker version (`docker --version`)
  - Error message or logs
  - Steps you've tried

---

## 15. CONCLUSION

### 🎉 You're Ready!

You now know how to:
- ✅ Install Docker
- ✅ Understand Docker concepts
- ✅ Run MasterX with Docker
- ✅ Make code changes with hot reload
- ✅ View logs and debug
- ✅ Stop and start services
- ✅ Troubleshoot common issues

### 🚀 What's Next?

1. **Start coding:** Make your own changes to the app
2. **Explore features:** Try all the APIs and UI components
3. **Read docs:** Learn about the architecture
4. **Contribute:** Add new features or fix bugs
5. **Deploy:** Use production Docker setup

---

### 💬 Final Tips

**Remember:**
- Docker makes development easier, not harder
- First time is slow, then it's fast
- When stuck, restart everything (it works!)
- Check logs when debugging
- Ask for help if needed

**You've got this!** Happy coding! 🎉

---

**Last Updated:** November 19, 2025  
**Created By:** E1 AI Agent  
**For:** MasterX Project  
**Difficulty:** ⭐⭐☆☆☆ Beginner-Friendly
