// **Purpose:** Manage chat messages, conversation history, real-time updates

// **What This File Contributes:**
// 1. Message list management (add, update, delete)
// 2. Typing indicators
// 3. Real-time emotion updates
// 4. Conversation context
// 5. Optimistic UI updates

// **Implementation:**
// ```typescript
import { create } from 'zustand';
import { chatAPI } from '@/services/api/chat.api';
import { MessageRole } from '@/types/chat.types';
import type { 
  Message, 
  ChatRequest, 
  ChatResponse, 
  SuggestedQuestion,
  StreamEvent,
  StreamingMessage 
} from '@/types/chat.types';
import type { EmotionState } from '@/types/emotion.types';

interface ChatState {
  // State
  messages: Message[];
  isTyping: boolean;
  isLoading: boolean;
  currentEmotion: EmotionState | null;
  sessionId: string | null;
  error: string | null;
  suggestedQuestions: SuggestedQuestion[]; // ML-generated follow-up questions
  
  // NEW: Streaming state
  isStreaming: boolean;
  streamingMessageId: string | null;
  streamingContent: string;
  cancelStream: (() => void) | null;
  
  // Actions
  sendMessage: (content: string, userId: string) => Promise<void>;
  streamMessage: (content: string, userId: string, options?: { subject?: string; enableReasoning?: boolean }) => void; // NEW
  stopStreaming: () => void; // NEW
  addMessage: (message: Message) => void;
  updateMessageEmotion: (messageId: string, emotion: EmotionState) => void;
  clearMessages: () => void;
  clearError: () => void;
  loadHistory: (sessionId: string) => Promise<void>;
  setTyping: (isTyping: boolean) => void;
  setCurrentEmotion: (emotion: EmotionState | null) => void;
  setSuggestedQuestions: (questions: SuggestedQuestion[]) => void; // Set ML questions
  clearSuggestedQuestions: () => void; // Clear questions when new message sent
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  isTyping: false,
  isLoading: false,
  currentEmotion: null,
  sessionId: null,
  error: null,
  suggestedQuestions: [], // ML-generated questions
  
  // NEW: Streaming state
  isStreaming: false,
  streamingMessageId: null,
  streamingContent: '',
  cancelStream: null,
  
  // Send message action
  sendMessage: async (content: string, userId: string) => {
    const { sessionId } = get();
    
    // Optimistic update: Add user message immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: sessionId || '',
      user_id: userId,
      role: MessageRole.USER,
      content,
      timestamp: new Date().toISOString(),
      emotion_state: null,
    };
    
    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      isTyping: true,
      error: null,
      suggestedQuestions: [], // Clear previous questions when sending new message
    }));
    
    try {
      // Call backend API
      const request: ChatRequest = {
        message: content,
        user_id: userId,
        session_id: sessionId || undefined,
      };
      
      const response: ChatResponse = await chatAPI.sendMessage(request);
      
      // Replace temp message with confirmed user message
      const confirmedUserMessage: Message = {
        ...userMessage,
        session_id: response.session_id,
      };
      
      // Add AI response
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        session_id: response.session_id,
        user_id: 'assistant',
        role: MessageRole.ASSISTANT,
        content: response.message,
        timestamp: response.timestamp,
        emotion_state: response.emotion_state || null,
        provider_used: response.provider_used,
        response_time_ms: response.response_time_ms,
        tokens_used: response.tokens_used,
        cost: response.cost,
        suggested_questions: response.suggested_questions || [], // ✅ ATTACH ML questions to message
      };
      
      set((state) => ({
        messages: [
          ...state.messages.filter((msg) => msg.id !== userMessage.id),
          confirmedUserMessage,
          aiMessage,
        ],
        isLoading: false,
        isTyping: false,
        currentEmotion: response.emotion_state || null,
        sessionId: response.session_id,
        suggestedQuestions: response.suggested_questions || [], // Set ML-generated questions
      }));
    } catch (error: any) {
      // Remove optimistic message on error
      set((state) => ({
        messages: state.messages.filter((msg) => msg.id !== userMessage.id),
        isLoading: false,
        isTyping: false,
        error: error.message || 'Failed to send message',
      }));
      throw error;
    }
  },
  
  // NEW: Stream message with real-time token-by-token response
  streamMessage: (content: string, userId: string, options = {}) => {
    const { sessionId } = get();
    
    // Add user message immediately (optimistic)
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      session_id: sessionId || '',
      user_id: userId,
      role: MessageRole.USER,
      content,
      timestamp: new Date().toISOString(),
      emotion_state: null,
    };
    
    // Create placeholder for streaming AI message
    const aiMessageId = `ai-${Date.now()}`;
    
    set((state) => ({
      messages: [...state.messages, userMessage],
      isStreaming: true,
      streamingMessageId: aiMessageId,
      streamingContent: '',
      isTyping: true,
      error: null,
      suggestedQuestions: [], // Clear previous questions
    }));
    
    try {
      // Start streaming via WebSocket
      const cancel = chatAPI.streamMessage(
        {
          message: content,
          user_id: userId,
          session_id: sessionId || undefined,
          context: {
            subject: options.subject,
            enable_reasoning: options.enableReasoning,
          },
        },
        (event: StreamEvent) => {
          // Handle each streaming event
          const state = get();
          
          switch (event.type) {
            case 'stream_start':
              // Update session ID if new session
              if (event.data.session_id && !state.sessionId) {
                set({ sessionId: event.data.session_id });
              }
              break;
            
            case 'content_chunk':
              // Append content chunk to streaming message
              set((prevState) => ({
                streamingContent: prevState.streamingContent + event.data.content,
              }));
              break;
            
            case 'emotion_update':
              // Update current emotion
              set({
                currentEmotion: event.data.emotion,
              });
              break;
            
            case 'stream_complete':
              // Finalize streaming message
              const completedMessage: Message = {
                id: event.data.ai_message_id,
                session_id: event.data.session_id,
                user_id: 'assistant',
                role: MessageRole.ASSISTANT,
                content: event.data.full_content,
                timestamp: event.data.timestamp,
                emotion_state: state.currentEmotion,
                provider_used: event.data.metadata.provider_used,
                response_time_ms: event.data.metadata.response_time_ms,
                tokens_used: event.data.metadata.tokens_used,
                cost: event.data.metadata.cost,
              };
              
              set((prevState) => ({
                messages: [...prevState.messages, completedMessage],
                isStreaming: false,
                streamingMessageId: null,
                streamingContent: '',
                isTyping: false,
                cancelStream: null,
              }));
              break;
            
            case 'stream_error':
              // Handle streaming error
              const errorMessage = event.data.error.message || 'Streaming failed';
              
              // If partial content exists, add it as a message
              if (event.data.partial_content) {
                const partialMessage: Message = {
                  id: `ai-partial-${Date.now()}`,
                  session_id: event.data.session_id,
                  user_id: 'assistant',
                  role: MessageRole.ASSISTANT,
                  content: event.data.partial_content + '\n\n[Generation incomplete due to error]',
                  timestamp: event.data.timestamp,
                  emotion_state: state.currentEmotion,
                };
                
                set((prevState) => ({
                  messages: [...prevState.messages, partialMessage],
                  isStreaming: false,
                  streamingMessageId: null,
                  streamingContent: '',
                  isTyping: false,
                  error: errorMessage,
                  cancelStream: null,
                }));
              } else {
                set({
                  isStreaming: false,
                  streamingMessageId: null,
                  streamingContent: '',
                  isTyping: false,
                  error: errorMessage,
                  cancelStream: null,
                });
              }
              break;
            
            case 'generation_stopped':
              // User cancelled or timeout
              if (event.data.partial_content) {
                const stoppedMessage: Message = {
                  id: event.data.ai_message_id,
                  session_id: event.data.session_id,
                  user_id: 'assistant',
                  role: MessageRole.ASSISTANT,
                  content: event.data.partial_content + '\n\n[Generation stopped]',
                  timestamp: event.data.timestamp,
                  emotion_state: state.currentEmotion,
                };
                
                set((prevState) => ({
                  messages: [...prevState.messages, stoppedMessage],
                  isStreaming: false,
                  streamingMessageId: null,
                  streamingContent: '',
                  isTyping: false,
                  cancelStream: null,
                }));
              } else {
                set({
                  isStreaming: false,
                  streamingMessageId: null,
                  streamingContent: '',
                  isTyping: false,
                  cancelStream: null,
                });
              }
              break;
          }
        }
      );
      
      // Store cancel function
      set({ cancelStream: cancel });
      
    } catch (error: any) {
      // Handle error
      set((state) => ({
        messages: state.messages.filter((msg) => msg.id !== userMessage.id),
        isStreaming: false,
        streamingMessageId: null,
        streamingContent: '',
        isTyping: false,
        error: error.message || 'Failed to start streaming',
        cancelStream: null,
      }));
    }
  },
  
  // NEW: Stop ongoing streaming
  stopStreaming: () => {
    const { cancelStream } = get();
    if (cancelStream) {
      cancelStream();
    }
    set({
      isStreaming: false,
      streamingMessageId: null,
      streamingContent: '',
      cancelStream: null,
    });
  },
  
  // Add message (for WebSocket updates)
  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },
  
  // Update emotion for existing message
  updateMessageEmotion: (messageId, emotion) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === messageId ? { ...msg, emotion_state: emotion } : msg
      ),
      currentEmotion: emotion,
    }));
  },
  
  // Clear all messages
  clearMessages: () => {
    set({
      messages: [],
      currentEmotion: null,
      sessionId: null,
      error: null,
    });
  },
  
  // Clear error
  clearError: () => {
    set({ error: null });
  },
  
  // Load message history
  loadHistory: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      // TODO: Backend endpoint /api/v1/chat/history/{sessionId} not yet implemented
      // For now, we'll maintain messages in the store from sendMessage responses
      // When the endpoint is available, uncomment below:
      
      // const messages = await chatAPI.getHistory(sessionId);
      // set({
      //   messages,
      //   sessionId,
      //   isLoading: false,
      // });
      
      // Temporary implementation: just set the sessionId
      set({
        sessionId,
        isLoading: false,
      });
      
      console.warn('[ChatStore] History endpoint not implemented yet. Messages will be loaded from sendMessage responses.');
    } catch (error: any) {
      set({
        error: error.message || 'Failed to load history',
        isLoading: false,
      });
      throw error;
    }
  },
  
  // Set typing indicator
  setTyping: (isTyping) => set({ isTyping }),
  
  // Set current emotion
  setCurrentEmotion: (emotion) => set({ currentEmotion: emotion }),
  
  // Set ML-generated suggested questions
  setSuggestedQuestions: (questions) => set({ suggestedQuestions: questions }),
  
  // Clear suggested questions (e.g., when starting new topic)
  clearSuggestedQuestions: () => set({ suggestedQuestions: [] }),
}));


// **Key Features:**
// 1. **Optimistic updates:** Instant UI feedback (feels fast)
// 2. **Real-time emotion:** Updates as AI analyzes
// 3. **Error handling:** Rollback on API failure
// 4. **Session management:** Track conversation context

// **Performance:**
// - Optimistic update: 0ms perceived latency
// - Only re-renders <MessageList> when messages change
// - Efficient array updates (immutable patterns)

// **Connected Files:**
// - ← `services/api/chat.api.ts` (API calls)
// - ← `types/chat.types.ts`, `types/emotion.types.ts` (types)
// - → `components/chat/MessageList.tsx` (displays messages)
// - → `components/chat/MessageInput.tsx` (uses sendMessage)
// - → `components/emotion/EmotionWidget.tsx` (displays currentEmotion)
// - ← `services/websocket/socket.client.ts` (real-time updates)

// **Integration with Backend:**
// ```
// POST /api/v1/chat              ← chatAPI.sendMessage()
// WebSocket /ws/chat             ← Real-time emotion updates