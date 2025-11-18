# MasterX Local Development Fix Documentation

## 📋 Overview

This document describes the critical fixes applied to resolve authentication and API connectivity issues between local development environments (VSCode, local machines) and the Emergent platform.

**Issue:** User signup/login worked on Emergent platform but failed in local development environments. Users would be created in MongoDB but the frontend would not load after successful authentication.

---

## 🔍 Root Cause Analysis

### Issue 1: Inconsistent API Base URL Configuration

**Problem:**
- Two different places defined base URLs with different logic:
  1. `/frontend/src/config/api.config.ts` - Used environment variable directly
  2. `/frontend/src/services/api/client.ts` - Had smart auto-detection
  
**Impact:**
- Could cause double-prefixing: `http://localhost:8001/http://localhost:8001/api/auth/register`
- Different behavior between local and Emergent environments
- Endpoints in `api.config.ts` created full URLs but `client.ts` also added baseURL

### Issue 2: Environment Variable Configuration

**Problem:**
- `VITE_BACKEND_URL` was commented out in `frontend/.env`
- Auto-detection logic was inconsistent
- No clear documentation on what to set for local vs Emergent

**Impact:**
- Local development couldn't find backend
- Network errors: "ERR_NETWORK" or "Connection refused"

### Issue 3: CORS Configuration

**Problem:**
- Backend CORS was set to wildcard `*` only
- Didn't explicitly list common local development ports
- Could cause CORS errors when browser is strict

**Impact:**
- Browser blocked requests from `localhost:3000` to `localhost:8001`
- Preflight OPTIONS requests failed

### Issue 4: Token Propagation Race Condition

**Problem:**
- Auth flow used 10ms timeout to wait for token to propagate
- Zustand state was set AFTER localStorage
- API interceptor might not have token when `getCurrentUser()` is called

**Impact:**
- User profile fetch failed
- Frontend showed "nothing loads" because user data never arrived
- Race condition was unreliable across different machines

### Issue 5: Poor Error Messages

**Problem:**
- Generic errors like "Login failed"
- No distinction between network errors and auth errors
- Hard to debug for users

**Impact:**
- Users couldn't identify if backend was down or if credentials were wrong

---

## ✅ Fixes Applied

### Fix 1: Unified API Base URL Strategy

**File:** `/frontend/src/config/api.config.ts`

**Changes:**
```typescript
// BEFORE (❌ Wrong):
const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
export const AUTH_ENDPOINTS = {
  REGISTER: `${API_BASE}/api/auth/register`,  // Full URL
  // ...
}

// AFTER (✅ Correct):
// Removed API_BASE completely
export const AUTH_ENDPOINTS = {
  REGISTER: '/api/auth/register',  // Relative path only
  LOGIN: '/api/auth/login',
  // ...
}
```

**Rationale:**
- All endpoints are now RELATIVE paths (start with `/`)
- Base URL is managed ONLY in `client.ts`
- Prevents double-prefixing issues
- Single source of truth for base URL configuration

**All endpoint categories fixed:**
- Authentication endpoints
- Chat endpoints
- Analytics endpoints
- Gamification endpoints
- Voice endpoints
- Personalization endpoints
- Content endpoints
- Spaced repetition endpoints
- Collaboration endpoints
- Health & monitoring endpoints
- Admin endpoints
- Budget endpoints

---

### Fix 2: Clear Environment Variable Configuration

**File:** `/frontend/.env`

**Changes:**
```bash
# BEFORE (❌ Unclear):
# VITE_BACKEND_URL=

# AFTER (✅ Clear):
# For LOCAL DEVELOPMENT (VSCode, etc.):
VITE_BACKEND_URL=http://localhost:8001

# For EMERGENT PLATFORM:
# Comment out or leave empty (uses relative URLs)
# VITE_BACKEND_URL=
```

**Instructions:**

**For Local Development:**
1. Set `VITE_BACKEND_URL=http://localhost:8001` in `frontend/.env`
2. Ensure backend is running on port 8001
3. Restart Vite dev server after changing `.env`

**For Emergent Platform:**
1. Comment out or remove `VITE_BACKEND_URL` line
2. OR set to empty string: `VITE_BACKEND_URL=`
3. Platform automatically routes `/api/*` to backend service

---

### Fix 3: Enhanced CORS Configuration

**File:** `/backend/.env`

**Changes:**
```bash
# BEFORE (❌ Only wildcard):
CORS_ORIGINS=*

# AFTER (✅ Explicit local ports + wildcard):
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*
```

**Rationale:**
- Explicitly allows common Vite ports (5173) and CRA ports (3000)
- Works with both `localhost` and `127.0.0.1`
- Maintains wildcard for Emergent platform compatibility
- More secure than wildcard alone

**Production Recommendation:**
```bash
# Replace wildcard with specific domains in production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

### Fix 4: Improved Token Propagation

**File:** `/frontend/src/store/authStore.ts`

**Changes in `login()` and `signup()` methods:**

```typescript
// BEFORE (❌ Race condition):
// Step 2: Set Zustand state
set({ accessToken, refreshToken, ... });

// Step 3: Store in localStorage
localStorage.setItem('jwt_token', response.access_token);

// Step 4: Wait 10ms (unreliable hack)
await new Promise(resolve => setTimeout(resolve, 10));

// Step 5: Fetch user profile
const apiUser = await authAPI.getCurrentUser();

// AFTER (✅ Reliable):
// Step 2: Store in localStorage FIRST (synchronous)
localStorage.setItem('jwt_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Step 3: Set Zustand state
set({ accessToken, refreshToken, ... });

// Step 4: Fetch user profile (no delay needed)
const apiUser = await authAPI.getCurrentUser();
```

**Rationale:**
- localStorage is synchronous - token is immediately available
- API interceptor checks localStorage as fallback (see `client.ts:89-94`)
- No race condition - token guaranteed to be available
- Removed unreliable 10ms timeout hack

---

### Fix 5: Better Error Handling and Logging

**File:** `/frontend/src/services/api/client.ts`

**Added network error detection:**
```typescript
} else if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
  console.error('❌ Network Error Details:', {
    message: error.message,
    code: error.code,
    config: { url, baseURL, method }
  });
  
  useUIStore.getState().showToast({
    type: 'error',
    message: 'Cannot connect to backend. Ensure backend is running on http://localhost:8001',
  });
}
```

**File:** `/frontend/src/store/authStore.ts`

**Added detailed error logging:**
```typescript
console.error('Error details:', {
  message: error.message,
  response: error.response?.data,
  status: error.response?.status,
  code: error.code,
});
```

**Improved error messages:**
```typescript
if (error.code === 'ERR_NETWORK') {
  errorMessage = 'Cannot connect to backend. Make sure backend is running on http://localhost:8001';
} else if (error.message?.includes('Network Error')) {
  errorMessage = 'Network error. Check if backend is running and CORS is configured.';
}
```

**Enhanced logging in auth flow:**
```typescript
console.log('🔐 Starting login process...');
console.log('📡 Backend URL:', import.meta.env.VITE_BACKEND_URL || 'auto-detected');
console.log('✓ Tokens stored in localStorage (synchronous)');
console.log('→ Fetching user profile...');
console.log('✅ Login complete! User:', user.name);
```

---

## 🚀 How to Use (Step by Step)

### For Local Development

#### Backend Setup

1. **Ensure MongoDB is running:**
   ```bash
   # Check if MongoDB is running
   sudo supervisorctl status mongodb
   # Should show: mongodb RUNNING
   ```

2. **Verify backend `.env` configuration:**
   ```bash
   # Check CORS settings
   cat /app/backend/.env | grep CORS_ORIGINS
   
   # Should show:
   # CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*
   ```

3. **Start/restart backend:**
   ```bash
   sudo supervisorctl restart backend
   
   # Wait for startup (10-15 seconds)
   sleep 15
   
   # Verify backend is responding
   curl http://localhost:8001/api/health
   # Should return: {"status":"ok","timestamp":"...","version":"1.0.0"}
   ```

#### Frontend Setup

1. **Configure frontend `.env`:**
   ```bash
   # Edit frontend/.env
   nano /app/frontend/.env
   
   # Set:
   VITE_BACKEND_URL=http://localhost:8001
   ```

2. **Install dependencies (if not already done):**
   ```bash
   cd /app/frontend
   yarn install
   ```

3. **Start frontend dev server:**
   ```bash
   # Option 1: Using supervisor (background)
   sudo supervisorctl restart frontend
   
   # Option 2: Using yarn directly (foreground with logs)
   cd /app/frontend
   yarn dev
   ```

4. **Access the app:**
   - Open browser: `http://localhost:3000` (or `http://localhost:5173` for Vite)
   - Open browser console (F12) to see detailed logs

#### Testing Authentication

1. **Open browser console** (F12 → Console tab)

2. **Navigate to Signup page**
   - Click "Sign Up" or go to `http://localhost:3000/signup`

3. **Fill out signup form:**
   - Name: Test User
   - Email: test@example.com
   - Password: TestPass123!

4. **Monitor console logs:**
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

5. **Verify success:**
   - Should redirect to main app (`/app`)
   - No errors in console
   - User info visible in UI

6. **Test login:**
   - Logout
   - Login with same credentials
   - Monitor console for similar log flow

---

### For Emergent Platform

#### Configuration

1. **Frontend `.env` - comment out backend URL:**
   ```bash
   # VITE_BACKEND_URL=
   # OR leave empty:
   VITE_BACKEND_URL=
   ```

2. **Backend `.env` - keep CORS permissive:**
   ```bash
   CORS_ORIGINS=*
   ```

3. **Deploy and test:**
   - Platform automatically routes `/api/*` to backend service
   - No manual URL configuration needed

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to backend"

**Symptoms:**
- Error: `ERR_NETWORK`
- Toast: "Cannot connect to backend. Ensure backend is running on http://localhost:8001"

**Diagnosis:**
```bash
# 1. Check if backend is running
sudo supervisorctl status backend

# 2. Check if port 8001 is listening
netstat -tuln | grep 8001
# OR
lsof -i :8001

# 3. Test backend directly
curl http://localhost:8001/api/health
```

**Solutions:**
1. **Backend not running:**
   ```bash
   sudo supervisorctl restart backend
   sleep 15  # Wait for startup
   ```

2. **Port conflict (8001 in use):**
   ```bash
   # Find process using port 8001
   lsof -i :8001
   # Kill it or change backend port
   ```

3. **Backend crashed on startup:**
   ```bash
   # Check error logs
   tail -50 /var/log/supervisor/backend.err.log
   
   # Common issues:
   # - Missing dependencies: pip install -r requirements.txt
   # - MongoDB not running: sudo supervisorctl start mongodb
   # - Port permission denied: Use sudo or change port
   ```

---

### Issue: "CORS policy blocking request"

**Symptoms:**
- Console error: `Access to XMLHttpRequest at 'http://localhost:8001/api/auth/login' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Diagnosis:**
```bash
# Check CORS configuration
cat /app/backend/.env | grep CORS_ORIGINS
```

**Solution:**
```bash
# Add your frontend port to CORS_ORIGINS
# Edit backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*

# Restart backend
sudo supervisorctl restart backend
```

---

### Issue: "User created but frontend doesn't load"

**Symptoms:**
- User saved in MongoDB
- Console shows successful signup API call
- Then error: "Failed to fetch user profile" or similar
- Frontend stuck on loading screen

**Diagnosis:**
```bash
# Check backend logs for /api/auth/me endpoint
tail -100 /var/log/supervisor/backend.out.log | grep "/api/auth/me"

# Check if token is in localStorage
# In browser console:
localStorage.getItem('jwt_token')
```

**Solutions:**

1. **Token not being sent:**
   - Clear browser cache and localStorage
   - Refresh page
   - Try signup again

2. **Backend rejecting token:**
   ```bash
   # Check backend logs for 401 errors
   tail -50 /var/log/supervisor/backend.err.log
   ```

3. **Database issue:**
   ```bash
   # Check MongoDB
   sudo supervisorctl status mongodb
   
   # Connect to MongoDB and verify user
   mongosh
   use masterx
   db.users.findOne({email: "test@example.com"})
   ```

---

### Issue: "Frontend shows different backend URL"

**Symptoms:**
- Console shows: `🔗 API Base URL: (empty - using relative URLs for production)`
- But you're in local development

**Diagnosis:**
```bash
# Check environment variable
cat /app/frontend/.env | grep VITE_BACKEND_URL
```

**Solution:**
```bash
# 1. Set VITE_BACKEND_URL explicitly
echo "VITE_BACKEND_URL=http://localhost:8001" >> /app/frontend/.env

# 2. CRITICAL: Restart Vite dev server
# Vite only reads .env on startup!
sudo supervisorctl restart frontend

# 3. Verify in browser console
# Should now show: "🔗 API Base URL: http://localhost:8001 (from VITE_BACKEND_URL)"
```

---

### Issue: "Mixed Content" errors

**Symptoms:**
- Error: "Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://localhost:8001/...'"

**Cause:**
- Frontend served over HTTPS
- Backend on HTTP (localhost:8001)
- Browser blocks mixed content

**Solution:**

**Option 1: Use HTTPS for both (recommended for production-like testing)**
```bash
# Set up HTTPS proxy for backend
# OR use ngrok/cloudflare tunnel
```

**Option 2: Disable mixed content blocking (development only)**
```bash
# Chrome: Add --disable-web-security flag (DEV ONLY!)
# Firefox: about:config → security.mixed_content.block_active_content = false
```

**Option 3: Use relative URLs**
```bash
# Comment out VITE_BACKEND_URL
# VITE_BACKEND_URL=

# Frontend will use relative URLs
# But backend must be on same domain (won't work locally)
```

---

## 📊 Verification Checklist

### Before Starting Development

- [ ] Backend is running: `sudo supervisorctl status backend` shows `RUNNING`
- [ ] MongoDB is running: `sudo supervisorctl status mongodb` shows `RUNNING`
- [ ] Backend health check works: `curl http://localhost:8001/api/health` returns 200 OK
- [ ] Frontend `.env` has `VITE_BACKEND_URL=http://localhost:8001`
- [ ] Backend `.env` has correct CORS settings
- [ ] Frontend dev server is running

### After Signup/Login

- [ ] Console shows: `✅ Login complete! User: <name>`
- [ ] No errors in browser console
- [ ] User data in localStorage: `localStorage.getItem('jwt_token')` returns token
- [ ] Redirected to `/app` route
- [ ] User info visible in UI
- [ ] No network errors in Network tab (F12 → Network)

### MongoDB Verification

```bash
# Connect to MongoDB
mongosh

# Switch to MasterX database
use masterx

# Check if user exists
db.users.findOne({email: "test@example.com"})

# Check if session exists
db.sessions.find({user_id: "..."})
```

---

## 🔧 File Changes Summary

### Modified Files

1. **`/app/frontend/.env`**
   - Set `VITE_BACKEND_URL=http://localhost:8001` for local dev
   - Added detailed comments explaining local vs Emergent config

2. **`/app/frontend/src/config/api.config.ts`**
   - Removed `API_BASE` constant
   - Changed all endpoints from full URLs to relative paths
   - Added documentation comments explaining the change

3. **`/app/frontend/src/services/api/client.ts`**
   - Enhanced `getBaseURL()` with better logging
   - Added network error detection (ERR_NETWORK)
   - Improved error messages for connection failures
   - Added detailed error logging in console

4. **`/app/frontend/src/store/authStore.ts`**
   - Fixed token propagation race condition
   - localStorage now set BEFORE Zustand state
   - Removed 10ms timeout hack
   - Added detailed console logging for debugging
   - Enhanced error messages with backend URL info
   - Better error categorization (network vs auth errors)

5. **`/app/backend/.env`**
   - Updated CORS_ORIGINS to explicitly list local ports
   - Added detailed comments explaining CORS configuration
   - Maintained wildcard for Emergent compatibility

6. **`/app/backend/middleware/simple_rate_limit.py`** (previous fix)
   - Fixed async event loop issue
   - Added `start_cleanup_task()` and `stop_cleanup_task()` methods
   - Deferred task creation until lifespan

7. **`/app/backend/server.py`** (previous fix)
   - Integrated rate limiter task start/stop with lifespan
   - Proper cleanup on shutdown

---

## 📝 Key Learnings

### Environment Variable Behavior

**CRITICAL:** Vite reads environment variables at BUILD TIME and DEV SERVER START TIME.

- Changing `.env` while dev server is running has NO EFFECT
- MUST restart dev server after changing `.env`
- Use `import.meta.env.VITE_*` to access variables
- Variables must start with `VITE_` prefix

### CORS in Development

- Wildcard `*` works but explicit origins are more secure
- Must include protocol: `http://localhost:3000` not `localhost:3000`
- Common Vite port: 5173
- Common CRA port: 3000

### Token Storage Best Practices

1. Store in localStorage first (synchronous)
2. Then update application state (Zustand, Redux, etc.)
3. API interceptors should check multiple sources (state → localStorage → sessionStorage)
4. Never rely on setTimeout for critical auth flow

### API Client Architecture

- Single base URL source (client.ts)
- All endpoints as relative paths
- Interceptors for token injection
- Fallback mechanisms for token retrieval

---

## 🎯 Testing Recommendations

### Manual Testing

1. **Test local development:**
   - Clear browser cache and localStorage
   - Start with fresh signup
   - Monitor console logs
   - Verify MongoDB entries

2. **Test Emergent platform:**
   - Deploy with commented `VITE_BACKEND_URL`
   - Test signup/login flow
   - Verify no CORS errors

3. **Test error scenarios:**
   - Backend down → Should show clear error
   - Wrong credentials → Should show "Invalid email or password"
   - Network timeout → Should show timeout message

### Automated Testing (Future)

Consider adding integration tests:
```typescript
describe('Auth Flow', () => {
  it('should signup, store tokens, and fetch user profile', async () => {
    // Test complete flow
  });
  
  it('should handle network errors gracefully', async () => {
    // Mock network failure
  });
  
  it('should handle token propagation correctly', async () => {
    // Verify localStorage → state → API call flow
  });
});
```

---

## 🚨 Security Notes

### Development vs Production

**Development (Current Config):**
- CORS wildcard allowed for convenience
- Explicit local ports for better debugging
- Detailed error messages
- Console logging enabled

**Production Recommendations:**
```bash
# Backend .env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ENABLE_HSTS=true

# Frontend .env
VITE_BACKEND_URL=  # Empty for relative URLs
VITE_ENVIRONMENT=production
```

### Token Security

- Tokens stored in localStorage (vulnerable to XSS)
- Consider httpOnly cookies for production
- Implement token rotation
- Add CSRF protection

### HTTPS in Production

- Always use HTTPS for frontend and backend
- Enable HSTS headers
- Use secure websockets (wss://)

---

## 📞 Support

### Getting Help

1. **Check console logs:**
   - Frontend: Browser console (F12)
   - Backend: `/var/log/supervisor/backend.err.log`

2. **Check this documentation:**
   - Review troubleshooting section
   - Follow verification checklist

3. **Common Issues:**
   - 90% of issues: Backend not running or VITE_BACKEND_URL not set
   - CORS errors: Update backend CORS_ORIGINS
   - "Nothing loads": Token propagation issue (check localStorage)

### Additional Resources

- FastAPI CORS docs: https://fastapi.tiangolo.com/tutorial/cors/
- Vite env variables: https://vitejs.dev/guide/env-and-mode.html
- Axios interceptors: https://axios-http.com/docs/interceptors

---

## ✅ Completion Checklist

After applying these fixes:

- [x] Fixed API base URL double-prefixing issue
- [x] Configured VITE_BACKEND_URL for local development
- [x] Updated CORS to explicitly allow local ports
- [x] Fixed token propagation race condition
- [x] Enhanced error handling and logging
- [x] Created comprehensive documentation
- [x] Tested signup flow
- [x] Tested login flow
- [x] Verified MongoDB storage
- [x] Verified token in localStorage
- [x] Verified user profile fetch

**Status:** ✅ All fixes applied and tested. Application now works in both local development and Emergent platform environments.

---

## 📅 Version History

- **v1.0** (2025-11-18): Initial fixes applied
  - Fixed API base URL configuration
  - Fixed CORS settings
  - Fixed token propagation
  - Enhanced error handling
  - Created documentation

---

## 🎉 Success Criteria

Your local development environment is working correctly when:

1. ✅ Backend responds to health checks
2. ✅ Frontend can signup new users
3. ✅ Tokens are stored in localStorage
4. ✅ User profile is fetched successfully
5. ✅ No CORS errors in console
6. ✅ No network errors in console
7. ✅ Redirect to `/app` after login
8. ✅ User data visible in UI

**All criteria should be met for both local development AND Emergent platform.**

---

End of Documentation
