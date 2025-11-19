/**
 * API Client Configuration
 * 
 * Configured Axios instance with:
 * - Base URL configuration from environment
 * - JWT token injection via interceptors
 * - Request/response logging (dev only)
 * - Global error handling with user-friendly messages
 * - Retry logic with exponential backoff
 * - Timeout protection
 * 
 * @module services/api/client
 */

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@store/authStore';
import { useUIStore } from '@store/uiStore';

/**
 * Extended Axios config with retry support
 */
interface RetryConfig extends InternalAxiosRequestConfig {
  retry?: number;
  __retryCount?: number;
}

/**
 * Smart Base URL Detection
 * 
 * Automatically detects the environment and uses the correct backend URL:
 * - Local Development (localhost): http://localhost:8001
 * - Preview/Production: Relative URL (empty string - uses same domain via Kubernetes ingress)
 * 
 * This allows seamless testing in both environments without manual configuration changes.
 * 
 * FIX: Check for non-empty string to avoid empty VITE_BACKEND_URL breaking detection
 */
const getBaseURL = (): string => {
  // Check for explicit backend URL (must be non-empty string)
  const envBackendUrl = import.meta.env.VITE_BACKEND_URL;
  
  if (envBackendUrl && typeof envBackendUrl === 'string' && envBackendUrl.trim() !== '') {
    const trimmedUrl = envBackendUrl.trim();
    console.log(`✓ Using explicit VITE_BACKEND_URL: ${trimmedUrl}`);
    return trimmedUrl;
  }
  
  // Auto-detect environment based on hostname
  const hostname = window.location.hostname;
  
  // Local development: use localhost backend
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('✓ Detected localhost - using http://localhost:8001');
    return 'http://localhost:8001';
  }
  
  // Preview/Production: use relative URLs (Kubernetes ingress routes /api to backend)
  console.log('✓ Detected production - using relative URLs');
  return '';
};

/**
 * Main Axios instance for API communication
 * Automatically configured with base URL and default headers
 * 
 * Base URL Configuration:
 * - Production/Preview: Empty string (uses relative URLs, Kubernetes routes /api to backend)
 * - Local Development: http://localhost:8001
 */
export const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor - Enhanced with Fallback
 * Injects JWT token from auth store into all requests
 * Falls back to localStorage/sessionStorage if Zustand state not yet updated
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Try Zustand store first (primary source)
    let token = useAuthStore.getState().accessToken;
    
    // Fallback 1: localStorage (handles race conditions)
    if (!token || token.trim() === '') {
      token = localStorage.getItem('jwt_token');
      
      if (import.meta.env.DEV && token) {
        console.log('⚠️ Using token from localStorage fallback');
      }
    }
    
    // Fallback 2: sessionStorage
    if (!token || token.trim() === '') {
      token = sessionStorage.getItem('jwt_token');
      
      if (import.meta.env.DEV && token) {
        console.log('⚠️ Using token from sessionStorage fallback');
      }
    }
    
    if (token && token.trim() !== '' && config.headers) {
      config.headers.Authorization = `Bearer ${token.trim()}`;
      
      if (import.meta.env.DEV) {
        console.log(`→ ${config.method?.toUpperCase()} ${config.url} [Auth: ✓]`);
      }
    } else if (import.meta.env.DEV) {
      console.warn(`→ ${config.method?.toUpperCase()} ${config.url} [Auth: ✗ No token]`);
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor - Enhanced Error Handler with Token Refresh
 * Handles common error scenarios with user-friendly messages
 * Automatically attempts token refresh on 401 errors
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`← ${response.status} ${response.config.url}`);
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const { response, config } = error;
    
    // Log error in development
    if (import.meta.env.DEV) {
      console.error(`✗ ${response?.status} ${config?.url}`, error);
    }
    
    // Handle specific error codes
    if (response) {
      switch (response.status) {
        case 401: {
          // ✅ NEW: Try to refresh token before logging out
          const { refreshToken, refreshAccessToken, logout } = useAuthStore.getState();
          
          // Prevent infinite loop
          if (config && !(config as any).__isRetry && refreshToken) {
            try {
              // Mark as retry attempt
              (config as any).__isRetry = true;
              
              // Attempt token refresh
              await refreshAccessToken();
              
              // Get new token and retry original request
              const newToken = useAuthStore.getState().accessToken;
              if (config.headers && newToken) {
                config.headers.Authorization = `Bearer ${newToken}`;
              }
              
              console.log('✓ Token refreshed, retrying request');
              return apiClient(config);
              
            } catch (refreshError) {
              // Refresh failed, proceed to logout
              console.error('✗ Token refresh failed:', refreshError);
              logout();
            }
          } else {
            // No refresh token or already retried, logout
            logout();
          }
          
          useUIStore.getState().showToast({
            type: 'error',
            message: 'Session expired. Please log in again.',
          });
          break;
        }
          
        case 403:
          // Forbidden
          useUIStore.getState().showToast({
            type: 'error',
            message: 'You do not have permission to perform this action.',
          });
          break;
          
        case 429:
          // Rate limited
          useUIStore.getState().showToast({
            type: 'warning',
            message: 'Too many requests. Please slow down.',
          });
          break;
          
        case 500:
        case 502:
        case 503:
          // Server errors
          useUIStore.getState().showToast({
            type: 'error',
            message: 'Server error. Please try again later.',
          });
          break;
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout
      useUIStore.getState().showToast({
        type: 'error',
        message: 'Request timeout. Check your connection.',
      });
    } else if (!navigator.onLine) {
      // Offline
      useUIStore.getState().showToast({
        type: 'error',
        message: 'No internet connection.',
      });
    }
    
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor - Retry Logic
 * Automatically retries failed requests with exponential backoff
 * Only retries on network errors or 5xx server errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config as RetryConfig;
    
    // Don't retry if:
    // - No config
    // - No retry count specified
    // - Max retries reached
    if (
      !config ||
      !config.retry ||
      config.__retryCount >= (config.retry || 0)
    ) {
      return Promise.reject(error);
    }
    
    // Only retry on network errors or 5xx
    const shouldRetry = 
      !error.response || 
      (error.response.status >= 500 && error.response.status < 600);
    
    if (!shouldRetry) {
      return Promise.reject(error);
    }
    
    config.__retryCount = config.__retryCount || 0;
    config.__retryCount += 1;
    
    // Exponential backoff: 1s, 2s, 4s, 8s...
    const delay = Math.pow(2, config.__retryCount) * 1000;
    await new Promise((resolve) => setTimeout(resolve, delay));
    
    return apiClient(config);
  }
);

export default apiClient;