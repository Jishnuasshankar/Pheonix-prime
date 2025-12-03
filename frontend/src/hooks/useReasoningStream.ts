/**
 * useReasoningStream Hook
 * 
 * React hook for streaming reasoning chains via WebSocket.
 * Provides real-time updates as AI generates reasoning steps.
 * 
 * AGENTS_FRONTEND.md compliant:
 * - TypeScript strict mode
 * - Comprehensive error handling
 * - Cleanup on unmount
 * - Connection state management
 * - Retry logic with exponential backoff
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  ReasoningStreamEvent,
  ReasoningChain,
  ReasoningStep,
  ThinkingMode,
  TokenBudget
} from '@/types/reasoning.types';

/**
 * WebSocket connection states
 */
export enum ConnectionState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

/**
 * Hook options
 */
interface UseReasoningStreamOptions {
  /** WebSocket URL (defaults to env variable) */
  wsUrl?: string;
  
  /** Auto-reconnect on disconnect */
  autoReconnect?: boolean;
  
  /** Maximum reconnection attempts */
  maxReconnectAttempts?: number;
  
  /** Initial reconnection delay (ms) */
  reconnectDelay?: number;
  
  /** Callback when connection established */
  onConnect?: () => void;
  
  /** Callback when connection closed */
  onDisconnect?: () => void;
  
  /** Callback on error */
  onError?: (error: Error) => void;
}

/**
 * Hook return value
 */
interface UseReasoningStreamReturn {
  /** Current reasoning chain being streamed */
  currentChain: ReasoningChain | null;
  
  /** Current reasoning step */
  currentStep: ReasoningStep | null;
  
  /** Thinking mode selected */
  thinkingMode: ThinkingMode | null;
  
  /** Token budget allocated */
  tokenBudget: TokenBudget | null;
  
  /** Whether stream is active */
  isStreaming: boolean;
  
  /** Connection state */
  connectionState: ConnectionState;
  
  /** Error message (if any) */
  error: string | null;
  
  /** Accumulated response text (for final message) */
  responseText: string;
  
  /** Connect to WebSocket */
  connect: (sessionId: string, userId: string) => void;
  
  /** Disconnect from WebSocket */
  disconnect: () => void;
  
  /** Send message to trigger reasoning */
  sendMessage: (message: string, options?: {
    enableReasoning?: boolean;
    thinkingMode?: ThinkingMode;
    maxDepth?: number;
  }) => void;
  
  /** Clear current chain */
  clearChain: () => void;
}

/**
 * Get WebSocket URL from environment or parameter
 */
const getWebSocketUrl = (customUrl?: string): string => {
  if (customUrl) {
    return customUrl;
  }
  
  // Try environment variable
  const envWsUrl = import.meta.env.VITE_WS_URL;
  if (envWsUrl) {
    return envWsUrl;
  }
  
  // Fallback: construct from current location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws/reasoning`;
};

/**
 * useReasoningStream Hook
 * 
 * Manages WebSocket connection for real-time reasoning streaming.
 * Handles connection lifecycle, reconnection, and event processing.
 * 
 * @param options - Hook configuration options
 * @returns Hook state and control functions
 * 
 * @example
 * ```tsx
 * const {
 *   currentChain,
 *   isStreaming,
 *   connect,
 *   sendMessage
 * } = useReasoningStream({
 *   autoReconnect: true,
 *   onConnect: () => console.log('Connected!')
 * });
 * 
 * // Connect to WebSocket
 * useEffect(() => {
 *   connect(sessionId, userId);
 *   return () => disconnect();
 * }, [sessionId, userId]);
 * 
 * // Send reasoning request
 * sendMessage('Explain quantum physics', {
 *   enableReasoning: true,
 *   thinkingMode: ThinkingMode.SYSTEM2
 * });
 * ```
 */
export const useReasoningStream = (
  options: UseReasoningStreamOptions = {}
): UseReasoningStreamReturn => {
  const {
    wsUrl: customWsUrl,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectDelay: initialReconnectDelay = 1000,
    onConnect,
    onDisconnect,
    onError
  } = options;
  
  // State
  const [currentChain, setCurrentChain] = useState<ReasoningChain | null>(null);
  const [currentStep, setCurrentStep] = useState<ReasoningStep | null>(null);
  const [thinkingMode, setThinkingMode] = useState<ThinkingMode | null>(null);
  const [tokenBudget, setTokenBudget] = useState<TokenBudget | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [error, setError] = useState<string | null>(null);
  const [responseText, setResponseText] = useState('');
  
  // Refs for WebSocket and reconnection logic
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sessionIdRef = useRef<string>('');
  const userIdRef = useRef<string>('');
  
  /**
   * Handle WebSocket message
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data: ReasoningStreamEvent = JSON.parse(event.data);
      
      switch (data.type) {
        case 'thinking_started':
          setIsStreaming(true);
          setError(null);
          setResponseText('');
          setThinkingMode(data.thinking_mode);
          
          // Initialize chain
          setCurrentChain({
            id: `chain-${Date.now()}`,
            query: '',
            thinking_mode: data.thinking_mode,
            steps: [],
            total_confidence: 0,
            processing_time_ms: 0,
            complexity_score: 0
          });
          break;
          
        case 'thinking_mode_selected':
          setThinkingMode(data.mode);
          break;
          
        case 'budget_allocated':
          setTokenBudget(data.budget);
          break;
          
        case 'reasoning_step':
          setCurrentStep(data.step);
          
          // Add step to chain
          setCurrentChain((prev) => {
            if (!prev) {
              return null;
            }
            
            return {
              ...prev,
              steps: [...prev.steps, data.step]
            };
          });
          break;
          
        case 'reasoning_complete':
          setCurrentChain((prev) => {
            if (!prev) {
              return null;
            }
            
            return {
              ...prev,
              processing_time_ms: data.time_ms,
              conclusion: data.conclusion,
              completed_at: new Date().toISOString()
            };
          });
          break;
          
        case 'response_token':
          setResponseText((prev) => prev + data.token);
          break;
          
        case 'complete':
          setIsStreaming(false);
          
          // Finalize chain
          setCurrentChain((prev) => {
            if (!prev) {
              return null;
            }
            
            return {
              ...prev,
              conclusion: responseText,
              completed_at: new Date().toISOString()
            };
          });
          break;
          
        case 'error':
          setError(data.error);
          setIsStreaming(false);
          
          if (onError) {
            onError(new Error(data.error));
          }
          break;
      }
    } catch (err) {
      console.error('[useReasoningStream] Failed to parse message:', err);
      setError('Failed to parse server message');
    }
  }, [responseText, onError]);
  
  /**
   * Handle WebSocket connection open
   */
  const handleOpen = useCallback(() => {
    console.log('[useReasoningStream] WebSocket connected');
    setConnectionState(ConnectionState.CONNECTED);
    setError(null);
    reconnectAttemptsRef.current = 0;
    
    if (onConnect) {
      onConnect();
    }
  }, [onConnect]);
  
  /**
   * Handle WebSocket connection close
   */
  const handleClose = useCallback(() => {
    console.log('[useReasoningStream] WebSocket disconnected');
    setConnectionState(ConnectionState.DISCONNECTED);
    setIsStreaming(false);
    
    if (onDisconnect) {
      onDisconnect();
    }
    
    // Attempt reconnection if enabled and under limit
    if (
      autoReconnect &&
      reconnectAttemptsRef.current < maxReconnectAttempts &&
      sessionIdRef.current &&
      userIdRef.current
    ) {
      const delay = initialReconnectDelay * Math.pow(2, reconnectAttemptsRef.current);
      console.log(`[useReasoningStream] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
      
      setConnectionState(ConnectionState.RECONNECTING);
      
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttemptsRef.current += 1;
        connect(sessionIdRef.current, userIdRef.current);
      }, delay);
    }
  }, [autoReconnect, maxReconnectAttempts, initialReconnectDelay, onDisconnect]);
  
  /**
   * Handle WebSocket error
   */
  const handleError = useCallback((event: Event) => {
    console.error('[useReasoningStream] WebSocket error:', event);
    setConnectionState(ConnectionState.ERROR);
    setError('WebSocket connection error');
    
    if (onError) {
      onError(new Error('WebSocket connection error'));
    }
  }, [onError]);
  
  /**
   * Connect to WebSocket
   */
  const connect = useCallback((sessionId: string, userId: string) => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    sessionIdRef.current = sessionId;
    userIdRef.current = userId;
    
    try {
      const wsUrl = getWebSocketUrl(customWsUrl);
      const fullUrl = `${wsUrl}?session_id=${sessionId}&user_id=${userId}`;
      
      console.log('[useReasoningStream] Connecting to:', fullUrl);
      setConnectionState(ConnectionState.CONNECTING);
      
      const ws = new WebSocket(fullUrl);
      
      ws.onopen = handleOpen;
      ws.onmessage = handleMessage;
      ws.onclose = handleClose;
      ws.onerror = handleError;
      
      wsRef.current = ws;
    } catch (err) {
      console.error('[useReasoningStream] Failed to create WebSocket:', err);
      setConnectionState(ConnectionState.ERROR);
      setError('Failed to create WebSocket connection');
      
      if (onError && err instanceof Error) {
        onError(err);
      }
    }
  }, [customWsUrl, handleOpen, handleMessage, handleClose, handleError, onError]);
  
  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setConnectionState(ConnectionState.DISCONNECTED);
    sessionIdRef.current = '';
    userIdRef.current = '';
  }, []);
  
  /**
   * Send message to trigger reasoning
   */
  const sendMessage = useCallback((
    message: string,
    options?: {
      enableReasoning?: boolean;
      thinkingMode?: ThinkingMode;
      maxDepth?: number;
    }
  ) => {
    if (!wsRef.current || connectionState !== ConnectionState.CONNECTED) {
      setError('WebSocket not connected');
      return;
    }
    
    const payload = {
      type: 'reasoning_request',
      message,
      enable_reasoning: options?.enableReasoning ?? true,
      thinking_mode: options?.thinkingMode,
      max_depth: options?.maxDepth ?? 5
    };
    
    wsRef.current.send(JSON.stringify(payload));
  }, [connectionState]);
  
  /**
   * Clear current chain
   */
  const clearChain = useCallback(() => {
    setCurrentChain(null);
    setCurrentStep(null);
    setThinkingMode(null);
    setTokenBudget(null);
    setResponseText('');
    setError(null);
  }, []);
  
  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);
  
  return {
    currentChain,
    currentStep,
    thinkingMode,
    tokenBudget,
    isStreaming,
    connectionState,
    error,
    responseText,
    connect,
    disconnect,
    sendMessage,
    clearChain
  };
};

export default useReasoningStream;
