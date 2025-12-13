/**
 * Chat API Service
 * 
 * Handles all chat-related API calls:
 * - Send messages to backend with emotion detection
 * - Process AI responses with context and adaptation
 * - Real-time learning interactions
 * 
 * Backend Integration:
 * POST /api/v1/chat - Main learning interaction endpoint
 * 
 * The chat endpoint handles:
 * - Emotion detection (frustration, confusion, etc.)
 * - Context management (conversation memory)
 * - Adaptive learning (difficulty adjustment)
 * - Provider selection (best AI model)
 * - Cost tracking
 * 
 * @module services/api/chat.api
 */

import apiClient from './client';
import type { ChatRequest, ChatResponse, ChatHistoryResponse } from '../../types/chat.types';

/**
 * Chat API endpoints
 */
export const chatAPI = {
  /**
   * Send a chat message
   * 
   * Processes user message through the full MasterX pipeline:
   * 1. Emotion detection (identifies frustration, confusion, etc.)
   * 2. Context retrieval (loads relevant conversation history)
   * 3. Adaptive learning (adjusts difficulty to student's ability)
   * 4. Provider selection (chooses best AI model for task)
   * 5. Response generation (personalized, emotion-aware response)
   * 
   * Session Handling:
   * - If session_id provided: Continues existing conversation
   * - If no session_id: Creates new session automatically
   * 
   * @param request - Chat request with message and context
   * @param request.user_id - User identifier (required)
   * @param request.message - User's message text (required)
   * @param request.session_id - Optional: existing session ID
   * @param request.context - Optional: additional context (subject, etc.)
   * @returns Chat response with AI message and metadata
   * 
   * Response includes:
   * - message: AI-generated response text
   * - emotion_state: Detected emotions and learning readiness
   * - session_id: Session identifier for follow-up messages
   * - provider_used: Which AI model was used (gemini, claude, etc.)
   * - response_time_ms: Processing time
   * - cost: Cost in USD for this interaction
   * - context_retrieved: Relevant conversation history used
   * - ability_info: Student's current ability level
   * 
   * @throws 404 - Session not found (if invalid session_id)
   * @throws 500 - Chat processing failed
   * 
   * @example
   * ```typescript
   * const response = await chatAPI.sendMessage({
   *   user_id: 'user-123',
   *   message: "I'm frustrated with this calculus problem",
   *   session_id: 'session-abc', // optional
   *   context: { subject: 'calculus' } // optional
   * });
   * 
   * // Response includes emotion detection
   * console.log(response.emotion_state.primary_emotion); // "frustration"
   * console.log(response.emotion_state.learning_readiness); // "STRUGGLING"
   * 
   * // AI response is personalized based on emotion
   * console.log(response.message); // Encouraging, supportive response
   * ```
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const { data } = await apiClient.post<ChatResponse>(
        '/api/v1/chat',
        request,
        {
          timeout: 30000, // 30 seconds (AI processing can take time)
        }
      );
      
      // ✅ ROBUST: Parse and validate suggested_questions from response
      let parsedData = data;
      
      try {
        // Handle case where suggested_questions might be stringified JSON
        if (data.suggested_questions && typeof data.suggested_questions === 'string') {
          console.warn('[ChatAPI] suggested_questions is a string, parsing JSON:', data.suggested_questions);
          parsedData = {
            ...data,
            suggested_questions: JSON.parse(data.suggested_questions as unknown as string)
          };
        }
        
        // Ensure suggested_questions is an array (or undefined/null)
        if (parsedData.suggested_questions && !Array.isArray(parsedData.suggested_questions)) {
          console.error('[ChatAPI] suggested_questions is not an array, converting:', parsedData.suggested_questions);
          parsedData = {
            ...parsedData,
            suggested_questions: [parsedData.suggested_questions as any]
          };
        }
      } catch (parseError) {
        console.error('[ChatAPI] Failed to parse suggested_questions, setting to empty array:', parseError);
        parsedData = {
          ...data,
          suggested_questions: []
        };
      }
      
      // ✅ DEBUG: Log the complete response to check suggested_questions
      console.log('[ChatAPI] sendMessage response:', {
        hasData: !!parsedData,
        hasSuggestedQuestions: !!parsedData.suggested_questions,
        suggestedQuestionsType: typeof parsedData.suggested_questions,
        suggestedQuestionsIsArray: Array.isArray(parsedData.suggested_questions),
        suggestedQuestionsLength: Array.isArray(parsedData.suggested_questions) ? parsedData.suggested_questions.length : 'N/A',
        rawSuggestedQuestions: parsedData.suggested_questions,
        fullResponse: parsedData,
      });
      
      return parsedData;
    } catch (error) {
      console.error('[ChatAPI] sendMessage error:', error);
      throw error;
    }
  },

  /**
   * Get conversation history
   * 
   * Retrieves all messages from a specific session for displaying
   * conversation history when user returns to a previous chat.
   * 
   * Returns messages in chronological order with full metadata:
   * - User and AI messages
   * - Emotion states detected
   * - Providers used
   * - Response times and costs
   * 
   * Use Cases:
   * - Loading previous conversations on app start
   * - Displaying chat history when switching sessions
   * - Exporting conversation data
   * - Analytics and review
   * 
   * @param sessionId - Session identifier (UUID)
   * @returns Chat history with messages and metadata
   * 
   * @throws 404 - Session not found
   * @throws 500 - Failed to fetch history
   * 
   * @example
   * ```typescript
   * const history = await chatAPI.getHistory('session-abc-123');
   * 
   * console.log(`${history.total_messages} messages`);
   * console.log(`Session started: ${history.session_started}`);
   * console.log(`Total cost: $${history.total_cost}`);
   * 
   * // Display messages
   * history.messages.forEach(msg => {
   *   console.log(`[${msg.role}]: ${msg.content}`);
   *   if (msg.emotion_state) {
   *     console.log(`  Emotion: ${msg.emotion_state.primary_emotion}`);
   *   }
   * });
   * ```
   */
  getHistory: async (sessionId: string): Promise<ChatHistoryResponse> => {
    const { data } = await apiClient.get<ChatHistoryResponse>(
      `/api/v1/chat/history/${sessionId}`
    );
    return data;
  },
};