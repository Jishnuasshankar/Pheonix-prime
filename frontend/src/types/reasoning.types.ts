/**
 * Deep Thinking / Reasoning TypeScript Types
 * 
 * Aligned with backend reasoning models from:
 * - /app/backend/core/reasoning/reasoning_chain.py
 * - /app/backend/core/reasoning/dual_process.py
 * - /app/backend/core/reasoning/budget_allocator.py
 * 
 * AGENTS_FRONTEND.md compliant:
 * - Strict TypeScript mode
 * - Zero 'any' types
 * - Comprehensive JSDoc comments
 * - Immutable by design (readonly where appropriate)
 */

/**
 * Thinking mode selection
 * - SYSTEM1: Fast, intuitive thinking (cached, simple queries)
 * - SYSTEM2: Slow, deliberate reasoning (complex, step-by-step)
 * - HYBRID: Adaptive approach (starts fast, goes deep if needed)
 */
export enum ThinkingMode {
  SYSTEM1 = 'system1',
  SYSTEM2 = 'system2',
  HYBRID = 'hybrid'
}

/**
 * Reasoning strategy types
 * Different ways of approaching problem-solving
 */
export enum ReasoningStrategy {
  DEDUCTIVE = 'deductive',     // General → specific (logical derivation)
  INDUCTIVE = 'inductive',     // Specific → general (pattern recognition)
  ABDUCTIVE = 'abductive',     // Best explanation (inference)
  ANALOGICAL = 'analogical',   // By analogy (similar cases)
  CAUSAL = 'causal',           // Cause-effect (why questions)
  ALGORITHMIC = 'algorithmic'  // Step-by-step procedure (how questions)
}

/**
 * Budget allocation modes
 * Determines token allocation based on complexity and student state
 */
export enum BudgetMode {
  MINIMAL = 'minimal',             // 500-1000 tokens (quick answers)
  STANDARD = 'standard',           // 1000-2000 tokens (normal)
  EXTENDED = 'extended',           // 2000-3500 tokens (detailed)
  COMPREHENSIVE = 'comprehensive'  // 3500-5000 tokens (struggling students)
}

/**
 * Single reasoning step in the thinking process
 * Represents one thought or cognitive action
 */
export interface ReasoningStep {
  /** Unique identifier for this step */
  readonly id?: string;
  
  /** Step number in the chain (1-indexed) */
  readonly step_number: number;
  
  /** Content of the reasoning step (the actual thought) */
  readonly content: string;
  
  /** Strategy used for this step */
  readonly strategy: ReasoningStrategy;
  
  /** Confidence in this step (0.0 to 1.0) */
  readonly confidence: number;
  
  /** ISO timestamp when step was created */
  readonly timestamp: string;
  
  /** Processing time for this step (milliseconds) */
  readonly processing_time_ms?: number;
  
  /** MCTS metadata (if from Monte Carlo Tree Search) */
  readonly parent_step_id?: string;
  readonly ucb_score?: number;
  readonly visit_count?: number;
}

/**
 * Complete reasoning chain from query to conclusion
 * Contains all thinking steps with metadata for transparency
 */
export interface ReasoningChain {
  /** Unique identifier for this reasoning chain */
  readonly id: string;
  
  /** Original user query */
  readonly query: string;
  
  /** Thinking mode used (system1, system2, or hybrid) */
  readonly thinking_mode: ThinkingMode;
  
  /** All reasoning steps in order */
  readonly steps: readonly ReasoningStep[];
  
  /** Final conclusion/answer (if completed) */
  readonly conclusion?: string;
  
  /** Overall confidence across all steps (0.0 to 1.0) */
  readonly total_confidence: number;
  
  /** Total processing time in milliseconds */
  readonly processing_time_ms: number;
  
  /** Query complexity score (0.0 to 1.0) */
  readonly complexity_score: number;
  
  /** Distribution of reasoning strategies used */
  readonly strategy_distribution?: Record<string, number>;
  
  /** Token budget information */
  readonly token_budget_used?: number;
  readonly token_budget_allocated?: number;
  
  /** Emotion context at reasoning start */
  readonly emotion_state?: Record<string, unknown>;
  
  /** Timestamps */
  readonly started_at?: string;
  readonly completed_at?: string;
}

/**
 * Token budget allocation details
 * Splits total budget between visible reasoning and final response
 */
export interface TokenBudget {
  /** Tokens allocated for visible reasoning steps */
  readonly reasoning_tokens: number;
  
  /** Tokens allocated for final answer */
  readonly response_tokens: number;
  
  /** Total token budget */
  readonly total_tokens: number;
  
  /** Query complexity that influenced budget (0.0 to 1.0) */
  readonly complexity_score: number;
  
  /** Adjustment factors */
  readonly emotion_factor: number;
  readonly cognitive_load_factor: number;
  readonly readiness_factor: number;
  
  /** Budget mode selected */
  readonly mode: BudgetMode;
}

/**
 * Thinking mode selection decision
 * Contains mode + confidence + reasoning for selection
 */
export interface ThinkingDecision {
  /** Selected thinking mode */
  readonly mode: ThinkingMode;
  
  /** Confidence in mode selection (0.0 to 1.0) */
  readonly confidence: number;
  
  /** Human-readable reasoning for selection */
  readonly reasoning: string;
  
  /** Factors that influenced decision */
  readonly complexity_score: number;
  readonly emotion_factor: number;
  readonly load_factor: number;
  readonly readiness_factor: number;
  
  /** Estimated processing requirements */
  readonly estimated_time_ms: number;
  readonly estimated_tokens: number;
}

/**
 * Request for reasoning-enabled chat
 * Extends normal chat request with reasoning controls
 */
export interface ReasoningRequest {
  /** User identifier */
  user_id: string;
  
  /** Session identifier (optional, creates new if not provided) */
  session_id?: string;
  
  /** User message/query */
  message: string;
  
  /** Enable visible reasoning (default: true) */
  enable_reasoning?: boolean;
  
  /** Force specific thinking mode (optional, auto-selects if not provided) */
  thinking_mode?: ThinkingMode;
  
  /** Maximum reasoning depth (1-10, default: 5) */
  max_reasoning_depth?: number;
  
  /** Additional context */
  context?: Record<string, unknown>;
}

/**
 * Enhanced chat response with reasoning chain
 * Includes all standard chat metadata plus reasoning information
 */
export interface ReasoningResponse {
  /** Session identifier */
  readonly session_id: string;
  
  /** Final AI response message */
  readonly message: string;
  
  /** Whether reasoning was enabled for this response */
  readonly reasoning_enabled: boolean;
  
  /** Reasoning chain (if reasoning was enabled) */
  readonly reasoning_chain?: ReasoningChain;
  
  /** Thinking mode used (if reasoning was enabled) */
  readonly thinking_mode?: ThinkingMode;
  
  /** Emotion state during reasoning */
  readonly emotion_state?: {
    primary_emotion: string;
    arousal: number;
    valence: number;
    learning_readiness: string;
  };
  
  /** AI provider used for generation */
  readonly provider_used: string;
  
  /** Total response time in milliseconds */
  readonly response_time_ms: number;
  
  /** ISO timestamp */
  readonly timestamp: string;
  
  /** Token usage and cost */
  readonly tokens_used?: number;
  readonly cost?: number;
  
  /** Additional metadata */
  readonly category_detected?: string;
  readonly context_retrieved?: unknown;
  readonly ability_info?: unknown;
  readonly cached?: boolean;
  readonly processing_breakdown?: unknown;
  
  /** RAG metadata */
  readonly rag_enabled?: boolean;
  readonly citations?: unknown[];
  readonly sources_count?: number;
  readonly search_provider?: string;
  
  /** ML-generated follow-up questions */
  readonly suggested_questions?: string[];
}

/**
 * Reasoning session document
 * Stored in database for analysis and improvement
 */
export interface ReasoningSessionDocument {
  /** Unique identifier */
  readonly id: string;
  
  /** User and session identifiers */
  readonly user_id: string;
  readonly session_id: string;
  
  /** Original query */
  readonly query: string;
  
  /** Thinking mode used */
  readonly thinking_mode: string;
  
  /** Reasoning steps (stored as JSON) */
  readonly reasoning_steps: readonly Record<string, unknown>[];
  readonly reasoning_depth: number;
  
  /** Emotion context */
  readonly emotion_state?: Record<string, unknown>;
  readonly cognitive_load: number;
  readonly learning_readiness: string;
  
  /** Token usage */
  readonly token_budget_allocated: number;
  readonly token_budget_used: number;
  readonly reasoning_tokens: number;
  readonly response_tokens: number;
  
  /** Performance metrics */
  readonly complexity_score: number;
  readonly total_confidence: number;
  readonly processing_time_ms: number;
  
  /** User feedback (optional) */
  readonly user_feedback_rating?: number;
  readonly user_feedback_helpful?: boolean;
  
  /** Timestamp */
  readonly created_at: string;
}

/**
 * Reasoning analytics for a user
 * Aggregated metrics across all reasoning sessions
 */
export interface ReasoningAnalytics {
  /** User identifier */
  readonly user_id: string;
  
  /** Thinking mode distribution */
  readonly thinking_mode_distribution: readonly {
    mode: ThinkingMode;
    count: number;
    avg_complexity: number;
    avg_confidence: number;
    avg_time_ms: number;
  }[];
  
  /** Total reasoning sessions */
  readonly total_reasoning_sessions: number;
  
  /** Average metrics */
  readonly avg_steps_per_session?: number;
  readonly avg_processing_time_ms?: number;
  readonly avg_complexity?: number;
  readonly avg_confidence?: number;
  
  /** Trends over time */
  readonly complexity_trend?: 'increasing' | 'decreasing' | 'stable';
  readonly confidence_trend?: 'improving' | 'declining' | 'stable';
}

/**
 * WebSocket event types for real-time reasoning streaming
 * Enables live display of thinking process as it happens
 */
export type ReasoningStreamEvent =
  | {
      type: 'thinking_started';
      estimated_duration_ms: number;
      thinking_mode: ThinkingMode;
    }
  | {
      type: 'thinking_mode_selected';
      mode: ThinkingMode;
      confidence: number;
      reasoning: string;
    }
  | {
      type: 'budget_allocated';
      budget: TokenBudget;
    }
  | {
      type: 'reasoning_step';
      step: ReasoningStep;
      total_steps_so_far: number;
    }
  | {
      type: 'reasoning_complete';
      total_steps: number;
      time_ms: number;
      conclusion?: string;
    }
  | {
      type: 'response_token';
      token: string;
      position: number;
    }
  | {
      type: 'complete';
      total_time_ms: number;
      message: string;
    }
  | {
      type: 'error';
      error: string;
      code?: string;
    };

/**
 * Reasoning display preferences
 * User preferences for how reasoning chains are displayed
 */
export interface ReasoningDisplayPreferences {
  /** Show reasoning by default */
  showReasoningByDefault: boolean;
  
  /** Auto-expand reasoning steps */
  autoExpandSteps: boolean;
  
  /** Show confidence scores */
  showConfidence: boolean;
  
  /** Show strategy labels */
  showStrategy: boolean;
  
  /** Show timing information */
  showTiming: boolean;
  
  /** Animation speed (0 = instant, 1 = normal, 2 = slow) */
  animationSpeed: 0 | 1 | 2;
  
  /** Compact mode (less visual space) */
  compactMode: boolean;
}

/**
 * Reasoning store state
 * Zustand store shape for reasoning feature
 */
export interface ReasoningStoreState {
  /** Current reasoning chain being displayed */
  currentChain: ReasoningChain | null;
  
  /** Reasoning chains history (keyed by session_id) */
  chains: Record<string, ReasoningChain[]>;
  
  /** Loading state */
  isLoading: boolean;
  
  /** Error state */
  error: string | null;
  
  /** Display preferences */
  preferences: ReasoningDisplayPreferences;
  
  /** Actions */
  setCurrentChain: (chain: ReasoningChain | null) => void;
  addChain: (sessionId: string, chain: ReasoningChain) => void;
  updateChain: (chainId: string, updates: Partial<ReasoningChain>) => void;
  clearChains: (sessionId?: string) => void;
  setPreferences: (preferences: Partial<ReasoningDisplayPreferences>) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

/**
 * Reasoning API client methods
 * Type definitions for API service functions
 */
export interface ReasoningAPI {
  /** Send reasoning-enabled chat request */
  chatWithReasoning: (request: ReasoningRequest) => Promise<ReasoningResponse>;
  
  /** Get reasoning session details */
  getReasoningSession: (sessionId: string) => Promise<{
    session_id: string;
    reasoning_sessions: readonly ReasoningSessionDocument[];
    total_reasoning_sessions: number;
    session_metadata: Record<string, unknown>;
  }>;
  
  /** Get reasoning analytics for user */
  getReasoningAnalytics: (userId: string) => Promise<ReasoningAnalytics>;
  
  /** Submit feedback on reasoning quality */
  submitReasoningFeedback: (
    sessionId: string,
    chainId: string,
    feedback: {
      rating: number;
      helpful: boolean;
      comments?: string;
    }
  ) => Promise<void>;
}

/**
 * Component prop types
 */

export interface ReasoningChainDisplayProps {
  /** Reasoning chain to display */
  reasoning: ReasoningChain;
  
  /** Whether chain is still streaming */
  isStreaming?: boolean;
  
  /** Additional CSS classes */
  className?: string;
  
  /** Callback when step is clicked */
  onStepClick?: (step: ReasoningStep) => void;
  
  /** Callback when feedback is submitted */
  onFeedback?: (rating: number, helpful: boolean) => void;
}

export interface ThinkingIndicatorProps {
  /** Thinking mode being used */
  mode: ThinkingMode;
  
  /** Current step number (if available) */
  currentStep?: number;
  
  /** Total steps (if known) */
  totalSteps?: number;
  
  /** Estimated time remaining (milliseconds) */
  estimatedTimeMs?: number;
  
  /** Additional CSS classes */
  className?: string;
}

export interface ReasoningToggleProps {
  /** Whether reasoning is enabled */
  enabled: boolean;
  
  /** Callback when toggle changes */
  onChange: (enabled: boolean) => void;
  
  /** Disabled state */
  disabled?: boolean;
  
  /** Additional CSS classes */
  className?: string;
  
  /** Show label */
  showLabel?: boolean;
}
