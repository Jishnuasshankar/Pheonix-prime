# MasterX - Quick Start for Local Development

## 🚀 5-Minute Setup Guide

### Prerequisites
- ✅ MongoDB installed and running
- ✅ Python 3.11+ with dependencies installed
- ✅ Node.js 18+ with Yarn installed

---

## Step 1: Configure Backend (30 seconds)

```bash
# Navigate to backend
cd /app/backend

# Verify .env has correct CORS settings
cat .env | grep CORS_ORIGINS
# Should show: CORS_ORIGINS=http://localhost:3000,http://localhost:5173,...

# If not, add:
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*
```

---

## Step 2: Configure Frontend (30 seconds)

```bash
# Navigate to frontend
cd /app/frontend

# Edit .env
nano .env

# ENSURE this line exists and is NOT commented:
VITE_BACKEND_URL=http://localhost:8001

# Save and exit (Ctrl+X, Y, Enter)
```

---

## Step 3: Start Services (2 minutes)

```bash
# Start MongoDB (if not running)
sudo supervisorctl start mongodb

# Start backend
sudo supervisorctl restart backend

# Wait for backend to initialize (important!)
sleep 15

# Verify backend is running
curl http://localhost:8001/api/health
# Should return: {"status":"ok",...}

# Start frontend
sudo supervisorctl restart frontend
# OR run directly:
cd /app/frontend && yarn dev
```

---

## Step 4: Access Application (10 seconds)

1. Open browser: **http://localhost:3000** (or **http://localhost:5173** for Vite)
2. Open browser console (F12) to see logs
3. Go to Signup page
4. Create test account:
   - Name: Test User
   - Email: test@example.com  
   - Password: TestPass123!

---

## ✅ Expected Console Output (Success)

```
📝 Starting signup process...
📡 Backend URL: http://localhost:8001
✓ Signup API call successful, tokens received
✓ Tokens stored in localStorage (synchronous)
✓ Tokens set in Zustand state
→ Fetching user profile...
✓ User profile fetched: {id: "...", email: "test@example.com", ...}
✓ User data adapted for frontend
✅ Signup complete! Welcome, Test User
```

After successful signup:
- Should redirect to `/app`
- User info visible in UI
- No errors in console

---

## ❌ Common Issues & Quick Fixes

### Issue: "Cannot connect to backend"

**Quick Fix:**
```bash
# Check if backend is running
sudo supervisorctl status backend

# If not running:
sudo supervisorctl restart backend
sleep 15

# Test backend
curl http://localhost:8001/api/health
```

---

### Issue: CORS Error

**Quick Fix:**
```bash
# Add to backend/.env:
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*

# Restart backend
sudo supervisorctl restart backend
```

---

### Issue: Frontend shows wrong backend URL

**Quick Fix:**
```bash
# 1. Set VITE_BACKEND_URL in frontend/.env
echo "VITE_BACKEND_URL=http://localhost:8001" > /app/frontend/.env

# 2. MUST restart frontend (Vite only reads .env on startup!)
sudo supervisorctl restart frontend
```

---

## 🔍 Verification Commands

```bash
# Check all services
sudo supervisorctl status

# Should show:
# backend    RUNNING
# frontend   RUNNING  
# mongodb    RUNNING

# Test backend health
curl http://localhost:8001/api/health

# Check backend logs
tail -50 /var/log/supervisor/backend.err.log

# Check frontend logs
tail -50 /var/log/supervisor/frontend.err.log
```

---

## 📱 Testing Checklist

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads without errors
- [ ] Can create new user (signup)
- [ ] Can login with created user
- [ ] Redirects to `/app` after auth
- [ ] User info visible in UI
- [ ] No CORS errors in console
- [ ] Token stored in localStorage

---

## 🆘 Need More Help?

See detailed documentation: `/app/LOCAL_DEVELOPMENT_FIX_DOCUMENTATION.md`

Common sections:
- Full troubleshooting guide
- Environment configuration explained
- Token flow details
- Security notes
- Testing recommendations

---

## 🎯 For Emergent Platform

To deploy on Emergent (not local):

1. Comment out `VITE_BACKEND_URL` in `frontend/.env`:
   ```bash
   # VITE_BACKEND_URL=
   ```

2. Keep `CORS_ORIGINS=*` in `backend/.env`

3. Deploy normally - platform handles routing automatically

---

**Last Updated:** 2025-11-18  
**Status:** ✅ Tested and working in both local and Emergent environments
