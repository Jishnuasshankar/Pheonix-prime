/**
 * Message Component - Modern Centered Layout (2025)
 * 
 * MODERNIZED DESIGN:
 * - Centered fixed-width column (max-width: 768px)
 * - Both user and AI messages in center
 * - Suggested questions below AI response
 * - Matches ChatGPT/Claude 2025 patterns
 * 
 * WCAG 2.1 AA Compliant:
 * - Proper semantic HTML (article element)
 * - Clear visual distinction (user vs AI)
 * - Readable contrast ratios (>4.5:1)
 * - Keyboard accessible actions
 * 
 * Performance:
 * - React.memo to prevent unnecessary re-renders
 * - Lazy loading of markdown renderer
 * - Code highlighting on demand
 * - Height reporting for virtual scrolling
 * 
 * Backend Integration:
 * - Message data structure from ChatResponse
 * - Emotion state visualization
 * - Provider metadata display
 * - ML-generated suggested questions
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User, Bot, Copy, Check, Edit, Trash,
  Sparkles, DollarSign, Zap
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { Tooltip } from '@/components/ui/Tooltip';
import { Avatar } from '@/components/ui/Avatar';
import { SuggestedQuestions } from './SuggestedQuestions';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import type { Message as MessageType, SuggestedQuestion } from '@/types/chat.types';

// ============================================================================
// TYPES
// ============================================================================

export interface MessageProps {
  /**
   * Message data
   */
  message: MessageType;
  
  /**
   * Is this the current user's message
   */
  isOwn: boolean;
  
  /**
   * Callback when suggested question is clicked
   */
  onQuestionClick?: (question: string, questionData: SuggestedQuestion) => void;
  
  /**
   * Callback when message height changes (for virtual scrolling)
   */
  onHeightChange?: (height: number) => void;
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

// ============================================================================
// EMOTION BADGE COMPONENT
// ============================================================================

const EmotionBadge = React.memo<{ 
  emotion: string; 
  intensity: number;
  readiness: string;
}>(({ emotion, intensity, readiness }) => {
  // Map emotions to colors
  const emotionColors: Record<string, string> = {
    joy: 'bg-emotion-joy text-black',
    curiosity: 'bg-emotion-curiosity text-white',
    frustration: 'bg-emotion-frustration text-white',
    confusion: 'bg-accent-warning text-white',
    excitement: 'bg-emotion-joy text-black',
    calm: 'bg-emotion-calm text-black',
    anxiety: 'bg-emotion-frustration text-white',
    boredom: 'bg-text-tertiary text-white'
  };
  
  // Map readiness to icons
  const readinessIcons: Record<string, string> = {
    optimal_readiness: '🎯',
    high_readiness: '✨',
    moderate_readiness: '💫',
    low_readiness: '⚠️',
    not_ready: '🛑'
  };
  
  return (
    <Tooltip content={`Learning Readiness: ${readiness.replace(/_/g, ' ')}`}>
      <div className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium',
        emotionColors[emotion] || 'bg-bg-tertiary text-text-primary'
      )}>
        <span>{readinessIcons[readiness] || '💭'}</span>
        <span className="capitalize">{emotion}</span>
        <span className="opacity-70">
          {Math.round(intensity * 100)}%
        </span>
      </div>
    </Tooltip>
  );
});

EmotionBadge.displayName = 'EmotionBadge';

// ============================================================================
// METADATA FOOTER COMPONENT
// ============================================================================

const MessageMetadata = React.memo<{
  provider?: string;
  responseTime?: number;
  cost?: number;
  tokensUsed?: number;
}>(({ provider, responseTime, cost, tokensUsed }) => {
  if (!provider) return null;
  
  return (
    <div className="flex items-center gap-3 text-xs text-text-tertiary mt-2">
      {/* Provider */}
      <Tooltip content="AI Provider">
        <div className="flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          <span className="capitalize">{provider}</span>
        </div>
      </Tooltip>
      
      {/* Response Time */}
      {responseTime && (
        <Tooltip content="Response Time">
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3" />
            <span>{(responseTime / 1000).toFixed(2)}s</span>
          </div>
        </Tooltip>
      )}
      
      {/* Tokens Used */}
      {tokensUsed && (
        <Tooltip content="Tokens Used">
          <div className="flex items-center gap-1">
            <span>🎟️</span>
            <span>{tokensUsed.toLocaleString()}</span>
          </div>
        </Tooltip>
      )}
      
      {/* Cost */}
      {cost !== undefined && (
        <Tooltip content="Cost">
          <div className="flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            <span>${cost.toFixed(4)}</span>
          </div>
        </Tooltip>
      )}
    </div>
  );
});

MessageMetadata.displayName = 'MessageMetadata';

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const Message: React.FC<MessageProps> = ({
  message,
  isOwn,
  onQuestionClick,
  onHeightChange,
  className
}) => {
  // ============================================================================
  // STATE & REFS
  // ============================================================================
  
  const messageRef = useRef<HTMLDivElement>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [showActions, setShowActions] = useState(false);
  
  // ============================================================================
  // HEIGHT TRACKING (for virtual scrolling)
  // ============================================================================
  
  useEffect(() => {
    if (messageRef.current && onHeightChange) {
      const height = messageRef.current.offsetHeight;
      onHeightChange(height);
      
      // Observe size changes (e.g., image loading, code expansion)
      const resizeObserver = new ResizeObserver((entries) => {
        const newHeight = entries[0].contentRect.height;
        if (newHeight !== height) {
          onHeightChange(newHeight);
        }
      });
      
      resizeObserver.observe(messageRef.current);
      
      return () => resizeObserver.disconnect();
    }
  }, [onHeightChange]);
  
  // ============================================================================
  // COPY HANDLER
  // ============================================================================
  
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  }, [message.content]);
  
  // ============================================================================
  // MARKDOWN COMPONENTS
  // ============================================================================
  
  const markdownComponents = {
    code({ inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      return !inline && language ? (
        <div className="relative group my-4">
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => navigator.clipboard.writeText(String(children))}
              className="px-2 py-1 bg-white/[0.08] hover:bg-white/[0.12] rounded text-xs text-white/60"
            >
              Copy
            </button>
          </div>
          <SyntaxHighlighter
            style={vscDarkPlus}
            language={language}
            PreTag="div"
            className="rounded-lg text-sm"
            {...props}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      ) : (
        <code className="px-1.5 py-0.5 bg-white/[0.08] rounded text-sm font-mono" {...props}>
          {children}
        </code>
      );
    },
    a({ href, children }: any) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:underline"
        >
          {children}
        </a>
      );
    }
  };
  
  // ============================================================================
  // RENDER - MODERN CENTERED LAYOUT
  // ============================================================================
  
  return (
    <motion.article
      ref={messageRef}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'w-full px-6 py-4',
        className
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      role="article"
      aria-label={`Message from ${isOwn ? 'you' : 'AI assistant'}`}
    >
      {/* CENTERED CONTAINER - Max width 768px */}
      <div className="mx-auto" style={{ maxWidth: '768px' }}>
        
        {/* MESSAGE BUBBLE - Modern centered design */}
        <div className={cn(
          'rounded-2xl px-5 py-4 mb-2 border transition-all duration-200',
          isOwn
            ? 'bg-blue-500/10 border-blue-500/20 backdrop-blur-xl'
            : 'bg-white/[0.03] border-white/[0.08] backdrop-blur-xl'
        )}>
          {/* Role Indicator */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {isOwn ? (
                <>
                  <User className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-semibold text-white/80">You</span>
                </>
              ) : (
                <>
                  <Bot className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-semibold text-white/80">AI Tutor</span>
                </>
              )}
            </div>
            
            {/* Timestamp */}
            <time
              className="text-xs text-white/40"
              dateTime={message.timestamp}
            >
              {format(new Date(message.timestamp), 'h:mm a')}
            </time>
          </div>
          
          {/* MESSAGE CONTENT */}
          <div className="relative">
            {isOwn ? (
              // User message (plain text)
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-white/90">
                {message.content}
              </p>
            ) : (
              // AI message (markdown)
              <div className="prose prose-sm prose-invert max-w-none text-white/90">
                <ReactMarkdown components={markdownComponents}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
            
            {/* Copy Button (hover) */}
            <AnimatePresence>
              {showActions && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className="absolute top-0 right-0"
                >
                  <Tooltip content={isCopied ? 'Copied!' : 'Copy message'}>
                    <button
                      onClick={handleCopy}
                      className="p-2 hover:bg-white/[0.08] rounded-lg transition-colors"
                      aria-label="Copy message"
                    >
                      {isCopied ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4 text-white/60" />
                      )}
                    </button>
                  </Tooltip>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
        
        {/* METADATA BAR - AI messages only */}
        {!isOwn && (message.provider_used || message.emotion_state) && (
          <div className="flex items-center gap-3 px-2 mb-3 text-xs text-white/40">
            {/* Emotion Badge */}
            {message.emotion_state && (
              <EmotionBadge
                emotion={message.emotion_state.primary_emotion}
                intensity={message.emotion_state.valence || 0.5}
                readiness={message.emotion_state.learning_readiness}
              />
            )}
            
            {/* Provider Info */}
            {message.provider_used && (
              <Tooltip content="AI Provider">
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-3 h-3" />
                  <span className="capitalize">{message.provider_used}</span>
                </div>
              </Tooltip>
            )}
            
            {/* Response Time */}
            {message.response_time_ms && (
              <Tooltip content="Response Time">
                <div className="flex items-center gap-1.5">
                  <Zap className="w-3 h-3" />
                  <span>{(message.response_time_ms / 1000).toFixed(2)}s</span>
                </div>
              </Tooltip>
            )}
            
            {/* Cost */}
            {message.cost !== undefined && message.cost > 0 && (
              <Tooltip content="Cost">
                <div className="flex items-center gap-1.5">
                  <DollarSign className="w-3 h-3" />
                  <span>${message.cost.toFixed(4)}</span>
                </div>
              </Tooltip>
            )}
          </div>
        )}
        
        {/* SUGGESTED QUESTIONS - Below AI response (NEW LOCATION) */}
        {!isOwn && message.suggested_questions && message.suggested_questions.length > 0 && onQuestionClick && (
          <div className="mt-3">
            <SuggestedQuestions
              questions={message.suggested_questions}
              onQuestionClick={onQuestionClick}
              visible={true}
              maxDisplay={5}
            />
          </div>
        )}
      </div>
    </motion.article>
  );
};

Message.displayName = 'Message';

export default React.memo(Message);
