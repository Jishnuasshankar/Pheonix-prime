/**
 * API Endpoints Configuration
 * 
 * Matches backend server.py endpoints exactly
 * 
 * CRITICAL: All endpoints are RELATIVE paths (start with /)
 * The base URL is configured in client.ts and automatically injected
 * 
 * DO NOT add base URL here - it causes double-prefixing issues:
 * ❌ Wrong: `${API_BASE}/api/auth/register` → http://localhost:8001/api/auth/register
 * ✅ Right: '/api/auth/register' → Gets baseURL from client.ts
 * 
 * This ensures compatibility across environments:
 * - Local: Uses http://localhost:8001 from client.ts
 * - Emergent: Uses relative URLs (Kubernetes ingress handles routing)
 */

// NO API_BASE - endpoints are relative paths only!

// ============================================================================
// AUTHENTICATION ENDPOINTS
// ============================================================================

export const AUTH_ENDPOINTS = {
  REGISTER: '/api/auth/register',
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
  REFRESH: '/api/auth/refresh',
  ME: '/api/auth/me',
} as const;

// ============================================================================
// CHAT ENDPOINTS
// ============================================================================

export const CHAT_ENDPOINTS = {
  SEND_MESSAGE: '/api/v1/chat',
  GET_HISTORY: (sessionId: string) => `/api/v1/chat/history/${sessionId}`,
  DELETE_SESSION: (sessionId: string) => `/api/v1/chat/session/${sessionId}`,
} as const;

// ============================================================================
// ANALYTICS ENDPOINTS
// ============================================================================

export const ANALYTICS_ENDPOINTS = {
  DASHBOARD: (userId: string) => `/api/v1/analytics/dashboard/${userId}`,
  PERFORMANCE: (userId: string, daysBack = 30) => 
    `/api/v1/analytics/performance/${userId}?days_back=${daysBack}`,
  EMOTIONS: (userId: string, days = 7) => 
    `/api/v1/analytics/emotions/${userId}?days=${days}`,
  TOPICS: (userId: string) => `/api/v1/analytics/topics/${userId}`,
  VELOCITY: (userId: string) => `/api/v1/analytics/velocity/${userId}`,
  SESSIONS: (userId: string) => `/api/v1/analytics/sessions/${userId}`,
  INSIGHTS: (userId: string) => `/api/v1/analytics/insights/${userId}`,
} as const;

// ============================================================================
// GAMIFICATION ENDPOINTS
// ============================================================================

export const GAMIFICATION_ENDPOINTS = {
  STATS: (userId: string) => `/api/v1/gamification/stats/${userId}`,
  LEADERBOARD: (timeRange: string = 'weekly') => 
    `/api/v1/gamification/leaderboard?time_range=${timeRange}`,
  ACHIEVEMENTS: '/api/v1/gamification/achievements',
  RECORD_ACTIVITY: '/api/v1/gamification/record-activity',
  STREAK: (userId: string) => `/api/v1/gamification/streak/${userId}`,
} as const;

// ============================================================================
// VOICE ENDPOINTS
// ============================================================================

export const VOICE_ENDPOINTS = {
  TRANSCRIBE: '/api/v1/voice/transcribe',
  SYNTHESIZE: '/api/v1/voice/synthesize',
  ASSESS_PRONUNCIATION: '/api/v1/voice/assess-pronunciation',
  CHAT: '/api/v1/voice/chat',
  VOICES: '/api/v1/voice/voices',
} as const;

// ============================================================================
// PERSONALIZATION ENDPOINTS
// ============================================================================

export const PERSONALIZATION_ENDPOINTS = {
  PROFILE: (userId: string) => `/api/v1/personalization/profile/${userId}`,
  RECOMMENDATIONS: (userId: string) => 
    `/api/v1/personalization/recommendations/${userId}`,
  LEARNING_PATH: (userId: string, topic: string) => 
    `/api/v1/personalization/learning-path/${userId}/${topic}`,
} as const;

// ============================================================================
// CONTENT ENDPOINTS
// ============================================================================

export const CONTENT_ENDPOINTS = {
  NEXT: (userId: string) => `/api/v1/content/next/${userId}`,
  SEQUENCE: (userId: string, topic: string, nItems = 10) => 
    `/api/v1/content/sequence/${userId}/${topic}?n_items=${nItems}`,
  SEARCH: (query: string, nResults = 5) => 
    `/api/v1/content/search?query=${encodeURIComponent(query)}&n_results=${nResults}`,
} as const;

// ============================================================================
// SPACED REPETITION ENDPOINTS
// ============================================================================

export const SPACED_REPETITION_ENDPOINTS = {
  DUE_CARDS: (userId: string, limit = 20, includeNew = true) => 
    `/api/v1/spaced-repetition/due-cards/${userId}?limit=${limit}&include_new=${includeNew}`,
  CREATE_CARD: '/api/v1/spaced-repetition/create-card',
  REVIEW_CARD: '/api/v1/spaced-repetition/review-card',
  STATS: (userId: string) => `/api/v1/spaced-repetition/stats/${userId}`,
} as const;

// ============================================================================
// COLLABORATION ENDPOINTS
// ============================================================================

export const COLLABORATION_ENDPOINTS = {
  FIND_PEERS: '/api/v1/collaboration/find-peers',
  CREATE_SESSION: '/api/v1/collaboration/create-session',
  JOIN_SESSION: '/api/v1/collaboration/join-session',
  SEND_MESSAGE: '/api/v1/collaboration/send-message',
} as const;

// ============================================================================
// HEALTH & MONITORING ENDPOINTS
// ============================================================================

export const HEALTH_ENDPOINTS = {
  BASIC: '/api/health',
  DETAILED: '/api/health/detailed',
  PROVIDERS: '/api/v1/providers',
  MODEL_STATUS: '/api/v1/system/model-status',
} as const;

// ============================================================================
// ADMIN ENDPOINTS
// ============================================================================

export const ADMIN_ENDPOINTS = {
  COSTS: '/api/v1/admin/costs',
  PERFORMANCE: '/api/v1/admin/performance',
  CACHE: '/api/v1/admin/cache',
  PRODUCTION_READINESS: '/api/v1/admin/production-readiness',
  SYSTEM_STATUS: '/api/v1/admin/system/status',
} as const;

// ============================================================================
// BUDGET ENDPOINTS
// ============================================================================

export const BUDGET_ENDPOINTS = {
  STATUS: '/api/v1/budget/status',
} as const;

// ============================================================================
// ALL ENDPOINTS (for reference)
// ============================================================================

export const API_ENDPOINTS = {
  AUTH: AUTH_ENDPOINTS,
  CHAT: CHAT_ENDPOINTS,
  ANALYTICS: ANALYTICS_ENDPOINTS,
  GAMIFICATION: GAMIFICATION_ENDPOINTS,
  VOICE: VOICE_ENDPOINTS,
  PERSONALIZATION: PERSONALIZATION_ENDPOINTS,
  CONTENT: CONTENT_ENDPOINTS,
  SPACED_REPETITION: SPACED_REPETITION_ENDPOINTS,
  COLLABORATION: COLLABORATION_ENDPOINTS,
  HEALTH: HEALTH_ENDPOINTS,
  ADMIN: ADMIN_ENDPOINTS,
  BUDGET: BUDGET_ENDPOINTS,
} as const;

// ============================================================================
// HELPER TYPES
// ============================================================================

export type EndpointCategory = keyof typeof API_ENDPOINTS;
