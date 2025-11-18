# MasterX Local Development Setup Guide

**Last Updated:** November 18, 2025  
**Status:** ✅ Verified Working in Local, Emergent, and VSCode Environments

---

## 🎯 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- MongoDB running on localhost:27017
- Git

### 1. Clone Repository
```bash
git clone https://github.com/vishnuas22/MasterX.git
cd MasterX
```

### 2. Configure Environment Files

#### Backend Configuration (`backend/.env`)
```bash
# Database - MongoDB on localhost
MONGO_URL="mongodb://localhost:27017"
DB_NAME=masterx

# CORS - Allow local frontend origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# JWT Secret (use your own in production!)
JWT_SECRET_KEY=your-secret-key-here

# AI Provider API Keys (get from providers)
GROQ_API_KEY=your-groq-key-here
GEMINI_API_KEY=your-gemini-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Optional: External Services
SERPER_API_KEY=your-serper-key-here
ARTIFICIAL_ANALYSIS_API_KEY=your-aa-key-here
```

#### Frontend Configuration (`frontend/.env`)
```bash
# ⚡ CRITICAL: Backend URL Configuration ⚡
# This tells frontend where to find the backend API

# For LOCAL DEVELOPMENT (VSCode, terminal, etc.)
VITE_BACKEND_URL=http://localhost:8001

# For EMERGENT PLATFORM (leave empty or comment out)
# VITE_BACKEND_URL=

# WebSocket URL (for real-time features)
VITE_WS_URL=ws://localhost:8001

# Feature Flags
VITE_ENABLE_VOICE=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_GAMIFICATION=true

# Environment
VITE_ENVIRONMENT=development
```

### 3. Install Dependencies

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
yarn install
# or
npm install
```

### 4. Start Services

Open 3 terminal windows:

#### Terminal 1: MongoDB
```bash
mongod --bind_ip_all
```

#### Terminal 2: Backend
```bash
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 3: Frontend
```bash
cd frontend
yarn dev
# or
npm run dev
```

### 5. Verify Setup

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8001/api/health
   ```
   Should return: `{"status":"ok",...}`

2. **Open Browser:**
   - Frontend: http://localhost:3000 (or http://localhost:5173 if Vite)
   - Backend API: http://localhost:8001/api/health/detailed

3. **Test Registration:**
   - Click "Sign Up"
   - Fill in email, name, password
   - Should successfully create account and navigate to /app

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to backend" error

**Symptoms:**
- Frontend shows "ERR_NETWORK" or "Cannot connect to backend"
- Registration creates user in MongoDB but frontend hangs

**Solution:**
1. Verify backend is running:
   ```bash
   curl http://localhost:8001/api/health
   ```

2. Check `frontend/.env` has correct backend URL:
   ```bash
   VITE_BACKEND_URL=http://localhost:8001
   ```

3. Restart Vite dev server (env vars are read at startup):
   ```bash
   # Ctrl+C to stop, then:
   yarn dev
   ```

4. Check CORS configuration in `backend/.env`:
   ```bash
   # Must include your frontend origin
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

### Issue: User created but "nothing loads" after registration

**Root Cause:** Frontend API client prioritization issue (FIXED in this version)

**Previous Behavior:**
- `client.ts` prioritized hostname detection over `VITE_BACKEND_URL`
- Even if you set `VITE_BACKEND_URL=http://localhost:8001`, it was ignored
- This caused API calls to fail in some local environments

**Fixed Behavior:**
- `VITE_BACKEND_URL` now takes priority over hostname detection
- Explicitly configured URLs always win
- Users have full control via `.env` file

**Verify Fix:**
1. Open browser console (F12)
2. Look for: `🔗 API Base URL: http://localhost:8001 (from VITE_BACKEND_URL - user configuration)`
3. If you see "localhost detected" instead, restart Vite dev server

### Issue: WebSocket connection fails

**Symptoms:**
- Console shows "[WebSocket] Error" messages
- Real-time features don't work

**Solution:**
1. WebSocket errors are non-critical - app still works!
2. Check `frontend/.env` has WebSocket URL:
   ```bash
   VITE_WS_URL=ws://localhost:8001
   ```
3. Verify backend WebSocket endpoint:
   ```bash
   curl http://localhost:8001/api/ws
   ```

**Note:** WebSocket is optional for core functionality. App works in "degraded mode" without it.

### Issue: MongoDB connection failed

**Symptoms:**
- Backend logs show "Failed to connect to MongoDB"
- Health check shows database: "unhealthy"

**Solution:**
1. Start MongoDB:
   ```bash
   mongod --bind_ip_all
   ```

2. Verify MongoDB is running:
   ```bash
   mongo --eval "db.version()"
   ```

3. Check `backend/.env` has correct URL:
   ```bash
   MONGO_URL="mongodb://localhost:27017"
   ```

---

## 🌐 Environment-Specific Configuration

### Local Development (VSCode, Terminal)
```bash
# frontend/.env
VITE_BACKEND_URL=http://localhost:8001
VITE_WS_URL=ws://localhost:8001
```

### Emergent Platform
```bash
# frontend/.env - Leave empty or comment out
# VITE_BACKEND_URL=
# Platform auto-detects and uses Kubernetes ingress routing
```

### Custom Domain/IP
```bash
# frontend/.env
VITE_BACKEND_URL=http://192.168.1.100:8001
VITE_WS_URL=ws://192.168.1.100:8001
```

### Production Deployment
```bash
# frontend/.env
VITE_BACKEND_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com

# backend/.env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 📋 Configuration Priority

### API Client (`frontend/src/services/api/client.ts`)

**Priority Order (top to bottom):**
1. **Emergent Platform Detection** (highest)
   - If hostname includes `emergentagent.com`
   - Uses: Empty string (relative URLs, Kubernetes routing)

2. **VITE_BACKEND_URL** (user configuration)
   - If explicitly set in `.env`
   - Uses: Exact value from `.env`
   - **This is your control lever for local dev!**

3. **Localhost Detection** (fallback)
   - If hostname is `localhost` or `127.0.0.1`
   - Uses: `http://localhost:8001`

4. **Default** (last resort)
   - Uses: Empty string (relative URLs)

**Key Insight:** Set `VITE_BACKEND_URL` in your `.env` to override auto-detection!

### WebSocket Client (`frontend/src/services/websocket/native-socket.client.ts`)

**Matches API client priority:**
1. Emergent platform → `wss://` (current origin)
2. VITE_BACKEND_URL → Converts `http://` to `ws://`
3. Localhost → `ws://localhost:8001`
4. Default → `wss://` (current origin)

---

## 🧪 Testing the Fix

### Test 1: API Communication
```bash
# In browser console (F12), after starting frontend:
# Look for this log message:
🔗 API Base URL: http://localhost:8001 (from VITE_BACKEND_URL - user configuration)

# If you see "(localhost detected)" instead, you need to restart Vite:
# Ctrl+C in frontend terminal, then: yarn dev
```

### Test 2: Registration Flow
```bash
# 1. Open http://localhost:3000
# 2. Click "Sign Up"
# 3. Fill in:
#    - Email: test@example.com
#    - Name: Test User
#    - Password: TestPass123!
# 4. Click "Sign Up"
# 
# Expected behavior:
# ✅ User created in MongoDB (check with Compass or mongo shell)
# ✅ JWT tokens stored in localStorage
# ✅ Browser navigates to /app
# ✅ MainApp component loads (shows chat interface)
# ✅ Toast notification: "Welcome to MasterX, Test User! 🎉"
```

### Test 3: Token Verification
```bash
# In browser console (F12), after registration:
localStorage.getItem('jwt_token')
// Should show: "eyJhbGciOiJIUzI1NiIs..."

# Verify token is valid:
fetch('http://localhost:8001/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
  }
}).then(r => r.json()).then(console.log)
// Should show: {id: "...", email: "test@example.com", name: "Test User", ...}
```

---

## 📊 Expected Console Logs (Success)

### Backend Console
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✅ MongoDB connected: masterx
✅ All database collections initialized
🚀 MasterX server started successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001

📝 Registration attempt: test@example.com
✅ User registered: test@example.com
```

### Frontend Console (Browser F12)
```
🔗 API Base URL: http://localhost:8001 (from VITE_BACKEND_URL - user configuration)
🔐 Starting signup process...
📡 Backend URL: http://localhost:8001
→ POST /api/auth/register [Auth: ✗ No token]
← 201 /api/auth/register
✓ Signup API call successful, tokens received
✓ Tokens stored in localStorage (synchronous)
✓ Tokens set in Zustand state
→ Fetching user profile...
→ GET /api/auth/me [Auth: ✓]
← 200 /api/auth/me
✓ User profile fetched: {id: "...", email: "test@example.com", ...}
✓ User data adapted for frontend
✅ Signup complete! Welcome, Test User
```

---

## 🔒 Security Notes

### Development
- CORS allows all origins (`*`) - **OK for local dev**
- JWT secret is simple - **OK for local dev**
- MongoDB has no authentication - **OK for local dev**

### Production
- Set `CORS_ORIGINS` to specific domains only
- Use strong JWT secret (64+ characters)
- Enable MongoDB authentication
- Use HTTPS/WSS (not HTTP/WS)
- Enable rate limiting (already built-in)

---

## 🚀 Performance Tips

### Backend
- Use `--workers 4` for production:
  ```bash
  uvicorn server:app --workers 4 --host 0.0.0.0 --port 8001
  ```

### Frontend
- Production build:
  ```bash
  yarn build
  # Output: frontend/dist
  ```

### Database
- Add MongoDB indexes (already configured in code):
  ```javascript
  db.users.createIndex({ email: 1 }, { unique: true })
  db.sessions.createIndex({ user_id: 1 })
  ```

---

## 📞 Support

If you encounter issues not covered here:

1. Check backend logs for errors
2. Check browser console (F12) for frontend errors
3. Verify all environment variables are set correctly
4. Restart all services (backend, frontend, MongoDB)
5. Clear browser cache and localStorage
6. Try incognito/private mode to rule out extension conflicts

**Common Issue:** "I changed `.env` but nothing changed"
- **Solution:** Restart Vite dev server - env vars are read at startup, not runtime!

---

## 🎉 Success Checklist

- [ ] Backend health check returns `{"status":"ok"}`
- [ ] Frontend loads at http://localhost:3000
- [ ] Registration creates user in MongoDB
- [ ] Registration navigates to /app
- [ ] MainApp component loads successfully
- [ ] No console errors (warnings OK)
- [ ] Console shows "from VITE_BACKEND_URL - user configuration"
- [ ] JWT tokens stored in localStorage
- [ ] /api/auth/me returns user data with token

If all checked, congratulations! Your local development environment is working perfectly! 🎊

---

## 📝 Changes in This Version

### Fixed: Registration "Nothing Loads" Issue

**Problem:**
- Registration created user in MongoDB ✅
- But frontend hung with "nothing loads" ❌
- Worked in Emergent, failed in local VSCode ❌

**Root Cause:**
- `client.ts` prioritized hostname detection over `VITE_BACKEND_URL`
- Even when explicitly set, `.env` was ignored
- Frontend couldn't reach backend in some local setups

**Fix:**
1. Updated priority in `frontend/src/services/api/client.ts`:
   - VITE_BACKEND_URL now takes priority over hostname detection
   - User configuration always wins
   - Removed check that ignored `localhost:8001` in `.env`

2. Updated WebSocket client matching API client logic:
   - Same priority order as API client
   - Consistent behavior across all network operations

3. Enhanced error handling:
   - WebSocket errors are non-critical (app works without it)
   - Better console logging for debugging
   - Toast notifications only after multiple failures

**Result:**
- ✅ Works in ALL environments (local, VSCode, Emergent, custom)
- ✅ User has full control via `.env` configuration
- ✅ Explicit configuration takes precedence
- ✅ Registration completes successfully in local dev

---

**Last Verified:** November 18, 2025  
**Tested On:** macOS, Ubuntu, Windows (WSL), VSCode, Emergent Platform  
**Status:** ✅ Production Ready
