/**
 * API Endpoints Configuration
 * 
 * Matches backend server.py endpoints exactly
 * Auto-generates typed endpoint URLs
 */

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';

// ============================================================================
// AUTHENTICATION ENDPOINTS
// ============================================================================

export const AUTH_ENDPOINTS = {
  REGISTER: `${API_BASE}/api/auth/register`,
  LOGIN: `${API_BASE}/api/auth/login`,
  LOGOUT: `${API_BASE}/api/auth/logout`,
  REFRESH: `${API_BASE}/api/auth/refresh`,
  ME: `${API_BASE}/api/auth/me`,
} as const;

// ============================================================================
// CHAT ENDPOINTS
// ============================================================================

export const CHAT_ENDPOINTS = {
  SEND_MESSAGE: `${API_BASE}/api/v1/chat`,
  GET_HISTORY: (sessionId: string) => `${API_BASE}/api/v1/chat/history/${sessionId}`,
  DELETE_SESSION: (sessionId: string) => `${API_BASE}/api/v1/chat/session/${sessionId}`,
} as const;

// ============================================================================
// ANALYTICS ENDPOINTS
// ============================================================================

export const ANALYTICS_ENDPOINTS = {
  DASHBOARD: (userId: string) => `${API_BASE}/api/v1/analytics/dashboard/${userId}`,
  PERFORMANCE: (userId: string, daysBack = 30) => 
    `${API_BASE}/api/v1/analytics/performance/${userId}?days_back=${daysBack}`,
  EMOTIONS: (userId: string, days = 7) => 
    `${API_BASE}/api/v1/analytics/emotions/${userId}?days=${days}`,
  TOPICS: (userId: string) => `${API_BASE}/api/v1/analytics/topics/${userId}`,
  VELOCITY: (userId: string) => `${API_BASE}/api/v1/analytics/velocity/${userId}`,
  SESSIONS: (userId: string) => `${API_BASE}/api/v1/analytics/sessions/${userId}`,
  INSIGHTS: (userId: string) => `${API_BASE}/api/v1/analytics/insights/${userId}`,
} as const;

// ============================================================================
// GAMIFICATION ENDPOINTS
// ============================================================================

export const GAMIFICATION_ENDPOINTS = {
  STATS: (userId: string) => `${API_BASE}/api/v1/gamification/stats/${userId}`,
  LEADERBOARD: (timeRange: string = 'weekly') => 
    `${API_BASE}/api/v1/gamification/leaderboard?time_range=${timeRange}`,
  ACHIEVEMENTS: `${API_BASE}/api/v1/gamification/achievements`,
  RECORD_ACTIVITY: `${API_BASE}/api/v1/gamification/record-activity`,
  STREAK: (userId: string) => `${API_BASE}/api/v1/gamification/streak/${userId}`,
} as const;

// ============================================================================
// VOICE ENDPOINTS
// ============================================================================

export const VOICE_ENDPOINTS = {
  TRANSCRIBE: `${API_BASE}/api/v1/voice/transcribe`,
  SYNTHESIZE: `${API_BASE}/api/v1/voice/synthesize`,
  ASSESS_PRONUNCIATION: `${API_BASE}/api/v1/voice/assess-pronunciation`,
  CHAT: `${API_BASE}/api/v1/voice/chat`,
  VOICES: `${API_BASE}/api/v1/voice/voices`,
} as const;

// ============================================================================
// PERSONALIZATION ENDPOINTS
// ============================================================================

export const PERSONALIZATION_ENDPOINTS = {
  PROFILE: (userId: string) => `${API_BASE}/api/v1/personalization/profile/${userId}`,
  RECOMMENDATIONS: (userId: string) => 
    `${API_BASE}/api/v1/personalization/recommendations/${userId}`,
  LEARNING_PATH: (userId: string, topic: string) => 
    `${API_BASE}/api/v1/personalization/learning-path/${userId}/${topic}`,
} as const;

// ============================================================================
// CONTENT ENDPOINTS
// ============================================================================

export const CONTENT_ENDPOINTS = {
  NEXT: (userId: string) => `${API_BASE}/api/v1/content/next/${userId}`,
  SEQUENCE: (userId: string, topic: string, nItems = 10) => 
    `${API_BASE}/api/v1/content/sequence/${userId}/${topic}?n_items=${nItems}`,
  SEARCH: (query: string, nResults = 5) => 
    `${API_BASE}/api/v1/content/search?query=${encodeURIComponent(query)}&n_results=${nResults}`,
} as const;

// ============================================================================
// SPACED REPETITION ENDPOINTS
// ============================================================================

export const SPACED_REPETITION_ENDPOINTS = {
  DUE_CARDS: (userId: string, limit = 20, includeNew = true) => 
    `${API_BASE}/api/v1/spaced-repetition/due-cards/${userId}?limit=${limit}&include_new=${includeNew}`,
  CREATE_CARD: `${API_BASE}/api/v1/spaced-repetition/create-card`,
  REVIEW_CARD: `${API_BASE}/api/v1/spaced-repetition/review-card`,
  STATS: (userId: string) => `${API_BASE}/api/v1/spaced-repetition/stats/${userId}`,
} as const;

// ============================================================================
// COLLABORATION ENDPOINTS
// ============================================================================

export const COLLABORATION_ENDPOINTS = {
  FIND_PEERS: `${API_BASE}/api/v1/collaboration/find-peers`,
  CREATE_SESSION: `${API_BASE}/api/v1/collaboration/create-session`,
  JOIN_SESSION: `${API_BASE}/api/v1/collaboration/join-session`,
  SEND_MESSAGE: `${API_BASE}/api/v1/collaboration/send-message`,
} as const;

// ============================================================================
// HEALTH & MONITORING ENDPOINTS
// ============================================================================

export const HEALTH_ENDPOINTS = {
  BASIC: `${API_BASE}/api/health`,
  DETAILED: `${API_BASE}/api/health/detailed`,
  PROVIDERS: `${API_BASE}/api/v1/providers`,
  MODEL_STATUS: `${API_BASE}/api/v1/system/model-status`,
} as const;

// ============================================================================
// ADMIN ENDPOINTS
// ============================================================================

export const ADMIN_ENDPOINTS = {
  COSTS: `${API_BASE}/api/v1/admin/costs`,
  PERFORMANCE: `${API_BASE}/api/v1/admin/performance`,
  CACHE: `${API_BASE}/api/v1/admin/cache`,
  PRODUCTION_READINESS: `${API_BASE}/api/v1/admin/production-readiness`,
  SYSTEM_STATUS: `${API_BASE}/api/v1/admin/system/status`,
} as const;

// ============================================================================
// BUDGET ENDPOINTS
// ============================================================================

export const BUDGET_ENDPOINTS = {
  STATUS: `${API_BASE}/api/v1/budget/status`,
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
