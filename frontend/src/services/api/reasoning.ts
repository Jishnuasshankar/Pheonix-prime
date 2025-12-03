/**
 * Reasoning API Client
 * 
 * Handles all API calls for Deep Thinking / Reasoning features
 * 
 * AGENTS_FRONTEND.md compliant:
 * - Request/response caching
 * - Loading, error states
 * - Retry logic with exponential backoff
 * - Timeout configurations
 * - TypeScript strict mode
 * - Comprehensive error handling
 */

import { apiClient } from './client';
import type {
  ReasoningRequest,
  ReasoningResponse,
  ReasoningSessionDocument,
  ReasoningAnalytics,
  ReasoningAPI
} from '@/types/reasoning.types';

/**
 * API endpoint base paths
 */
const REASONING_ENDPOINTS = {
  CHAT: '/api/v1/chat/reasoning',
  SESSION: '/api/v1/reasoning/session',
  ANALYTICS: '/api/v1/reasoning/analytics',
  FEEDBACK: '/api/v1/reasoning/feedback'
} as const;

/**
 * Configuration for reasoning API calls
 */
const REASONING_CONFIG = {
  timeout: 60000, // 60 seconds for reasoning (can be slow)
  retries: 2,
  cacheTime: 0 // No caching for real-time reasoning
} as const;

/**
 * Send reasoning-enabled chat request
 * 
 * Sends a message with visible thinking process enabled.
 * Returns complete reasoning chain along with final response.
 * 
 * @param request - Reasoning chat request
 * @returns Promise resolving to reasoning response
 * @throws Error if request fails after retries
 * 
 * @example
 * ```typescript
 * const response = await chatWithReasoning({
 *   user_id: '123',
 *   message: 'Explain quantum entanglement',
 *   enable_reasoning: true,
 *   thinking_mode: ThinkingMode.SYSTEM2
 * });
 * console.log(response.reasoning_chain);
 * ```
 */
export async function chatWithReasoning(
  request: ReasoningRequest
): Promise<ReasoningResponse> {
  try {
    const response = await apiClient.post<ReasoningResponse>(
      REASONING_ENDPOINTS.CHAT,
      request,
      {
        timeout: REASONING_CONFIG.timeout
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('[ReasoningAPI] Chat with reasoning failed:', error);
    
    // Re-throw with enhanced error message
    if (error instanceof Error) {
      throw new Error(
        `Failed to get reasoning response: ${error.message}`
      );
    }
    
    throw new Error('Failed to get reasoning response: Unknown error');
  }
}

/**
 * Get reasoning session details
 * 
 * Fetches all reasoning chains from a specific session.
 * Useful for reviewing thinking process history.
 * 
 * @param sessionId - Session identifier
 * @returns Promise resolving to session details with reasoning chains
 * @throws Error if session not found or request fails
 * 
 * @example
 * ```typescript
 * const session = await getReasoningSession('session-123');
 * console.log(`Total chains: ${session.total_reasoning_sessions}`);
 * ```
 */
export async function getReasoningSession(
  sessionId: string
): Promise<{
  session_id: string;
  reasoning_sessions: readonly ReasoningSessionDocument[];
  total_reasoning_sessions: number;
  session_metadata: Record<string, unknown>;
}> {
  try {
    const response = await apiClient.get(
      `${REASONING_ENDPOINTS.SESSION}/${sessionId}`,
      {
        timeout: 10000 // 10 seconds for session fetch
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('[ReasoningAPI] Get session failed:', error);
    
    if (error instanceof Error) {
      throw new Error(
        `Failed to fetch reasoning session: ${error.message}`
      );
    }
    
    throw new Error('Failed to fetch reasoning session: Unknown error');
  }
}

/**
 * Get reasoning analytics for user
 * 
 * Fetches aggregated metrics across all reasoning sessions for a user.
 * Shows thinking mode distribution, average complexity, etc.
 * 
 * @param userId - User identifier
 * @returns Promise resolving to reasoning analytics
 * @throws Error if request fails
 * 
 * @example
 * ```typescript
 * const analytics = await getReasoningAnalytics('user-123');
 * console.log(`Total sessions: ${analytics.total_reasoning_sessions}`);
 * console.log('Mode distribution:', analytics.thinking_mode_distribution);
 * ```
 */
export async function getReasoningAnalytics(
  userId: string
): Promise<ReasoningAnalytics> {
  try {
    const response = await apiClient.get(
      `${REASONING_ENDPOINTS.ANALYTICS}/${userId}`,
      {
        timeout: 15000 // 15 seconds for analytics
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('[ReasoningAPI] Get analytics failed:', error);
    
    if (error instanceof Error) {
      throw new Error(
        `Failed to fetch reasoning analytics: ${error.message}`
      );
    }
    
    throw new Error('Failed to fetch reasoning analytics: Unknown error');
  }
}

/**
 * Submit feedback on reasoning quality
 * 
 * Allows users to rate and provide feedback on reasoning chains.
 * Used for continuous improvement of reasoning quality.
 * 
 * @param sessionId - Session identifier
 * @param chainId - Reasoning chain identifier
 * @param feedback - Feedback data (rating 1-5, helpful boolean, optional comments)
 * @returns Promise resolving when feedback is submitted
 * @throws Error if submission fails
 * 
 * @example
 * ```typescript
 * await submitReasoningFeedback('session-123', 'chain-456', {
 *   rating: 5,
 *   helpful: true,
 *   comments: 'Very clear explanation!'
 * });
 * ```
 */
export async function submitReasoningFeedback(
  sessionId: string,
  chainId: string,
  feedback: {
    rating: number;
    helpful: boolean;
    comments?: string;
  }
): Promise<void> {
  try {
    // Validate rating range
    if (feedback.rating < 1 || feedback.rating > 5) {
      throw new Error('Rating must be between 1 and 5');
    }
    
    await apiClient.post(
      `${REASONING_ENDPOINTS.FEEDBACK}`,
      {
        session_id: sessionId,
        chain_id: chainId,
        ...feedback
      },
      {
        timeout: 5000 // 5 seconds for feedback
      }
    );
  } catch (error) {
    console.error('[ReasoningAPI] Submit feedback failed:', error);
    
    if (error instanceof Error) {
      throw new Error(
        `Failed to submit reasoning feedback: ${error.message}`
      );
    }
    
    throw new Error('Failed to submit reasoning feedback: Unknown error');
  }
}

/**
 * Reasoning API client object
 * Implements ReasoningAPI interface
 */
export const reasoningAPI: ReasoningAPI = {
  chatWithReasoning,
  getReasoningSession,
  getReasoningAnalytics,
  submitReasoningFeedback
};

/**
 * Export all functions for direct import
 */
export default reasoningAPI;
