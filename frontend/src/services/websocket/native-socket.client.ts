/**
 * Native WebSocket Client - Real-time bidirectional communication
 * 
 * Uses native WebSocket API instead of socket.io for compatibility with FastAPI
 * 
 * Features:
 * - Auto-reconnection on disconnect
 * - Token authentication
 * - Event-based messaging
 * - Connection state tracking
 * - Heartbeat/keepalive
 * 
 * Performance:
 * - WebSocket: ~1KB overhead per message
 * - Real-time: <50ms latency for emotion updates
 * - Automatic keepalive pings every 30s
 */

import { useAuthStore } from '@/store/authStore';

// Event types for type safety
export type WebSocketEvent = 
  | 'emotion_update'
  | 'typing_indicator'
  | 'message_received'
  | 'session_update'
  | 'notification'
  | 'error'
  | 'user_typing'
  | 'join_session'
  | 'leave_session'
  | 'message_sent';

interface WebSocketMessage {
  type: WebSocketEvent;
  data: any;
  timestamp?: number;
}

type EventCallback = (data: any) => void;

class NativeSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 5000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isIntentionalClose = false;
  private url = '';
  private eventHandlers: Map<WebSocketEvent, Set<EventCallback>> = new Map();
  private messageQueue: WebSocketMessage[] = [];

  /**
   * Initialize WebSocket connection
   * 
   * CRITICAL: Smart environment detection matching API client logic
   * Priority order:
   * 1. Emergent platform → use relative path (window.location.origin)
   * 2. VITE_BACKEND_URL from .env (user configuration)
   * 3. Localhost detection → ws://localhost:8001
   * 4. Fallback → use current origin
   */
  connect(): void {
    const token = useAuthStore.getState().accessToken;
    
    if (!token) {
      console.warn('[WebSocket] No token available, skipping WebSocket connection');
      // Don't try to connect without token - this is OK, not an error
      return;
    }

    // Smart environment detection (matches API client logic in client.ts)
    let backendURL = '';
    const hostname = window.location.hostname;
    
    // Priority 1: Check Emergent platform (Kubernetes routing)
    if (hostname.includes('emergentagent.com')) {
      backendURL = window.location.origin;
      console.log('[WebSocket] Emergent platform detected, using:', backendURL);
    }
    // Priority 2: Check VITE_BACKEND_URL (user configuration)
    else if (import.meta.env.VITE_BACKEND_URL && typeof import.meta.env.VITE_BACKEND_URL === 'string' && import.meta.env.VITE_BACKEND_URL.trim() !== '') {
      backendURL = import.meta.env.VITE_BACKEND_URL.trim();
      console.log('[WebSocket] Using VITE_BACKEND_URL:', backendURL);
    }
    // Priority 3: Check localhost (default for local dev)
    else if (hostname === 'localhost' || hostname === '127.0.0.1') {
      backendURL = 'http://localhost:8001';
      console.log('[WebSocket] Localhost detected, using:', backendURL);
    }
    // Priority 4: Fallback to current origin
    else {
      backendURL = window.location.origin;
      console.log('[WebSocket] Using current origin:', backendURL);
    }
    
    // Convert HTTP to WS protocol
    const wsURL = backendURL
      .replace(/^https/, 'wss')
      .replace(/^http/, 'ws')
      .replace(/\/api$/, '') + '/api/ws';
    
    this.url = `${wsURL}?token=${encodeURIComponent(token)}`;
    
    console.log('[WebSocket] Final WebSocket URL:', this.url.replace(/token=[^&]+/, 'token=***'));
    
    this.isIntentionalClose = false;
    this._connect();
  }

  /**
   * Internal connection method
   */
  private _connect(): void {
    try {
      console.log('[WebSocket] Connecting to:', this.url.replace(/token=[^&]+/, 'token=***'));
      
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = this._handleOpen.bind(this);
      this.ws.onclose = this._handleClose.bind(this);
      this.ws.onerror = this._handleError.bind(this);
      this.ws.onmessage = this._handleMessage.bind(this);
      
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this._scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket open event
   */
  private _handleOpen(event: Event): void {
    console.log('[WebSocket] ✓ Connected:', this.ws?.url);
    this.reconnectAttempts = 0;
    
    // Start heartbeat
    this._startHeartbeat();
    
    // Flush message queue
    this._flushMessageQueue();
    
    // Notify listeners
    this._emit('connect', { timestamp: Date.now() });
  }

  /**
   * Handle WebSocket close event
   */
  private _handleClose(event: CloseEvent): void {
    console.log('[WebSocket] ✗ Disconnected:', event.code, event.reason);
    
    // Stop heartbeat
    this._stopHeartbeat();
    
    // Notify listeners
    this._emit('disconnect', { code: event.code, reason: event.reason });
    
    // Reconnect if not intentional
    if (!this.isIntentionalClose) {
      this._scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   * 
   * CRITICAL: WebSocket errors should NOT block the UI
   * - App should still work without WebSocket (degraded mode)
   * - Only show toast after multiple failed attempts
   */
  private _handleError(event: Event): void {
    console.warn('[WebSocket] Connection error (non-critical):', event);
    
    // Increment reconnection counter
    this.reconnectAttempts++;
    
    // Only show toast after max attempts (don't spam user)
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('[WebSocket] Max reconnection attempts reached - operating in degraded mode');
      
      // Notify user via toast (optional - app still works)
      import('@/store/uiStore').then(({ useUIStore }) => {
        useUIStore.getState().showToast({
          type: 'warning',
          message: 'Real-time features unavailable. App will still work.',
          duration: 5000,
        });
      }).catch(() => {
        // Ignore if toast fails - this is truly non-critical
        console.log('[WebSocket] Could not show toast notification');
      });
    }
  }

  /**
   * Handle incoming WebSocket message
   */
  private _handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Handle heartbeat response
      if (message.type === 'pong' as any) {
        return;
      }
      
      // Emit to registered handlers
      this._emit(message.type, message.data);
      
    } catch (error) {
      console.error('[WebSocket] Failed to parse message:', error);
    }
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private _scheduleReconnect(): void {
    if (this.isIntentionalClose) return;
    
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );
    
    console.log(`[WebSocket] Reconnecting in ${delay}ms...`);
    
    setTimeout(() => {
      if (!this.isIntentionalClose) {
        this._connect();
      }
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private _startHeartbeat(): void {
    this._stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send('ping', {});
      }
    }, 30000); // 30 seconds
  }

  /**
   * Stop heartbeat
   */
  private _stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Flush queued messages
   */
  private _flushMessageQueue(): void {
    if (this.messageQueue.length === 0) return;
    
    console.log(`[WebSocket] Flushing ${this.messageQueue.length} queued messages`);
    
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this._sendRaw(message);
      }
    }
  }

  /**
   * Emit event to registered handlers
   */
  private _emit(event: WebSocketEvent, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`[WebSocket] Error in ${event} handler:`, error);
        }
      });
    }
  }

  /**
   * Send raw WebSocket message
   */
  private _sendRaw(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send, connection not open');
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    this.isIntentionalClose = true;
    this._stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Manual reconnect
   */
  reconnect(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }

  /**
   * Send message to server
   */
  send(type: WebSocketEvent, data: any): void {
    const message: WebSocketMessage = {
      type,
      data,
      timestamp: Date.now()
    };

    if (this.isConnected()) {
      this._sendRaw(message);
    } else {
      // Queue message for when connection is restored
      console.warn('[WebSocket] Queueing message:', type);
      this.messageQueue.push(message);
    }
  }

  /**
   * Register event listener
   */
  on(event: WebSocketEvent, callback: EventCallback): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    
    this.eventHandlers.get(event)!.add(callback);
  }

  /**
   * Remove event listener
   */
  off(event: WebSocketEvent, callback?: EventCallback): void {
    if (callback) {
      this.eventHandlers.get(event)?.delete(callback);
    } else {
      this.eventHandlers.delete(event);
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getState(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (!this.ws) return 'closed';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'open';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'closed';
    }
  }
}

// Singleton instance
export const nativeSocketClient = new NativeSocketClient();
export default nativeSocketClient;
