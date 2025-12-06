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

import { v4 as uuidv4 } from 'uuid';
import apiClient from './client';
import nativeSocketClient from '../websocket/native-socket.client';
import type { 
  ChatRequest, 
  ChatResponse, 
  ChatHistoryResponse,
  StreamEvent 
} from '../../types/chat.types';

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
    const { data } = await apiClient.post<ChatResponse>(
      '/api/v1/chat',
      request,
      {
        timeout: 30000, // 30 seconds (AI processing can take time)
      }
    );
    return data;
  },

  /**
   * Send a streaming chat message via WebSocket
   * 
   * Triggers real-time streaming response with:
   * - Thinking phase (reasoning steps)
   * - Content phase (token-by-token response)
   * - Emotion updates
   * - Context information
   * - Cancellation support
   * 
   * This provides a ChatGPT-like streaming experience where tokens
   * appear in real-time as the AI generates them.
   * 
   * @param request - Chat request (same as sendMessage)
   * @param onEvent - Callback for each streaming event
   * @returns Cancellation function to stop generation
   * 
   * @example
   * ```typescript
   * const cancel = chatAPI.streamMessage(
   *   {
   *     user_id: 'user-123',
   *     message: 'Explain quantum computing',
   *     session_id: 'session-abc',
   *     context: { subject: 'physics' }
   *   },
   *   (event) => {
   *     if (event.type === 'content_chunk') {
   *       console.log('Chunk:', event.data.content);
   *     } else if (event.type === 'stream_complete') {
   *       console.log('Complete:', event.data.full_content);
   *     }
   *   }
   * );
   * 
   * // Cancel if needed
   * cancel();
   * ```
   */
  streamMessage: (
    request: ChatRequest,
    onEvent: (event: StreamEvent) => void
  ): (() => void) => {
    // Generate client-side message ID for tracking
    const messageId = uuidv4();
    const sessionId = request.session_id || uuidv4();
    
    // Build WebSocket message
    const wsMessage = {
      type: 'chat_stream',
      data: {
        message_id: messageId,
        session_id: sessionId,
        user_id: request.user_id,
        message: request.message,
        context: request.context || {}
      }
    };
    
    // Subscribe to ALL streaming events for this message
    const eventTypes: Array<WebSocketEvent> = [
      'stream_start',
      'thinking_chunk',
      'content_chunk',
      'emotion_update',
      'context_info',
      'stream_complete',
      'stream_error',
      'generation_stopped'
    ];
    
    const unsubscribers: Array<() => void> = [];
    
    // Register handlers for each event type
    eventTypes.forEach(eventType => {
      const unsubscribe = nativeSocketClient.on(eventType, (data: any) => {
        // Filter by message_id to ensure we only handle events for this specific message
        if (data.message_id === messageId) {
          onEvent({
            type: eventType,
            data
          } as StreamEvent);
        }
      });
      
      unsubscribers.push(unsubscribe);
    });
    
    // Send chat_stream request
    nativeSocketClient.send('chat_stream' as any, wsMessage.data);
    
    // Return cancellation function
    return () => {
      // Unsubscribe from all events
      unsubscribers.forEach(unsub => unsub());
      
      // Send stop_generation message
      nativeSocketClient.send('stop_generation' as any, {
        message_id: messageId,
        session_id: sessionId
      });
    };
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