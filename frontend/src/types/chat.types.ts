/**
 * Chat & Messaging Types
 * 
 * Matches backend models.py:
 * - Message (lines 203-218)
 * - ChatRequest (lines 374-379)
 * - ChatResponse (lines 382-403)
 * - ContextInfo (lines 334-339)
 * - AbilityInfo (lines 342-347)
 */

import type { EmotionState, EmotionMetrics } from './emotion.types';

// ============================================================================
// MESSAGE TYPES
// ============================================================================

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Message {
  id: string; // UUID
  session_id: string;
  user_id: string;
  role: MessageRole;
  content: string;
  timestamp: string; // ISO 8601
  
  // Emotion data (for user messages)
  emotion_state?: EmotionState | null;
  
  // AI response metadata (for assistant messages)
  provider_used?: string;
  response_time_ms?: number; // milliseconds
  tokens_used?: number;
  cost?: number;
  
  // ML-generated follow-up questions (for assistant messages)
  suggested_questions?: SuggestedQuestion[];
  
  // Optional fields
  embedding?: number[];
  quality_rating?: number; // 1-5
  
  // Legacy aliases for backward compatibility
  emotion?: EmotionState | EmotionMetrics | null;
  provider?: string;
  responseTime?: number;
}

// ============================================================================
// CHAT API TYPES
// ============================================================================

export interface ChatRequest {
  user_id: string;
  session_id?: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface ContextInfo {
  recent_messages_count: number;
  relevant_messages_count: number;
  has_context: boolean;
  retrieval_time_ms?: number;
}

export interface AbilityInfo {
  ability_level: number; // 0.0 - 1.0
  recommended_difficulty: number; // 0.0 - 1.0
  cognitive_load: number; // 0.0 - 1.0
  flow_state_score?: number;
}

/**
 * ML-Generated Follow-Up Question (Perplexity-inspired)
 * 
 * Matches backend models.py SuggestedQuestion (lines 350-361)
 * Generated using ML-based question generator with:
 * - LLM generation (contextual candidates)
 * - Semantic diversity filtering (sentence transformers)
 * - ML ranking (emotion + ability + RL)
 * - Reinforcement learning from user clicks
 */
export interface SuggestedQuestion {
  /**
   * The follow-up question text
   */
  question: string;
  
  /**
   * Why this question is suggested
   * @example "building_on_success", "connecting_concepts", "addressing_confusion"
   */
  rationale: string;
  
  /**
   * Change in difficulty relative to current level
   * @range -1.0 (easier) to +1.0 (harder)
   * @default 0.0 (same difficulty)
   */
  difficulty_delta: number;
  
  /**
   * Question type/category
   * @default "exploration"
   */
  category: 'exploration' | 'application' | 'challenge' | 'clarification' | string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  emotion_state?: EmotionState | null;
  provider_used: string;
  response_time_ms: number;
  timestamp: string; // ISO 8601
  
  // Enhanced metadata (Phase 2-4)
  category_detected?: string;
  tokens_used?: number;
  cost?: number;
  
  // Phase 3 metadata
  context_retrieved?: ContextInfo;
  ability_info?: AbilityInfo;
  ability_updated?: boolean;
  
  // Phase 4 metadata
  cached?: boolean;
  processing_breakdown?: Record<string, number>;
  
  // RAG metadata (Perplexity-inspired)
  rag_enabled?: boolean;
  citations?: string[];
  sources_count?: number;
  search_provider?: string;
  
  // Follow-up questions (Perplexity-inspired ML)
  suggested_questions?: SuggestedQuestion[];
}

/**
 * Chat History Response
 * 
 * Response from GET /api/v1/chat/history/{session_id}
 * Returns all messages from a conversation session
 */
export interface ChatHistoryResponse {
  session_id: string;
  messages: Message[];
  total_messages: number;
  session_started: string; // ISO 8601
  total_cost: number;
}

// ============================================================================
// REAL-TIME TYPES (WebSocket)
// ============================================================================

export interface TypingIndicator {
  user_id: string;
  session_id: string;
  is_typing: boolean;
  timestamp: string;
}

export interface MessageUpdate {
  message_id: string;
  session_id: string;
  updates: Partial<Message>;
  timestamp: string;
}

export interface EmotionUpdate {
  session_id: string;
  emotion: string;
  confidence: number;
  timestamp: string;
}

// ============================================================================
// CHAT UI STATE
// ============================================================================

export interface ChatUIState {
  isTyping: boolean;
  isLoading: boolean;
  error: string | null;
  scrollToBottom: boolean;
}

export interface MessageGroup {
  date: string; // YYYY-MM-DD
  messages: Message[];
}

// ============================================================================
// WEBSOCKET STREAMING TYPES
// ============================================================================

/**
 * Client → Server: Request to start streaming chat
 */
export interface ChatStreamRequest {
  message_id: string;
  session_id: string;
  user_id: string;
  message: string;
  context?: {
    subject?: string;
    enable_rag?: boolean;
    enable_reasoning?: boolean;
  };
}

/**
 * Client → Server: Stop ongoing generation
 */
export interface StopGenerationRequest {
  message_id: string;
  session_id: string;
}

/**
 * Server → Client: Stream start event
 */
export interface StreamStartEvent {
  type: 'stream_start';
  data: {
    message_id: string;
    session_id: string;
    ai_message_id: string;
    timestamp: string;
    metadata: {
      provider: string;
      category: string;
      estimated_tokens?: number;
    };
  };
}

/**
 * Server → Client: Thinking chunk (reasoning phase)
 */
export interface ThinkingChunkEvent {
  type: 'thinking_chunk';
  data: {
    message_id: string;
    session_id: string;
    reasoning_step: {
      step_number: number;
      thinking_mode: 'analytical' | 'creative' | 'metacognitive';
      description: string;
      confidence: number;
      timestamp: string;
    };
  };
}

/**
 * Server → Client: Content chunk (response text)
 */
export interface ContentChunkEvent {
  type: 'content_chunk';
  data: {
    message_id: string;
    session_id: string;
    content: string;
    chunk_index: number;
    is_code: boolean;
    timestamp: string;
  };
}

/**
 * Server → Client: Emotion update
 */
export interface EmotionUpdateEvent {
  type: 'emotion_update';
  data: {
    message_id: string;
    session_id: string;
    emotion: EmotionState;
    timestamp: string;
  };
}

/**
 * Server → Client: Context info
 */
export interface ContextInfoEvent {
  type: 'context_info';
  data: {
    message_id: string;
    session_id: string;
    context: {
      recent_messages_used: number;
      relevant_messages_used: number;
      semantic_search_enabled: boolean;
      rag_enabled: boolean;
      rag_sources?: number;
    };
    timestamp: string;
  };
}

/**
 * Server → Client: Stream complete
 */
export interface StreamCompleteEvent {
  type: 'stream_complete';
  data: {
    message_id: string;
    session_id: string;
    ai_message_id: string;
    full_content: string;
    metadata: {
      provider_used: string;
      response_time_ms: number;
      tokens_used: number;
      cost: number;
      ability_updated?: {
        subject: string;
        new_ability: number;
        confidence: number;
      };
    };
    timestamp: string;
  };
}

/**
 * Server → Client: Stream error
 */
export interface StreamErrorEvent {
  type: 'stream_error';
  data: {
    message_id: string;
    session_id: string;
    error: {
      code: string;
      message: string;
      details?: string;
      recoverable: boolean;
    };
    partial_content: string;
    timestamp: string;
  };
}

/**
 * Server → Client: Generation stopped (user cancelled)
 */
export interface GenerationStoppedEvent {
  type: 'generation_stopped';
  data: {
    message_id: string;
    session_id: string;
    ai_message_id: string;
    reason: 'user_cancelled' | 'timeout' | 'error';
    partial_content: string;
    metadata: {
      tokens_used: number;
      cost: number;
      stopped_at_ms: number;
    };
    timestamp: string;
  };
}

/**
 * Union type of all streaming events
 */
export type StreamEvent = 
  | StreamStartEvent
  | ThinkingChunkEvent
  | ContentChunkEvent
  | EmotionUpdateEvent
  | ContextInfoEvent
  | StreamCompleteEvent
  | StreamErrorEvent
  | GenerationStoppedEvent;

/**
 * Streaming message state
 */
export interface StreamingMessage extends Message {
  isStreaming: boolean;
  partialContent: string;
  streamMetadata?: {
    provider?: string;
    category?: string;
    contextInfo?: ContextInfoEvent['data']['context'];
    emotionDetected?: EmotionState;
  };
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

export const isMessage = (obj: unknown): obj is Message => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'role' in obj &&
    'content' in obj
  );
};

export const isChatResponse = (obj: unknown): obj is ChatResponse => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'session_id' in obj &&
    'message' in obj &&
    'provider_used' in obj
  );
};

export const isSuggestedQuestion = (obj: unknown): obj is SuggestedQuestion => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'question' in obj &&
    'rationale' in obj &&
    typeof (obj as SuggestedQuestion).question === 'string'
  );
};

// ============================================================================
// HELPER TYPES
// ============================================================================

export type MessageWithEmotion = Message & {
  emotion: EmotionMetrics;
};

export type OptimisticMessage = Omit<Message, 'id'> & {
  id: string;
  optimistic: boolean;
};
