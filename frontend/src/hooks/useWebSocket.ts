/**
 * useWebSocket Hook - React hook for WebSocket connection
 * 
 * Features:
 * - Auto-connect on mount
 * - Auto-disconnect on unmount
 * - Connection state tracking
 * - Event listener management
 * - Subscribe/unsubscribe pattern
 * 
 * Usage:
 * ```tsx
 * const { isConnected, subscribe } = useWebSocket();
 * 
 * useEffect(() => {
 *   if (!isConnected) return;
 *   
 *   const unsubscribe = subscribe('emotion_update', (data) => {
 *     console.log('Emotion:', data);
 *   });
 *   
 *   return unsubscribe;
 * }, [isConnected]);
 * ```
 */

import { useEffect, useState, useCallback } from 'react';
import nativeSocketClient, { type WebSocketEvent } from '@/services/websocket/native-socket.client';
import { 
  initializeSocketHandlers, 
  cleanupSocketHandlers 
} from '@/services/websocket/socket.handlers';

export interface UseWebSocketReturn {
  /**
   * Connection status
   */
  isConnected: boolean;
  
  /**
   * Emit event to server
   */
  emit: (event: string, data: any) => void;
  
  /**
   * Subscribe to event (returns unsubscribe function)
   */
  subscribe: (event: string, callback: (data: any) => void) => () => void;
  
  /**
   * Manually reconnect
   */
  reconnect: () => void;
  
  /**
   * Manually disconnect
   */
  disconnect: () => void;
}

// Singleton connection manager
let connectionInitialized = false;
let connectionRefCount = 0;

export const useWebSocket = (): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Increment ref count (number of components using WebSocket)
    connectionRefCount++;
    console.log(`[useWebSocket] Component mounted (ref count: ${connectionRefCount})`);
    
    // CRITICAL FIX: Only initialize once globally
    // Prevent multiple components from creating multiple connections
    if (!connectionInitialized) {
      console.log('[useWebSocket] Initializing WebSocket connection (first mount)');
      connectionInitialized = true;
      
      // Connect on mount (will check if already connected internally)
      nativeSocketClient.connect();
      
      // Initialize event handlers
      initializeSocketHandlers();
    } else {
      console.log('[useWebSocket] Using existing WebSocket connection');
    }

    // Listen to connection state
    const checkConnection = () => {
      setIsConnected(nativeSocketClient.isConnected());
    };

    const interval = setInterval(checkConnection, 1000);
    checkConnection(); // Initial check

    // Cleanup on unmount
    return () => {
      clearInterval(interval);
      
      // Decrement ref count
      connectionRefCount--;
      console.log(`[useWebSocket] Component unmounted (ref count: ${connectionRefCount})`);
      
      // Only disconnect when NO components are using it
      if (connectionRefCount === 0) {
        console.log('[useWebSocket] No more components using WebSocket, disconnecting');
        cleanupSocketHandlers();
        nativeSocketClient.disconnect();
        connectionInitialized = false;
      }
    };
  }, []);

  /**
   * Subscribe to event (returns unsubscribe function)
   */
  const subscribe = useCallback((event: string, callback: (data: any) => void): (() => void) => {
    nativeSocketClient.on(event as WebSocketEvent, callback);
    
    // Return unsubscribe function
    return () => {
      nativeSocketClient.off(event as WebSocketEvent, callback);
    };
  }, []);

  /**
   * Emit event to server
   */
  const emit = useCallback((event: string, data: any) => {
    nativeSocketClient.send(event as WebSocketEvent, data);
  }, []);

  /**
   * Manually reconnect
   */
  const reconnect = useCallback(() => {
    nativeSocketClient.reconnect();
  }, []);

  /**
   * Manually disconnect
   */
  const disconnect = useCallback(() => {
    nativeSocketClient.disconnect();
  }, []);

  return {
    isConnected,
    emit,
    subscribe,
    reconnect,
    disconnect,
  };
};
