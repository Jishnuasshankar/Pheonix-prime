/**
 * ChatContainer Component - WITH DEEP THINKING INTEGRATION
 * 
 * Production-ready integration of reasoning/deep thinking features into chat.
 * 
 * WCAG 2.1 AA Compliant + Deep Thinking Features:
 * - All existing accessibility features maintained
 * - Reasoning toggle with keyboard support
 * - Live reasoning chain display
 * - Error boundaries for reasoning failures
 * 
 * Deep Thinking Integration Points:
 * 1. Reasoning toggle in UI
 * 2. Dual API support (regular chat vs reasoning chat)
 * 3. Reasoning chain display in messages
 * 4. Thinking mode selection
 * 5. Real-time reasoning step streaming (future)
 * 
 * Backend Integration:
 * - POST /api/v1/chat/reasoning - Send reasoning-enabled message
 * - POST /api/v1/chat - Send regular message (existing)
 * - WebSocket for real-time updates (existing)
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChatStore } from '@/store/chatStore';
import { useEmotionStore } from '@/store/emotionStore';
import { useAuthStore } from '@/store/authStore';
import { useReasoningStore } from '@/store/reasoningStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { joinSession, leaveSession } from '@/services/websocket/socket.handlers';
import { chatWithReasoning } from '@/services/api/reasoning';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { EmotionIndicator } from './EmotionIndicator';
import { TypingIndicator } from './TypingIndicator';
import { VoiceButton } from './VoiceButton';
import { ReasoningToggle } from '@/components/reasoning/ReasoningToggle';
import { ThinkingIndicator } from '@/components/reasoning/ThinkingIndicator';
import { ReasoningChainDisplay } from '@/components/reasoning/ReasoningChainDisplay';
import { cn } from '@/utils/cn';
import { toast } from '@/components/ui/Toast';
import { AlertCircle, Wifi, WifiOff, Sparkles, Brain } from 'lucide-react';
import type { ThinkingMode } from '@/types/reasoning.types';

// ============================================================================
// TYPES
// ============================================================================

export interface ChatContainerProps {
  sessionId?: string;
  initialTopic?: string;
  showEmotion?: boolean;
  enableVoice?: boolean;
  enableReasoning?: boolean;
  className?: string;
}

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'error';

// ============================================================================
// PREMIUM EMPTY STATE (Unchanged)
// ============================================================================

const PremiumEmptyState: React.FC = React.memo(() => {
  return (
    <div className="flex-1 flex items-center justify-center px-8 relative overflow-hidden">
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
              👋
            </span>
          </div>
        </div>
        
        <h2 className="text-2xl font-black mb-4 tracking-tight leading-tight">
          <span 
            className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent"
            style={{
              backgroundSize: '200% 200%',
              animation: 'gradient 3s ease infinite'
            }}
          >
            Start Your Learning Journey
          </span>
        </h2>
        
        <p className="text-white/60 text-xl mb-3 leading-relaxed font-medium max-w-2xl mx-auto">
          Ask me anything! I'm here to help you learn with personalized, emotion-aware responses.
        </p>
        
        <p className="text-white/40 text-base mb-10 leading-relaxed font-medium">
          Powered by advanced AI with real-time emotion detection and deep thinking
        </p>
        
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
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-xs font-bold tracking-widest text-blue-400">EMOTION-AWARE</span>
          </div>
          <div 
            className="px-4 py-2 rounded-full backdrop-blur-xl border transition-all duration-300 hover:scale-105 flex items-center gap-2"
            style={{
              background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.2), rgba(252, 211, 77, 0.2))',
              borderColor: 'rgba(236, 72, 153, 0.3)'
            }}
          >
            <Brain className="w-3.5 h-3.5 text-pink-400" />
            <span className="text-xs font-bold tracking-widest text-pink-400">DEEP THINKING</span>
          </div>
        </div>
      </div>
    </div>
  );
});

PremiumEmptyState.displayName = 'PremiumEmptyState';

// ============================================================================
// CONNECTION STATUS BAR (Unchanged)
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
          <Wifi className="w-5 h-5 animate-pulse" />
          <span className="font-medium">Establishing secure connection...</span>
        </>
      )}
      {status === 'disconnected' && (
        <>
          <WifiOff className="w-5 h-5" />
          <span className="font-medium">Reconnecting to real-time services...</span>
        </>
      )}
      {status === 'error' && (
        <>
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">Connection error - Some features may be limited</span>
        </>
      )}
    </div>
  );
});

PremiumConnectionStatus.displayName = 'PremiumConnectionStatus';

// ============================================================================
// LOADING STATE (Unchanged)
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
// MAIN COMPONENT - WITH DEEP THINKING INTEGRATION
// ============================================================================

export const ChatContainer: React.FC<ChatContainerProps> = ({
  sessionId: propSessionId,
  initialTopic = 'general',
  showEmotion = true,
  enableVoice = true,
  enableReasoning = true,
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
    suggestedQuestions,
    clearSuggestedQuestions
  } = useChatStore();
  
  const {
    currentEmotion
  } = useEmotionStore();
  
  const {
    currentChain,
    setCurrentChain,
    addChain,
    preferences
  } = useReasoningStore();
  
  // Local state
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [isInitialized, setIsInitialized] = useState(false);
  const [reasoningEnabled, setReasoningEnabled] = useState(preferences.showReasoningByDefault);
  const [isReasoningInProgress, setIsReasoningInProgress] = useState(false);
  const [thinkingMode] = useState<ThinkingMode | undefined>(undefined);
  
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
    if (!activeSessionId) return;
    
    if (isConnected) {
      try {
        joinSession(activeSessionId);
        console.log('✓ Joined chat session:', activeSessionId);
      } catch (err) {
        console.warn('⚠️ Failed to join WebSocket session:', err);
      }
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
  
  useEffect(() => {
    if (!isConnected) return;
    
    const unsubscribe = subscribe('session_update', (data: any) => {
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
  // MESSAGE SENDING - DUAL STRATEGY (Regular vs Reasoning)
  // ============================================================================
  
  const handleSendMessage = useCallback(async (content: string) => {
    if (!content.trim() || !user) return;
    
    try {
      // Clear any previous error
      clearError();
      
      if (reasoningEnabled && enableReasoning) {
        // DEEP THINKING PATH: Use reasoning-enabled endpoint
        setIsReasoningInProgress(true);
        
        try {
          const reasoningResponse = await chatWithReasoning({
            user_id: user.id,
            session_id: activeSessionId || undefined,
            message: content.trim(),
            enable_reasoning: true,
            thinking_mode: thinkingMode,
            max_reasoning_depth: 5
          });
          
          // Store reasoning chain if present
          if (reasoningResponse.reasoning_chain) {
            setCurrentChain(reasoningResponse.reasoning_chain);
            if (reasoningResponse.session_id) {
              addChain(reasoningResponse.session_id, reasoningResponse.reasoning_chain);
            }
          }
          
          // Add user message to chat (optimistic)
          await storeSendMessage(content.trim(), user.id);
          
          // Clear reasoning state
          setIsReasoningInProgress(false);
          
          // WebSocket notification
          if (reasoningResponse.session_id && isConnected) {
            try {
              sendEvent({
                type: 'message_sent',
                sessionId: reasoningResponse.session_id,
                userId: user.id,
                reasoning_enabled: true
              });
            } catch (wsErr) {
              console.warn('WebSocket notification failed (non-critical):', wsErr);
            }
          }
          
          // Success toast for reasoning mode
          toast.success('Deep Thinking Complete', {
            description: `Used ${reasoningResponse.thinking_mode || 'adaptive'} thinking mode`
          });
          
        } catch (reasoningErr) {
          console.error('Reasoning request failed:', reasoningErr);
          setIsReasoningInProgress(false);
          
          // Fallback to regular chat on reasoning failure
          toast.warning('Reasoning Unavailable', {
            description: 'Falling back to regular chat mode'
          });
          
          await storeSendMessage(content.trim(), user.id);
        }
        
      } else {
        // REGULAR CHAT PATH: Use existing endpoint
        await storeSendMessage(content.trim(), user.id);
        
        // WebSocket event
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
      }
      
    } catch (err: any) {
      console.error('Failed to send message:', err);
      
      // Comprehensive error handling
      let errorTitle = 'Send Failed';
      let errorMessage = 'Failed to send message. Please try again.';
      
      if (err.code === 'ECONNABORTED' || err.code === 'ETIMEDOUT') {
        errorTitle = 'Request Timeout';
        errorMessage = 'Request timed out. Check your internet connection and try again.';
      } else if (err.response?.status === 401) {
        errorTitle = 'Authentication Required';
        errorMessage = 'Your session expired. Please log in again.';
      } else if (err.response?.status === 429) {
        errorTitle = 'Too Many Requests';
        errorMessage = 'You\'re sending messages too quickly. Please wait a moment.';
      } else if (err.response?.status === 500) {
        errorTitle = 'Server Error';
        errorMessage = 'Something went wrong on our end. Please try again in a moment.';
      } else if (err.response?.status === 404) {
        errorTitle = 'Not Found';
        errorMessage = 'The chat endpoint is not available. Please contact support.';
      } else if (!navigator.onLine) {
        errorTitle = 'No Connection';
        errorMessage = 'You appear to be offline. Check your network connection.';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      toast.error(errorTitle, {
        description: errorMessage
      });
    }
  }, [
    user,
    reasoningEnabled,
    enableReasoning,
    thinkingMode,
    activeSessionId,
    storeSendMessage,
    storeSessionId,
    isConnected,
    sendEvent,
    clearError,
    setCurrentChain,
    addChain
  ]);
  
  // ============================================================================
  // SUGGESTED QUESTIONS HANDLER
  // ============================================================================
  
  const handleSuggestedQuestionClick = useCallback(async (question: string) => {
    clearSuggestedQuestions();
    await handleSendMessage(question);
  }, [handleSendMessage, clearSuggestedQuestions]);
  
  // ============================================================================
  // REASONING TOGGLE HANDLER
  // ============================================================================
  
  const handleReasoningToggle = useCallback((enabled: boolean) => {
    setReasoningEnabled(enabled);
    
    toast.success(
      enabled ? 'Deep Thinking Enabled' : 'Deep Thinking Disabled',
      {
        description: enabled 
          ? 'AI will show its reasoning process step-by-step'
          : 'AI will provide direct answers'
      }
    );
  }, []);
  
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
      aria-label="Chat interface with deep thinking"
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
        <PremiumEmptyState />
      ) : (
        <div className="flex-1 overflow-hidden">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            currentUserId={user?.id}
            onQuestionClick={handleSuggestedQuestionClick}
          />
          
          {/* Reasoning Chain Display (if reasoning in progress and chain available) */}
          {isReasoningInProgress && currentChain && (
            <div className="px-8 py-4">
              <div className="mx-auto" style={{ maxWidth: '768px' }}>
                <ReasoningChainDisplay
                  reasoning={currentChain}
                  isStreaming={isReasoningInProgress}
                />
              </div>
            </div>
          )}
          
          {/* Thinking Indicator (when reasoning is in progress but no chain yet) */}
          {(isLoading || isReasoningInProgress) && (
            <div className="px-8 py-4">
              <div className="mx-auto" style={{ maxWidth: '768px' }}>
                {reasoningEnabled ? (
                  <ThinkingIndicator
                    mode={(thinkingMode as ThinkingMode) || ThinkingMode.HYBRID}
                    currentStep={currentChain?.steps.length}
                    totalSteps={5}
                  />
                ) : (
                  <TypingIndicator />
                )}
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
          {/* Reasoning Toggle */}
          {enableReasoning && (
            <div className="mb-4 flex justify-end">
              <ReasoningToggle
                enabled={reasoningEnabled}
                onChange={handleReasoningToggle}
                disabled={isLoading || isReasoningInProgress}
                showLabel
              />
            </div>
          )}
          
          <div className="flex items-end gap-4">
            {/* Voice Button */}
            {enableVoice && (
              <div className="flex-shrink-0">
                <VoiceButton
                  onTranscription={handleSendMessage}
                  disabled={isLoading || isReasoningInProgress || !isConnected}
                />
              </div>
            )}
            
            {/* Text Input */}
            <div className="flex-1">
              <MessageInput
                onSend={handleSendMessage}
                disabled={isLoading || isReasoningInProgress}
                placeholder={
                  isReasoningInProgress
                    ? 'AI is thinking deeply...'
                    : isLoading
                    ? 'AI is thinking...'
                    : reasoningEnabled
                    ? 'Ask anything... (Deep Thinking Mode)'
                    : 'Message MasterX...'
                }
                enableAttachments={false}
                enableEmoji={false}
                showCounter={true}
              />
              
              {/* Connection Warning */}
              {!isConnected && (
                <div className="mt-2 flex items-center gap-2 text-xs text-yellow-400/80 font-medium">
                  <WifiOff className="w-3.5 h-3.5" />
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
              
              {reasoningEnabled && (
                <span className="flex items-center gap-1.5 text-purple-400">
                  <Brain className="w-3 h-3" />
                  Deep Thinking Active
                </span>
              )}
              
              {storeSessionId && (
                <span className="text-white/20">
                  Session: {storeSessionId.slice(0, 8)}...
                </span>
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
          66% { transform: translate(-30px, 30px) rotate(-5deg); }
        }
        
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ChatContainer;
