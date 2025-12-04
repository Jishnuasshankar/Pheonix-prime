/**
 * ChatContainer Component - Premium Enhanced with Deep Thinking Integration
 * 
 * PRODUCTION-READY DEEP THINKING INTEGRATION
 * - Real-time reasoning chain display
 * - Thinking mode indicators
 * - Seamless fallback to standard chat
 * - Comprehensive error handling
 * - WCAG 2.1 AA Compliant
 * 
 * Performance:
 * - Virtual scrolling for large message lists
 * - Lazy loading of reasoning components
 * - Optimistic UI updates
 * - GPU-accelerated animations
 * 
 * Backend Integration:
 * - POST /api/v1/chat - Standard chat (existing)
 * - POST /api/v1/chat/reasoning - Chat with reasoning (NEW)
 * - WebSocket for real-time emotion + reasoning updates
 * - Session persistence in MongoDB
 */

import React, { useEffect, useRef, useState, useCallback, lazy, Suspense } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChatStore } from '@/store/chatStore';
import { useEmotionStore } from '@/store/emotionStore';
import { useAuthStore } from '@/store/authStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { joinSession, leaveSession } from '@/services/websocket/socket.handlers';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { EmotionIndicator } from './EmotionIndicator';
import { TypingIndicator } from './TypingIndicator';
import { VoiceButton } from './VoiceButton';
import { cn } from '@/utils/cn';
import { toast } from '@/components/ui/Toast';
import { AlertCircle, Wifi, WifiOff, Sparkles, Brain, Zap } from 'lucide-react';
import type { ReasoningChain, ThinkingMode, ReasoningResponse } from '@/types/reasoning.types';

// Lazy load reasoning display component (improves initial load)
const ReasoningChainDisplay = lazy(() =>
  import('@/components/reasoning/ReasoningChainDisplay')
);

// ============================================================================
// TYPES
// ============================================================================

export interface ChatContainerProps {
  sessionId?: string;
  initialTopic?: string;
  showEmotion?: boolean;
  enableVoice?: boolean;
  enableReasoning?: boolean;  // NEW: Enable deep thinking
  className?: string;
}

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

// Extended message type with reasoning support
interface ExtendedMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  emotion_state?: Record<string, unknown>;
  provider_used?: string;
  response_time_ms?: number;
  // Deep Thinking fields
  reasoning_enabled?: boolean;
  reasoning_chain?: ReasoningChain;
  thinking_mode?: ThinkingMode;
}

// ============================================================================
// PREMIUM EMPTY STATE COMPONENT
// ============================================================================

const PremiumEmptyState: React.FC<{ enableReasoning?: boolean }> = React.memo(({ enableReasoning = false }) => {
  return (
    <div className="flex-1 flex items-center justify-center px-8 relative overflow-hidden">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full blur-3xl opacity-30"
          style={{ 
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent 70%)',
            animation: 'float 20s ease-in-out infinite'
          }}
        />
        <div 
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] rounded-full blur-3xl opacity-30"
          style={{ 
            background: 'radial-gradient(circle, rgba(168, 85, 247, 0.4), transparent 70%)',
            animation: 'float 25s ease-in-out infinite',
            animationDelay: '-10s'
          }}
        />
      </div>
      
      <div className="relative z-10 text-center max-w-3xl">
        {/* Hero emoji */}
        <div className="mb-10 relative inline-block">
          <div 
            className="absolute inset-0 rounded-full blur-3xl opacity-50"
            style={{ 
              background: 'radial-gradient(circle, rgba(59, 130, 246, 0.4), rgba(168, 85, 247, 0.4))',
              animation: 'pulse 3s ease-in-out infinite'
            }}
          />
          <div className="relative text-[120px] leading-none">
            <span 
              className="inline-block filter drop-shadow-2xl"
              style={{
                animation: 'wave 2.5s ease-in-out infinite',
                transformOrigin: '70% 70%'
              }}
            >
              {enableReasoning ? '🧠' : '👋'}
            </span>
          </div>
        </div>
        
        {/* Main greeting */}
        <h2 className="text-2xl font-black mb-4 tracking-tight leading-tight">
          <span 
            className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
            style={{
              backgroundSize: '200% 200%',
              animation: 'gradient 3s ease infinite'
            }}
          >
            {enableReasoning ? 'Start Learning with Deep Thinking' : 'Start Your Learning Journey'}
          </span>
        </h2>
        
        {/* Description */}
        <p className="text-white/60 text-xl mb-3 leading-relaxed font-medium max-w-2xl mx-auto">
          {enableReasoning 
            ? "Ask me anything! I'll show you my step-by-step thinking process."
            : "Ask me anything! I'm here to help you learn with personalized, emotion-aware responses."}
        </p>
        
        <p className="text-white/40 text-base mb-10 leading-relaxed font-medium">
          Powered by advanced AI with real-time emotion detection
          {enableReasoning && ' and visible reasoning'}
        </p>
        
        {/* Premium badges */}
        <div className="flex items-center justify-center gap-3 flex-wrap">
          <div 
            className="px-4 py-2 rounded-full border backdrop-blur-xl transition-all duration-300 hover:scale-105"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderColor: 'rgba(255, 255, 255, 0.1)'
            }}
          >
            <span className="text-xs text-white/50 font-bold tracking-widest">AI ASSISTANT</span>
          </div>
          <div 
            className="px-4 py-2 rounded-full backdrop-blur-xl border transition-all duration-300 hover:scale-105 flex items-center gap-2"
            style={{
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(168, 85, 247, 0.2))',
              borderColor: 'rgba(59, 130, 246, 0.3)'
            }}
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-400" aria-hidden="true" />
            <span className="text-xs font-bold tracking-widest text-blue-400">EMOTION-AWARE</span>
          </div>
          {enableReasoning && (
            <div 
              className="px-4 py-2 rounded-full backdrop-blur-xl border transition-all duration-300 hover:scale-105 flex items-center gap-2"
              style={{
                background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2))',
                borderColor: 'rgba(124, 58, 237, 0.3)'
              }}
            >
              <Brain className="w-3.5 h-3.5 text-purple-400" aria-hidden="true" />
              <span className="text-xs font-bold tracking-widest text-purple-400">DEEP THINKING</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

PremiumEmptyState.displayName = 'PremiumEmptyState';

// ============================================================================
// CONNECTION STATUS BAR
// ============================================================================

const PremiumConnectionStatus: React.FC<{ status: ConnectionStatus }> = React.memo(({ status }) => {
  if (status === 'connected') return null;
  
  return (
    <div
      className={cn(
        'px-6 py-3 text-sm flex items-center gap-3 border-b backdrop-blur-xl transition-all duration-300',
        status === 'connecting' && 'bg-white/[0.03] text-white/60 border-white/[0.08]',
        status === 'disconnected' && 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        status === 'error' && 'bg-red-500/10 text-red-400 border-red-500/20'
      )}
      role="status"
      aria-live="polite"
    >
      {status === 'connecting' && (
        <>
          <Wifi className="w-5 h-5 animate-pulse" aria-hidden="true" />
          <span className="font-medium">Establishing secure connection...</span>
        </>
      )}
      {status === 'disconnected' && (
        <>
          <WifiOff className="w-5 h-5" aria-hidden="true" />
          <span className="font-medium">Reconnecting to real-time services...</span>
        </>
      )}
      {status === 'error' && (
        <>
          <AlertCircle className="w-5 h-5" aria-hidden="true" />
          <span className="font-medium">Connection error - Some features may be limited</span>
        </>
      )}
    </div>
  );
});

PremiumConnectionStatus.displayName = 'PremiumConnectionStatus';

// ============================================================================
// LOADING STATE
// ============================================================================

const PremiumLoadingState: React.FC = React.memo(() => {
  return (
    <div className="flex items-center justify-center h-full relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full blur-3xl opacity-30"
          style={{ 
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.4), transparent 70%)',
            animation: 'pulse 2s ease-in-out infinite'
          }}
        />
      </div>
      
      <div className="text-center space-y-6 relative z-10">
        <div className="relative w-20 h-20 mx-auto">
          <div 
            className="absolute inset-0 rounded-full border-4 border-transparent"
            style={{
              borderTopColor: '#3b82f6',
              borderRightColor: '#a855f7',
              animation: 'spin 1s linear infinite'
            }}
          />
          <div 
            className="absolute inset-2 rounded-full border-4 border-transparent opacity-50"
            style={{
              borderTopColor: '#ec4899',
              borderRightColor: '#3b82f6',
              animation: 'spin 1.5s linear infinite reverse'
            }}
          />
        </div>
        
        <div>
          <p className="text-white/80 text-lg font-semibold mb-2">Loading chat session...</p>
          <p className="text-white/40 text-sm">Preparing your personalized experience</p>
        </div>
      </div>
    </div>
  );
});

PremiumLoadingState.displayName = 'PremiumLoadingState';

// ============================================================================
// THINKING MODE INDICATOR (NEW)
// ============================================================================

const ThinkingModeIndicator: React.FC<{ mode: ThinkingMode }> = React.memo(({ mode }) => {
  const modeConfig = {
    system1: {
      label: 'Fast Thinking',
      icon: Zap,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20'
    },
    system2: {
      label: 'Deep Thinking',
      icon: Brain,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20'
    },
    hybrid: {
      label: 'Adaptive',
      icon: Sparkles,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20'
    }
  };

  const config = modeConfig[mode];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border',
        config.color,
        config.bgColor,
        config.borderColor
      )}
      role="status"
      aria-label={`Thinking mode: ${config.label}`}
    >
      <Icon className="w-3.5 h-3.5" aria-hidden="true" />
      <span>{config.label}</span>
    </div>
  );
});

ThinkingModeIndicator.displayName = 'ThinkingModeIndicator';

// ============================================================================
// MAIN COMPONENT - WITH DEEP THINKING INTEGRATION
// ============================================================================

export const ChatContainer: React.FC<ChatContainerProps> = ({
  sessionId: propSessionId,
  initialTopic = 'general',
  showEmotion = true,
  enableVoice = true,
  enableReasoning = false,  // NEW: Deep Thinking toggle
  className
}) => {
  // ============================================================================
  // STATE & REFS
  // ============================================================================
  
  const { user } = useAuthStore();
  const {
    messages,
    isLoading,
    error,
    sessionId: storeSessionId,
    sendMessage: storeSendMessage,
    loadHistory,
    clearError,
    setTyping,
    suggestedQuestions,
    clearSuggestedQuestions
  } = useChatStore();
  
  const {
    currentEmotion,
    isAnalyzing
  } = useEmotionStore();
  
  // Local state
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [isInitialized, setIsInitialized] = useState(false);
  const [currentReasoningChain, setCurrentReasoningChain] = useState<ReasoningChain | null>(null);
  const [isReasoningVisible, setIsReasoningVisible] = useState(false);
  
  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const messageEndRef = useRef<HTMLDivElement>(null);
  
  // Navigation
  const navigate = useNavigate();
  const { sessionId: urlSessionId } = useParams<{ sessionId: string }>();
  
  // Determine active session ID
  const activeSessionId = propSessionId || urlSessionId || storeSessionId;
  
  // ============================================================================
  // WEBSOCKET CONNECTION
  // ============================================================================
  
  const { isConnected, subscribe, emit: sendEvent } = useWebSocket();
  
  useEffect(() => {
    setConnectionStatus(isConnected ? 'connected' : 'disconnected');
  }, [isConnected]);
  
  useEffect(() => {
    if (!activeSessionId || !isConnected) return;
    
    try {
      joinSession(activeSessionId);
      console.log('✓ Joined chat session:', activeSessionId);
    } catch (err) {
      console.warn('⚠️ Failed to join WebSocket session:', err);
    }
    
    return () => {
      if (isConnected) {
        try {
          leaveSession(activeSessionId);
          console.log('✓ Left chat session:', activeSessionId);
        } catch (err) {
          console.warn('⚠️ Failed to leave WebSocket session:', err);
        }
      }
    };
  }, [isConnected, activeSessionId]);
  
  // Subscribe to session updates
  useEffect(() => {
    if (!isConnected) return;
    
    const unsubscribe = subscribe('session_update', (data: unknown) => {
      console.log('Session update:', data);
    });
    
    return unsubscribe;
  }, [isConnected, subscribe]);
  
  // ============================================================================
  // SESSION INITIALIZATION
  // ============================================================================
  
  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    const initializeSession = async () => {
      try {
        if (activeSessionId) {
          await loadHistory(activeSessionId);
        }
        setIsInitialized(true);
      } catch (err) {
        console.error('Failed to initialize session:', err);
        toast.error('Session Error', {
          description: 'Failed to load chat session. Please try again.'
        });
      }
    };
    
    initializeSession();
  }, [activeSessionId, user, navigate, loadHistory]);
  
  // ============================================================================
  // AUTO-SCROLL
  // ============================================================================
  
  const scrollToBottom = useCallback(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);
  
  useEffect(() => {
    if (messages.length > 0) {
      requestAnimationFrame(() => {
        scrollToBottom();
      });
    }
  }, [messages.length, scrollToBottom]);
  
  // ============================================================================
  // MESSAGE SENDING WITH REASONING SUPPORT (ENHANCED)
  // ============================================================================
  
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || !user) return;
    
    try {
      // Clear previous reasoning chain
      setCurrentReasoningChain(null);
      setIsReasoningVisible(false);
      
      // Determine which endpoint to use
      if (enableReasoning) {
        // Use reasoning endpoint
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || ''}/api/v1/chat/reasoning`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: user.id,
            session_id: storeSessionId || undefined,
            message: content.trim(),
            enable_reasoning: true,
            thinking_mode: undefined, // Let engine auto-select
            max_reasoning_depth: 5,
            context: {}
          })
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        const reasoningResponse: ReasoningResponse = await response.json();
        
        // Update store with new message (this will trigger UI update)
        await storeSendMessage(content.trim(), user.id);
        
        // If reasoning chain is available, display it
        if (reasoningResponse.reasoning_enabled && reasoningResponse.reasoning_chain) {
          setCurrentReasoningChain(reasoningResponse.reasoning_chain);
          setIsReasoningVisible(true);
        }
        
      } else {
        // Use standard chat endpoint (existing flow)
        await storeSendMessage(content.trim(), user.id);
      }
      
      // WebSocket notification
      if (storeSessionId && isConnected) {
        try {
          sendEvent({
            type: 'message_sent',
            sessionId: storeSessionId,
            userId: user.id
          });
        } catch (wsErr) {
          console.warn('WebSocket notification failed (non-critical):', wsErr);
        }
      }
      
    } catch (err: unknown) {
      console.error('Failed to send message:', err);
      
      const error = err as { code?: string; response?: { status?: number; data?: { detail?: string } }; message?: string };
      
      let errorTitle = 'Send Failed';
      let errorMessage = 'Failed to send message. Please try again.';
      
      if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
        errorTitle = 'Request Timeout';
        errorMessage = 'Request timed out. Check your internet connection and try again.';
      } else if (error.response?.status === 401) {
        errorTitle = 'Authentication Required';
        errorMessage = 'Your session expired. Please log in again.';
      } else if (error.response?.status === 429) {
        errorTitle = 'Too Many Requests';
        errorMessage = 'You\'re sending messages too quickly. Please wait a moment.';
      } else if (error.response?.status === 500) {
        errorTitle = 'Server Error';
        errorMessage = 'Something went wrong on our end. Please try again in a moment.';
      } else if (!navigator.onLine) {
        errorTitle = 'No Connection';
        errorMessage = 'You appear to be offline. Check your network connection.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorTitle, {
        description: errorMessage
      });
    }
  }, [user, enableReasoning, storeSendMessage, storeSessionId, isConnected, sendEvent]);
  
  // ============================================================================
  // SUGGESTED QUESTIONS HANDLER
  // ============================================================================
  
  const handleSuggestedQuestionClick = useCallback(async (question: string, questionData: unknown) => {
    clearSuggestedQuestions();
    await handleSendMessage(question);
  }, [handleSendMessage, clearSuggestedQuestions]);
  
  // ============================================================================
  // ERROR HANDLING
  // ============================================================================
  
  useEffect(() => {
    if (error) {
      toast.error('Error', {
        description: error
      });
    }
  }, [error]);
  
  // ============================================================================
  // LOADING STATE
  // ============================================================================
  
  if (!isInitialized) {
    return <PremiumLoadingState />;
  }
  
  // ============================================================================
  // RENDER - WITH REASONING INTEGRATION
  // ============================================================================
  
  return (
    <div
      ref={containerRef}
      className={cn(
        'flex flex-col h-full relative overflow-hidden',
        className
      )}
      style={{ 
        background: 'linear-gradient(to bottom, #0a0a0f, #0d0d15)'
      }}
      role="main"
      aria-label="Chat interface"
    >
      {/* Connection Status Bar */}
      <PremiumConnectionStatus status={connectionStatus} />
      
      {/* Floating Emotion Indicator */}
      {showEmotion && currentEmotion && (
        <div className="absolute top-6 right-6 z-20">
          <div 
            className="backdrop-blur-xl rounded-2xl border shadow-2xl transition-all duration-300 hover:scale-105"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
            }}
          >
            <EmotionIndicator
              emotion={currentEmotion}
              isAnalyzing={isAnalyzing}
              compact
            />
          </div>
        </div>
      )}
      
      {/* Message List or Empty State */}
      {messages.length === 0 && !isLoading ? (
        <PremiumEmptyState enableReasoning={enableReasoning} />
      ) : (
        <div className="flex-1 overflow-hidden">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            currentUserId={user?.id}
            onQuestionClick={handleSuggestedQuestionClick}
          />
          
          {/* Reasoning Chain Display (NEW) */}
          {isReasoningVisible && currentReasoningChain && (
            <div className="px-8 py-6">
              <div className="mx-auto" style={{ maxWidth: '768px' }}>
                <Suspense fallback={
                  <div className="p-4 text-center text-white/40">
                    Loading reasoning display...
                  </div>
                }>
                  <ReasoningChainDisplay
                    reasoning={currentReasoningChain}
                    isStreaming={false}
                    className="mb-4"
                  />
                </Suspense>
              </div>
            </div>
          )}
          
          {/* Typing Indicator */}
          {isLoading && (
            <div className="px-8 py-4">
              <div className="mx-auto" style={{ maxWidth: '768px' }}>
                <TypingIndicator />
              </div>
            </div>
          )}
          
          <div ref={messageEndRef} />
        </div>
      )}
      
      {/* Message Input Area */}
      <div className="border-t border-white/[0.08] backdrop-blur-2xl p-8 relative">
        <div 
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at bottom, rgba(59, 130, 246, 0.2), transparent 70%)'
          }}
        />
        
        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="flex items-end gap-4">
            {/* Voice Button */}
            {enableVoice && (
              <div className="flex-shrink-0">
                <VoiceButton
                  onTranscription={handleSendMessage}
                  disabled={isLoading || !isConnected}
                />
              </div>
            )}
            
            {/* Text Input */}
            <div className="flex-1">
              <MessageInput
                onSend={handleSendMessage}
                disabled={isLoading}
                placeholder={
                  isLoading
                    ? enableReasoning 
                      ? 'AI is thinking deeply...'
                      : 'AI is thinking...'
                    : 'Message MasterX...'
                }
                enableAttachments={false}
                enableEmoji={false}
                showCounter={true}
              />
              
              {/* Connection Warning */}
              {!isConnected && (
                <div className="mt-2 flex items-center gap-2 text-xs text-yellow-400/80 font-medium">
                  <WifiOff className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>Real-time updates unavailable. Messages will still send.</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Status Footer */}
          <div className="mt-4 flex items-center justify-between text-xs text-white/30 font-medium">
            <div className="flex items-center gap-4">
              <span
                className={cn(
                  'flex items-center gap-2 transition-colors duration-300',
                  isConnected ? 'text-emerald-400' : 'text-red-400'
                )}
              >
                <span className={cn(
                  'w-2 h-2 rounded-full',
                  isConnected ? 'bg-emerald-500 animate-pulse shadow-lg shadow-emerald-500/50' : 'bg-red-500'
                )} />
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
              
              {enableReasoning && (
                <>
                  <span className="text-white/20">•</span>
                  <span className="flex items-center gap-1.5 text-purple-400">
                    <Brain className="w-3 h-3" aria-hidden="true" />
                    Deep Thinking Mode
                  </span>
                </>
              )}
              
              {storeSessionId && (
                <>
                  <span className="text-white/20">•</span>
                  <span className="text-white/20">
                    Session: {storeSessionId.slice(0, 8)}...
                  </span>
                </>
              )}
            </div>
            
            <div className="flex items-center gap-2 text-white/40">
              <kbd className="px-2 py-1 text-[10px] bg-white/[0.05] rounded border border-white/[0.08] font-mono">Enter</kbd>
              <span>to send</span>
              <span className="text-white/20">•</span>
              <kbd className="px-2 py-1 text-[10px] bg-white/[0.05] rounded border border-white/[0.08] font-mono">Shift+Enter</kbd>
              <span>for new line</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Premium Animations CSS */}
      <style>{`
        @keyframes wave {
          0%, 100% { transform: rotate(0deg); }
          25% { transform: rotate(20deg); }
          75% { transform: rotate(-20deg); }
        }
        
        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          33% { transform: translate(30px, -30px) rotate(5deg); }
          66% { transform: translate(-20px, 20px) rotate(-5deg); }
        }
        
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

ChatContainer.displayName = 'ChatContainer';

export default ChatContainer;
