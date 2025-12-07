# WEBSOCKET IMPLEMENTATION GUIDE
## Bi-Directional Real-Time Streaming for MasterX Chat Engine

**Version:** 1.0.0  
**Status:** Architecture Design (Pre-Implementation)  
**Created:** 2025-12-06  
**Author:** Elite Full-Stack Architect Team

---

## TABLE OF CONTENTS

Development Progress

1. [Executive Summary](#executive-summary)
2. [Current Architecture Analysis](#current-architecture-analysis)
3. [Protocol Specification](#protocol-specification)
4. [Backend Implementation Blueprint](#backend-implementation-blueprint)
5. [Frontend Implementation Blueprint](#frontend-implementation-blueprint)
6. [Integration Checklist](#integration-checklist)
7. [Testing Strategy](#testing-strategy)
8. [Performance & Security](#performance--security)
9. [Rollback Plan](#rollback-plan)

---


# Development Progress

Phase 1: Backend Models (core/models.py) Completed ✅
Phase 2: AI Provider Streaming (core/ai_providers.py) Completed ✅
Phase 3: Engine Streaming (core/engine.py) Completed ✅
Phase 4: WebSocket Handlers (services/websocket_service.py, server.py) Completed ✅
  - server.py: WebSocket endpoint now handles chat_stream and stop_generation messages
  - Integrated engine.process_request_stream() for actual streaming
  - Added proper error handling and message validation
Phase 5: Frontend Types & Handlers  In Progress 🔄
Phase 6: Integration Testing Not completed 🚫

## EXECUTIVE SUMMARY

### Objective
Upgrade the MasterX chat engine from **HTTP Request-Response** to **Bi-Directional WebSocket Streaming** for real-time AI response streaming with:
- **Thinking Phase**: Stream reasoning steps as they occur
- **Content Phase**: Stream response content token-by-token
- **Cancellation Support**: User can stop generation mid-stream
- **Error Handling**: Graceful degradation with fallback to HTTP

### Current State (Truth Check)
✅ **WebSocket Infrastructure EXISTS** - `/app/backend/services/websocket_service.py`
- Enterprise-grade ConnectionManager with ML-based health monitoring
- Message prioritization queue
- Adaptive rate limiting
- Security validation
- Analytics tracking

✅ **WebSocket Endpoint EXISTS** - `server.py:3049` (`@app.websocket("/api/ws")`)
- JWT authentication via query parameter
- Connection management
- Basic message handling (typing indicators, session events)

✅ **Frontend WebSocket Hook EXISTS** - `/app/frontend/src/hooks/useWebSocket.ts`
- Auto-connect/disconnect lifecycle
- Event subscription pattern
- Connection state tracking

### Gap Analysis
❌ **Missing**: Streaming chat response integration with WebSocket
- Current `/api/v1/chat` is HTTP POST with single response
- `MasterXEngine.process_request()` returns full response, doesn't stream
- No cancellation mechanism for in-flight AI requests
- Frontend chat uses REST API, not WebSocket for messages

---

## CURRENT ARCHITECTURE ANALYSIS

### 1. Data Flow Mapping (HTTP - Current)

```
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND: ChatContainer.tsx                                         │
│                                                                      │
│  1. User types message in MessageInput                              │
│  2. Calls chatAPI.sendMessage(request)                              │
│     └─> POST /api/v1/chat                                          │
│                                                                      │
│  3. Shows loading state (TypingIndicator)                          │
│  4. Waits for full HTTP response (blocking)                        │
│  5. Updates UI with complete message                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                        HTTP Request
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND: server.py → @app.post("/api/v1/chat")                     │
│                                                                      │
│  1. Validates JWT token (from headers)                              │
│  2. Gets/creates session in MongoDB                                 │
│  3. Saves user message to messages collection                       │
│  4. Calls engine.process_request(user_id, message, session_id)      │
│     │                                                                │
│     ├─> MasterXEngine.process_request() in core/engine.py:         │
│     │   ├─ Step 1: Retrieve context (ContextManager)               │
│     │   ├─ Step 2: Analyze emotion (EmotionEngine)                 │
│     │   ├─ Step 3: Adaptive difficulty (AdaptiveLearningEngine)    │
│     │   ├─ Step 4: RAG augmentation (RAGEngine - optional)         │
│     │   ├─ Step 5: Provider selection (ProviderManager)            │
│     │   └─ Step 6: AI generation (Universal provider call)         │
│     │              ↓                                                 │
│     │       Returns AIResponse (full response string)               │
│     │                                                                │
│  5. Saves AI message to MongoDB                                     │
│  6. Sends emotion update via WebSocket (async, best-effort)        │
│  7. Updates session statistics                                      │
│  8. Returns ChatResponse (complete)                                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                       HTTP Response
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND: Receives full response, renders immediately              │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Findings:**
- **File**: `server.py:1282-1420` - `/api/v1/chat` endpoint
- **File**: `core/engine.py:149-450` - `process_request()` method
- **File**: `services/api/chat.api.ts:80-89` - Frontend API call
- **Limitation**: No streaming, no cancellation, blocking wait

---

### 2. Integration Points Identified

#### Backend Integration Points

| File | Function/Class | Integration Required |
|------|---------------|---------------------|
| `server.py` | `@app.websocket("/api/ws")` | Add `chat_stream` message type handler |
| `core/engine.py` | `MasterXEngine.process_request()` | Refactor to `process_request_stream()` with `yield` |
| `core/ai_providers.py` | `UniversalProvider.generate()` | Add streaming support via provider APIs |
| `services/websocket_service.py` | `handle_websocket_message()` | Add `chat_stream` and `stop_generation` handlers |
| `core/models.py` | Pydantic schemas | Add streaming message schemas |

#### Frontend Integration Points

| File | Component/Hook | Integration Required |
|------|----------------|---------------------|
| `components/chat/ChatContainer.tsx` | Main chat UI | Add streaming state machine |
| `hooks/useWebSocket.ts` | WebSocket connection | Already exists ✓ |
| `services/api/chat.api.ts` | API service | Add `streamMessage()` function |
| `types/chat.types.ts` | TypeScript types | Add streaming event types |
| `store/chatStore.ts` | State management | Add streaming message handling |

---

## PROTOCOL SPECIFICATION

### WebSocket Message Schemas

#### Client → Server Events

##### 1. Chat Stream Request
```typescript
{
  "type": "chat_stream",
  "data": {
    "message_id": "uuid",           // Client-generated for tracking
    "session_id": "uuid",           // Session identifier
    "user_id": "uuid",              // User identifier
    "message": "string",            // User message
    "context": {                    // Optional context
      "subject": "string",
      "enable_rag": boolean,
      "enable_reasoning": boolean   // NEW: Deep thinking mode
    }
  }
}
```

##### 2. Stop Generation
```typescript
{
  "type": "stop_generation",
  "data": {
    "message_id": "uuid",           // ID of message to cancel
    "session_id": "uuid"            // Session identifier
  }
}
```

##### 3. Configuration Update (Optional)
```typescript
{
  "type": "update_stream_config",
  "data": {
    "session_id": "uuid",
    "config": {
      "streaming_enabled": boolean,
      "chunk_delay_ms": number      // Artificial delay for UX
    }
  }
}
```

---

#### Server → Client Events

##### 1. Stream Start
```typescript
{
  "type": "stream_start",
  "data": {
    "message_id": "uuid",           // Echo from request
    "session_id": "uuid",
    "ai_message_id": "uuid",        // Server-generated ID for AI message
    "timestamp": "ISO8601",
    "metadata": {
      "provider": "gemini",         // Selected AI provider
      "category": "coding",         // Detected category
      "estimated_tokens": number    // Optional: token estimate
    }
  }
}
```

##### 2. Thinking Chunk (Reasoning Phase)
```typescript
{
  "type": "thinking_chunk",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "reasoning_step": {
      "step_number": number,        // 1, 2, 3...
      "thinking_mode": "analytical" | "creative" | "metacognitive",
      "description": "string",      // What AI is thinking about
      "confidence": number,         // 0.0-1.0
      "timestamp": "ISO8601"
    }
  }
}
```

##### 3. Content Chunk (Response Phase)
```typescript
{
  "type": "content_chunk",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "content": "string",            // Token(s) of response text
    "chunk_index": number,          // Sequential chunk number
    "is_code": boolean,             // Optional: code block detection
    "timestamp": "ISO8601"
  }
}
```

##### 4. Emotion Update (Real-time)
```typescript
{
  "type": "emotion_update",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "emotion": {
      "primary_emotion": "string",  // e.g., "curiosity"
      "arousal": number,            // -1.0 to 1.0
      "valence": number,            // -1.0 to 1.0
      "learning_readiness": "optimal_readiness" | "high_readiness" | "moderate_readiness" | "low_readiness" | "not_ready"
    },
    "timestamp": "ISO8601"
  }
}
```

##### 5. Context Info (Metadata)
```typescript
{
  "type": "context_info",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "context": {
      "recent_messages_used": number,
      "relevant_messages_used": number,
      "semantic_search_enabled": boolean,
      "rag_enabled": boolean,
      "rag_sources": number         // If RAG used
    },
    "timestamp": "ISO8601"
  }
}
```

##### 6. Stream Complete (Success)
```typescript
{
  "type": "stream_complete",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "ai_message_id": "uuid",
    "full_content": "string",       // Complete assembled message
    "metadata": {
      "provider_used": "string",
      "response_time_ms": number,
      "tokens_used": number,
      "cost": number,               // USD
      "ability_updated": {
        "subject": "string",
        "new_ability": number,      // 0.0-1.0
        "confidence": number        // 0.0-1.0
      }
    },
    "timestamp": "ISO8601"
  }
}
```

##### 7. Stream Error
```typescript
{
  "type": "stream_error",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "error": {
      "code": "string",             // ERROR_CODE constant
      "message": "string",          // User-friendly message
      "details": "string",          // Technical details (optional)
      "recoverable": boolean        // Can retry?
    },
    "partial_content": "string",    // Content generated before error
    "timestamp": "ISO8601"
  }
}
```

##### 8. Generation Stopped (Cancellation)
```typescript
{
  "type": "generation_stopped",
  "data": {
    "message_id": "uuid",
    "session_id": "uuid",
    "ai_message_id": "uuid",
    "reason": "user_cancelled" | "timeout" | "error",
    "partial_content": "string",    // Content generated before stop
    "metadata": {
      "tokens_used": number,
      "cost": number,
      "stopped_at_ms": number       // Time when stopped
    },
    "timestamp": "ISO8601"
  }
}
```

---

### Error Codes

```python
# File: core/models.py (Add these constants)

class StreamErrorCode(str, Enum):
    """WebSocket streaming error codes"""
    
    # Client Errors (4xx)
    INVALID_MESSAGE_FORMAT = "INVALID_MESSAGE_FORMAT"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"
    
    # Server Errors (5xx)
    AI_PROVIDER_UNAVAILABLE = "AI_PROVIDER_UNAVAILABLE"
    CONTEXT_RETRIEVAL_FAILED = "CONTEXT_RETRIEVAL_FAILED"
    EMOTION_DETECTION_FAILED = "EMOTION_DETECTION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Generation Errors
    GENERATION_TIMEOUT = "GENERATION_TIMEOUT"
    GENERATION_CANCELLED = "GENERATION_CANCELLED"
    TOKEN_LIMIT_EXCEEDED = "TOKEN_LIMIT_EXCEEDED"
```

---

## BACKEND IMPLEMENTATION BLUEPRINT

### File 1: `core/models.py` (Add Streaming Schemas)

```python
# Location: /app/backend/core/models.py
# Action: ADD to existing file

from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ============================================================================
# WEBSOCKET STREAMING MODELS
# ============================================================================

class ChatStreamRequest(BaseModel):
    """Client request to start chat streaming"""
    message_id: str = Field(..., description="Client-generated message ID")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")


class StopGenerationRequest(BaseModel):
    """Client request to stop ongoing generation"""
    message_id: str = Field(..., description="ID of message to cancel")
    session_id: str = Field(..., description="Session identifier")


class ThinkingStep(BaseModel):
    """Reasoning step in thinking phase"""
    step_number: int
    thinking_mode: Literal["analytical", "creative", "metacognitive"]
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StreamChunk(BaseModel):
    """Base class for streaming chunks"""
    message_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThinkingChunk(StreamChunk):
    """Thinking phase chunk"""
    type: Literal["thinking_chunk"] = "thinking_chunk"
    reasoning_step: ThinkingStep


class ContentChunk(StreamChunk):
    """Content phase chunk"""
    type: Literal["content_chunk"] = "content_chunk"
    content: str
    chunk_index: int
    is_code: bool = False


class StreamStartEvent(StreamChunk):
    """Stream start notification"""
    type: Literal["stream_start"] = "stream_start"
    ai_message_id: str
    metadata: Dict[str, Any]


class StreamCompleteEvent(StreamChunk):
    """Stream completion notification"""
    type: Literal["stream_complete"] = "stream_complete"
    ai_message_id: str
    full_content: str
    metadata: Dict[str, Any]


class StreamErrorEvent(StreamChunk):
    """Stream error notification"""
    type: Literal["stream_error"] = "stream_error"
    error: Dict[str, Any]
    partial_content: str = ""


class GenerationStoppedEvent(StreamChunk):
    """Generation stopped notification"""
    type: Literal["generation_stopped"] = "generation_stopped"
    ai_message_id: str
    reason: Literal["user_cancelled", "timeout", "error"]
    partial_content: str
    metadata: Dict[str, Any]
```

---

### File 2: `core/engine.py` (Refactor for Streaming)

```python
# Location: /app/backend/core/engine.py
# Action: ADD new method (keep existing process_request for backward compatibility)

import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from fastapi import WebSocket

async def process_request_stream(
    self,
    websocket: WebSocket,
    user_id: str,
    message: str,
    session_id: str,
    message_id: str,  # NEW: Client-provided message ID
    context: Optional[dict] = None,
    subject: str = "general"
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process user request with STREAMING support
    
    Yields WebSocket events as processing occurs:
    1. stream_start - Processing begins
    2. emotion_update - Emotion detected
    3. context_info - Context retrieved
    4. thinking_chunk - Reasoning steps (if enabled)
    5. content_chunk - Response content (token by token)
    6. stream_complete - Processing complete
    7. stream_error - If error occurs
    
    Args:
        websocket: WebSocket connection for sending events
        user_id: User identifier
        message: User message
        session_id: Session identifier
        message_id: Client-provided message ID for tracking
        context: Additional context (optional)
        subject: Learning subject/topic
        
    Yields:
        Dict[str, Any]: WebSocket event objects
    """
    
    import time
    import uuid
    from datetime import datetime
    
    start_time = time.time()
    ai_message_id = str(uuid.uuid4())
    
    # Track for cancellation
    self._active_streams[message_id] = {
        "session_id": session_id,
        "user_id": user_id,
        "ai_message_id": ai_message_id,
        "cancelled": False,
        "start_time": start_time
    }
    
    try:
        # Ensure intelligence layer is initialized
        if not self._db_initialized:
            logger.error("Intelligence layer not initialized")
            yield {
                "type": "stream_error",
                "data": {
                    "message_id": message_id,
                    "session_id": session_id,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "System not initialized",
                        "recoverable": False
                    },
                    "partial_content": "",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            return
        
        # ====================================================================
        # STREAM START
        # ====================================================================
        
        # Detect category first (fast, synchronous)
        category = self.provider_manager.detect_category_from_message(message, None)
        provider_name = self.provider_manager.select_best_model(category)
        
        yield {
            "type": "stream_start",
            "data": {
                "message_id": message_id,
                "session_id": session_id,
                "ai_message_id": ai_message_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "provider": provider_name,
                    "category": category
                }
            }
        }
        
        # Check for cancellation
        if self._check_cancelled(message_id):
            yield self._generate_stopped_event(message_id, session_id, ai_message_id, "")
            return
        
        # ====================================================================
        # STEP 1: CONTEXT RETRIEVAL (Non-blocking)
        # ====================================================================
        
        logger.info(f"🧠 Retrieving context for session {session_id}...")
        
        conversation_context = await self.context_manager.get_context(
            session_id=session_id,
            include_semantic=True,
            semantic_query=message
        )
        
        recent_messages = conversation_context.get('recent_messages', [])
        relevant_messages = conversation_context.get('relevant_messages', [])
        
        # Send context info
        yield {
            "type": "context_info",
            "data": {
                "message_id": message_id,
                "session_id": session_id,
                "context": {
                    "recent_messages_used": len(recent_messages),
                    "relevant_messages_used": len(relevant_messages),
                    "semantic_search_enabled": True,
                    "rag_enabled": False  # Will update if RAG runs
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Check cancellation
        if self._check_cancelled(message_id):
            yield self._generate_stopped_event(message_id, session_id, ai_message_id, "")
            return
        
        # ====================================================================
        # STEP 2: EMOTION ANALYSIS (Non-blocking)
        # ====================================================================
        
        logger.info(f"📊 Analyzing emotion...")
        
        try:
            emotion_result = await self.emotion_engine.analyze_emotion(
                text=message,
                user_id=user_id,
                session_id=session_id,
                interaction_context=context
            )
            
            # Map to API model
            from core.models import LearningReadiness, EmotionState
            readiness_map = {
                "optimal": LearningReadiness.OPTIMAL_READINESS,
                "good": LearningReadiness.HIGH_READINESS,
                "moderate": LearningReadiness.MODERATE_READINESS,
                "low": LearningReadiness.LOW_READINESS,
                "blocked": LearningReadiness.NOT_READY
            }
            
            emotion_state = EmotionState(
                primary_emotion=emotion_result.primary_emotion,
                arousal=emotion_result.pad_dimensions.arousal,
                valence=emotion_result.pad_dimensions.pleasure,
                learning_readiness=readiness_map.get(
                    emotion_result.learning_readiness,
                    LearningReadiness.MODERATE_READINESS
                )
            )
            
            # Send emotion update
            yield {
                "type": "emotion_update",
                "data": {
                    "message_id": message_id,
                    "session_id": session_id,
                    "emotion": emotion_state.model_dump(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"Emotion detection failed: {e}, using neutral")
            emotion_state = None
        
        # Check cancellation
        if self._check_cancelled(message_id):
            yield self._generate_stopped_event(message_id, session_id, ai_message_id, "")
            return
        
        # ====================================================================
        # STEP 3: ADAPTIVE DIFFICULTY (Fast)
        # ====================================================================
        
        ability = await self.adaptive_engine.ability_estimator.get_ability(
            user_id=user_id,
            subject=subject
        )
        
        difficulty_level = await self.adaptive_engine.recommend_difficulty(
            user_id=user_id,
            subject=subject,
            emotion_state=emotion_state,
            recent_performance=None
        )
        
        # ====================================================================
        # STEP 4: BUILD PROMPT
        # ====================================================================
        
        prompt = self._build_enhanced_prompt(
            message=message,
            recent_messages=recent_messages,
            relevant_messages=relevant_messages,
            emotion_state=emotion_state,
            difficulty_level=difficulty_level,
            rag_context=None,  # Simplified for streaming
            ability=ability
        )
        
        # ====================================================================
        # STEP 5: STREAM AI GENERATION
        # ====================================================================
        
        logger.info(f"🤖 Streaming generation from {provider_name}...")
        
        full_content = ""
        chunk_index = 0
        
        try:
            # Get streaming generator from provider
            async for chunk_text in self.provider_manager.generate_stream(
                provider_name=provider_name,
                prompt=prompt,
                category=category
            ):
                # Check cancellation before each chunk
                if self._check_cancelled(message_id):
                    yield self._generate_stopped_event(
                        message_id, session_id, ai_message_id, full_content
                    )
                    return
                
                # Accumulate content
                full_content += chunk_text
                
                # Send content chunk
                yield {
                    "type": "content_chunk",
                    "data": {
                        "message_id": message_id,
                        "session_id": session_id,
                        "content": chunk_text,
                        "chunk_index": chunk_index,
                        "is_code": False,  # TODO: Detect code blocks
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                
                chunk_index += 1
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            yield {
                "type": "stream_error",
                "data": {
                    "message_id": message_id,
                    "session_id": session_id,
                    "error": {
                        "code": "AI_PROVIDER_UNAVAILABLE",
                        "message": f"AI generation failed: {str(e)}",
                        "recoverable": True
                    },
                    "partial_content": full_content,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            return
        
        # ====================================================================
        # STEP 6: STREAM COMPLETE
        # ====================================================================
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Estimate cost and tokens (simplified)
        estimated_tokens = len(full_content.split()) * 1.3
        estimated_cost = self.provider_manager.estimate_cost(
            provider_name, estimated_tokens
        )
        
        yield {
            "type": "stream_complete",
            "data": {
                "message_id": message_id,
                "session_id": session_id,
                "ai_message_id": ai_message_id,
                "full_content": full_content,
                "metadata": {
                    "provider_used": provider_name,
                    "response_time_ms": response_time_ms,
                    "tokens_used": int(estimated_tokens),
                    "cost": estimated_cost,
                    "ability_updated": {
                        "subject": subject,
                        "new_ability": ability,
                        "confidence": 0.8
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"✅ Stream complete: {len(full_content)} chars, {response_time_ms:.0f}ms")
        
    except Exception as e:
        logger.error(f"Streaming failed: {e}", exc_info=True)
        yield {
            "type": "stream_error",
            "data": {
                "message_id": message_id,
                "session_id": session_id,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error during streaming",
                    "recoverable": False
                },
                "partial_content": "",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    
    finally:
        # Clean up tracking
        self._active_streams.pop(message_id, None)


def _check_cancelled(self, message_id: str) -> bool:
    """Check if generation was cancelled"""
    stream_info = self._active_streams.get(message_id)
    return stream_info and stream_info.get("cancelled", False)


def cancel_generation(self, message_id: str):
    """Cancel an ongoing generation"""
    if message_id in self._active_streams:
        self._active_streams[message_id]["cancelled"] = True
        logger.info(f"🛑 Cancelled generation: {message_id}")


def _generate_stopped_event(
    self, 
    message_id: str, 
    session_id: str, 
    ai_message_id: str, 
    partial_content: str
) -> Dict[str, Any]:
    """Generate stopped event"""
    stream_info = self._active_streams.get(message_id, {})
    elapsed_ms = (time.time() - stream_info.get("start_time", time.time())) * 1000
    
    return {
        "type": "generation_stopped",
        "data": {
            "message_id": message_id,
            "session_id": session_id,
            "ai_message_id": ai_message_id,
            "reason": "user_cancelled",
            "partial_content": partial_content,
            "metadata": {
                "tokens_used": len(partial_content.split()),
                "cost": 0.0,  # TODO: Calculate partial cost
                "stopped_at_ms": elapsed_ms
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    }


# Add to __init__
def __init__(self, model_max_tokens: int = 4096):
    # ... existing code ...
    
    # NEW: Track active streaming sessions
    self._active_streams: Dict[str, Dict[str, Any]] = {}
```

---

### File 3: `core/ai_providers.py` (Add Streaming Support)

```python
# Location: /app/backend/core/ai_providers.py
# Action: ADD new method to ProviderManager class

from typing import AsyncGenerator

async def generate_stream(
    self,
    provider_name: str,
    prompt: str,
    category: str,
    temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """
    Generate AI response with STREAMING support
    
    Yields tokens as they are generated by the AI provider.
    
    Args:
        provider_name: Name of provider to use
        prompt: Full prompt text
        category: Task category
        temperature: Generation temperature
        
    Yields:
        str: Token or chunk of generated text
    """
    
    try:
        provider_config = self.providers.get(provider_name)
        if not provider_config:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        # Get streaming client based on provider
        if provider_name == "gemini":
            async for chunk in self._stream_gemini(prompt, temperature):
                yield chunk
        
        elif provider_name == "groq":
            async for chunk in self._stream_groq(prompt, temperature):
                yield chunk
        
        else:
            # Fallback for providers without streaming: chunk the response
            full_response = await self.generate(
                provider_name=provider_name,
                prompt=prompt,
                category=category,
                temperature=temperature
            )
            
            # Simulate streaming by chunking
            words = full_response.split()
            for i in range(0, len(words), 3):  # 3 words per chunk
                chunk = " ".join(words[i:i+3]) + " "
                yield chunk
                await asyncio.sleep(0.05)  # 50ms delay for UX
    
    except Exception as e:
        logger.error(f"Streaming generation failed: {e}")
        raise


async def _stream_gemini(
    self,
    prompt: str,
    temperature: float
) -> AsyncGenerator[str, None]:
    """Stream from Gemini"""
    import google.generativeai as genai
    
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name)
    
    response = await model.generate_content_async(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
        ),
        stream=True
    )
    
    async for chunk in response:
        if chunk.text:
            yield chunk.text


async def _stream_groq(
    self,
    prompt: str,
    temperature: float
) -> AsyncGenerator[str, None]:
    """Stream from Groq"""
    from groq import AsyncGroq
    
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    
    stream = await client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

---

### File 4: `services/websocket_service.py` (Add Streaming Handlers)

```python
# Location: /app/backend/services/websocket_service.py
# Action: MODIFY handle_websocket_message function (around line 936)

async def handle_websocket_message(user_id: str, data: Dict[str, Any]):
    """
    Handle incoming WebSocket message based on type
    
    Enhanced with STREAMING CHAT support
    """
    message_type = data.get('type')
    message_data = data.get('data', {})
    
    # Rate limiting check
    if not manager.rate_limiter.check_rate_limit(user_id, message_type):
        logger.warning(f"Rate limit exceeded for user {user_id}")
        await manager.send_personal_message(user_id, {
            'type': 'error',
            'data': {
                'message': 'Rate limit exceeded. Please slow down.',
                'code': 'RATE_LIMIT_EXCEEDED'
            }
        }, priority=MessagePriority.HIGH)
        return
    
    # =========================================================================
    # NEW: CHAT STREAMING HANDLER
    # =========================================================================
    if message_type == 'chat_stream':
        # Import engine
        from utils.database import get_database
        from core.engine import MasterXEngine
        
        engine = MasterXEngine()
        db = get_database()
        await engine.initialize_intelligence_layer(db)
        
        # Extract request data
        message_id = message_data.get('message_id')
        session_id = message_data.get('session_id')
        message = message_data.get('message')
        context = message_data.get('context', {})
        subject = context.get('subject', 'general')
        
        # Validate
        if not all([message_id, session_id, message]):
            await manager.send_personal_message(user_id, {
                'type': 'stream_error',
                'data': {
                    'message_id': message_id or 'unknown',
                    'session_id': session_id or 'unknown',
                    'error': {
                        'code': 'INVALID_MESSAGE_FORMAT',
                        'message': 'Missing required fields: message_id, session_id, or message',
                        'recoverable': False
                    },
                    'partial_content': '',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }, priority=MessagePriority.CRITICAL)
            return
        
        # Get WebSocket connection for this user
        connections = manager.active_connections.get(user_id, {})
        if not connections:
            logger.error(f"No active WebSocket for user {user_id}")
            return
        
        # Get first connection (or iterate all)
        websocket = list(connections.values())[0]
        
        # Stream response
        try:
            async for event in engine.process_request_stream(
                websocket=websocket,
                user_id=user_id,
                message=message,
                session_id=session_id,
                message_id=message_id,
                context=context,
                subject=subject
            ):
                # Send event to client
                await manager.send_personal_message(
                    user_id=user_id,
                    message=event,
                    priority=MessagePriority.CRITICAL  # High priority for streaming
                )
        
        except Exception as e:
            logger.error(f"Chat streaming failed: {e}", exc_info=True)
            await manager.send_personal_message(user_id, {
                'type': 'stream_error',
                'data': {
                    'message_id': message_id,
                    'session_id': session_id,
                    'error': {
                        'code': 'INTERNAL_ERROR',
                        'message': 'Chat streaming failed',
                        'recoverable': False
                    },
                    'partial_content': '',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }, priority=MessagePriority.CRITICAL)
        
        return
    
    # =========================================================================
    # NEW: STOP GENERATION HANDLER
    # =========================================================================
    elif message_type == 'stop_generation':
        message_id = message_data.get('message_id')
        session_id = message_data.get('session_id')
        
        if not message_id:
            logger.warning("stop_generation missing message_id")
            return
        
        # Get engine and cancel
        from utils.database import get_database
        from core.engine import MasterXEngine
        
        engine = MasterXEngine()
        engine.cancel_generation(message_id)
        
        logger.info(f"✅ Cancelled generation for message {message_id}")
        return
    
    # ... existing handlers (join_session, leave_session, etc.) ...
```

---

### File 5: `server.py` (No Changes Required!)

**Finding:** The existing WebSocket endpoint at `server.py:3049` already handles message routing through `handle_websocket_message()`. No changes needed!

---

## FRONTEND IMPLEMENTATION BLUEPRINT

### File 1: `types/chat.types.ts` (Add Streaming Types)

```typescript
// Location: /app/frontend/src/types/chat.types.ts
// Action: ADD to existing file

/**
 * WebSocket Streaming Event Types
 */

export type StreamEventType =
  | 'stream_start'
  | 'thinking_chunk'
  | 'content_chunk'
  | 'emotion_update'
  | 'context_info'
  | 'stream_complete'
  | 'stream_error'
  | 'generation_stopped';

export interface BaseStreamEvent {
  type: StreamEventType;
  data: {
    message_id: string;
    session_id: string;
    timestamp: string;
  };
}

export interface StreamStartEvent extends BaseStreamEvent {
  type: 'stream_start';
  data: BaseStreamEvent['data'] & {
    ai_message_id: string;
    metadata: {
      provider: string;
      category: string;
      estimated_tokens?: number;
    };
  };
}

export interface ThinkingChunkEvent extends BaseStreamEvent {
  type: 'thinking_chunk';
  data: BaseStreamEvent['data'] & {
    reasoning_step: {
      step_number: number;
      thinking_mode: 'analytical' | 'creative' | 'metacognitive';
      description: string;
      confidence: number;
      timestamp: string;
    };
  };
}

export interface ContentChunkEvent extends BaseStreamEvent {
  type: 'content_chunk';
  data: BaseStreamEvent['data'] & {
    content: string;
    chunk_index: number;
    is_code: boolean;
  };
}

export interface EmotionUpdateEvent extends BaseStreamEvent {
  type: 'emotion_update';
  data: BaseStreamEvent['data'] & {
    emotion: {
      primary_emotion: string;
      arousal: number;
      valence: number;
      learning_readiness: string;
    };
  };
}

export interface ContextInfoEvent extends BaseStreamEvent {
  type: 'context_info';
  data: BaseStreamEvent['data'] & {
    context: {
      recent_messages_used: number;
      relevant_messages_used: number;
      semantic_search_enabled: boolean;
      rag_enabled: boolean;
      rag_sources?: number;
    };
  };
}

export interface StreamCompleteEvent extends BaseStreamEvent {
  type: 'stream_complete';
  data: BaseStreamEvent['data'] & {
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
  };
}

export interface StreamErrorEvent extends BaseStreamEvent {
  type: 'stream_error';
  data: BaseStreamEvent['data'] & {
    error: {
      code: string;
      message: string;
      details?: string;
      recoverable: boolean;
    };
    partial_content: string;
  };
}

export interface GenerationStoppedEvent extends BaseStreamEvent {
  type: 'generation_stopped';
  data: BaseStreamEvent['data'] & {
    ai_message_id: string;
    reason: 'user_cancelled' | 'timeout' | 'error';
    partial_content: string;
    metadata: {
      tokens_used: number;
      cost: number;
      stopped_at_ms: number;
    };
  };
}

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
 * Streaming state for UI
 */
export interface StreamingState {
  isStreaming: boolean;
  currentMessageId: string | null;
  aiMessageId: string | null;
  accumulatedContent: string;
  thinkingSteps: ThinkingStep[];
  currentEmotion: EmotionState | null;
  error: StreamError | null;
}

export interface ThinkingStep {
  step_number: number;
  thinking_mode: string;
  description: string;
  confidence: number;
  timestamp: string;
}

export interface StreamError {
  code: string;
  message: string;
  recoverable: boolean;
}
```

---

### File 2: `services/api/chat.api.ts` (Add Streaming Function)

```typescript
// Location: /app/frontend/src/services/api/chat.api.ts
// Action: ADD to existing chatAPI object

import { v4 as uuidv4 } from 'uuid';
import nativeSocketClient from '../websocket/native-socket.client';

/**
 * Send a streaming chat message via WebSocket
 * 
 * This triggers real-time streaming response with:
 * - Thinking phase (reasoning steps)
 * - Content phase (token-by-token response)
 * - Emotion updates
 * - Cancellation support
 * 
 * @param request - Chat request (same as sendMessage)
 * @param onEvent - Callback for each streaming event
 * @returns Cancellation function
 * 
 * @example
 * ```typescript
 * const cancel = chatAPI.streamMessage(
 *   {
 *     user_id: 'user-123',
 *     message: 'Explain quantum computing',
 *     session_id: 'session-abc'
 *   },
 *   (event) => {
 *     if (event.type === 'content_chunk') {
 *       console.log('Chunk:', event.data.content);
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
  
  // Build WebSocket message
  const wsMessage = {
    type: 'chat_stream',
    data: {
      message_id: messageId,
      session_id: request.session_id || uuidv4(), // Generate if not provided
      user_id: request.user_id,
      message: request.message,
      context: request.context || {}
    }
  };
  
  // Subscribe to ALL streaming events for this message
  const eventTypes: StreamEventType[] = [
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
  
  eventTypes.forEach(eventType => {
    const unsubscribe = nativeSocketClient.on(eventType, (data: any) => {
      // Filter by message_id
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
  nativeSocketClient.send('chat_stream', wsMessage.data);
  
  // Return cancellation function
  return () => {
    // Unsubscribe from all events
    unsubscribers.forEach(unsub => unsub());
    
    // Send stop_generation message
    nativeSocketClient.send('stop_generation', {
      message_id: messageId,
      session_id: wsMessage.data.session_id
    });
  };
},
```

---

### File 3: `components/chat/ChatContainer.tsx` (Add Streaming State Machine)

```typescript
// Location: /app/frontend/src/components/chat/ChatContainer.tsx
// Action: MODIFY existing component (around line 24-200)

import { useState, useCallback, useRef } from 'react';
import { chatAPI } from '@/services/api/chat.api';
import type { StreamEvent, StreamingState } from '@/types/chat.types';

/**
 * ChatContainer with Streaming Support
 */
export const ChatContainer: React.FC<ChatContainerProps> = ({
  sessionId,
  initialTopic,
  showEmotion = true,
  enableVoice = false,
  enableReasoning = false,
  className
}) => {
  // ... existing state ...
  
  // NEW: Streaming state
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    currentMessageId: null,
    aiMessageId: null,
    accumulatedContent: '',
    thinkingSteps: [],
    currentEmotion: null,
    error: null
  });
  
  // NEW: Cancellation function ref
  const cancelStreamRef = useRef<(() => void) | null>(null);
  
  /**
   * Handle streaming message send
   */
  const handleStreamMessage = useCallback((messageText: string) => {
    // Clear previous state
    setStreamingState({
      isStreaming: true,
      currentMessageId: null,
      aiMessageId: null,
      accumulatedContent: '',
      thinkingSteps: [],
      currentEmotion: null,
      error: null
    });
    
    // Add user message to UI immediately (optimistic)
    const userMessage = {
      id: uuidv4(),
      role: 'user' as const,
      content: messageText,
      timestamp: new Date().toISOString()
    };
    
    addMessage(userMessage);
    
    // Start streaming
    const cancel = chatAPI.streamMessage(
      {
        user_id: user?.id || 'anonymous',
        message: messageText,
        session_id: currentSessionId,
        context: {
          subject: currentTopic || 'general',
          enable_reasoning: enableReasoning
        }
      },
      (event: StreamEvent) => {
        handleStreamEvent(event);
      }
    );
    
    // Store cancel function
    cancelStreamRef.current = cancel;
    
  }, [user, currentSessionId, currentTopic, enableReasoning]);
  
  /**
   * Handle streaming events
   */
  const handleStreamEvent = useCallback((event: StreamEvent) => {
    
    switch (event.type) {
      case 'stream_start':
        setStreamingState(prev => ({
          ...prev,
          currentMessageId: event.data.message_id,
          aiMessageId: event.data.ai_message_id
        }));
        break;
      
      case 'thinking_chunk':
        if (enableReasoning) {
          setStreamingState(prev => ({
            ...prev,
            thinkingSteps: [...prev.thinkingSteps, event.data.reasoning_step]
          }));
        }
        break;
      
      case 'content_chunk':
        setStreamingState(prev => ({
          ...prev,
          accumulatedContent: prev.accumulatedContent + event.data.content
        }));
        
        // Update UI with accumulated content (real-time)
        updateStreamingMessage(event.data.content);
        break;
      
      case 'emotion_update':
        if (showEmotion) {
          setStreamingState(prev => ({
            ...prev,
            currentEmotion: event.data.emotion
          }));
          
          // Update emotion store
          setEmotion(event.data.emotion);
        }
        break;
      
      case 'context_info':
        // Optional: Log or display context info
        console.log('Context:', event.data.context);
        break;
      
      case 'stream_complete':
        // Finalize message
        finalizeStreamingMessage({
          id: event.data.ai_message_id,
          role: 'assistant',
          content: event.data.full_content,
          timestamp: event.data.timestamp,
          emotion_state: streamingState.currentEmotion,
          provider_used: event.data.metadata.provider_used,
          response_time_ms: event.data.metadata.response_time_ms,
          reasoning_chain: enableReasoning ? streamingState.thinkingSteps : undefined
        });
        
        // Reset streaming state
        setStreamingState({
          isStreaming: false,
          currentMessageId: null,
          aiMessageId: null,
          accumulatedContent: '',
          thinkingSteps: [],
          currentEmotion: null,
          error: null
        });
        
        cancelStreamRef.current = null;
        break;
      
      case 'stream_error':
        // Show error
        setStreamingState(prev => ({
          ...prev,
          isStreaming: false,
          error: event.data.error
        }));
        
        toast.error(event.data.error.message);
        
        // If partial content exists, show it
        if (event.data.partial_content) {
          finalizeStreamingMessage({
            id: uuidv4(),
            role: 'assistant',
            content: event.data.partial_content + '\n\n[Error: Generation incomplete]',
            timestamp: event.data.timestamp,
            emotion_state: streamingState.currentEmotion
          });
        }
        
        cancelStreamRef.current = null;
        break;
      
      case 'generation_stopped':
        // User cancelled
        finalizeStreamingMessage({
          id: event.data.ai_message_id,
          role: 'assistant',
          content: event.data.partial_content + '\n\n[Generation stopped by user]',
          timestamp: event.data.timestamp,
          emotion_state: streamingState.currentEmotion
        });
        
        setStreamingState({
          isStreaming: false,
          currentMessageId: null,
          aiMessageId: null,
          accumulatedContent: '',
          thinkingSteps: [],
          currentEmotion: null,
          error: null
        });
        
        cancelStreamRef.current = null;
        break;
    }
  }, [enableReasoning, showEmotion, streamingState]);
  
  /**
   * Handle stop button click
   */
  const handleStopGeneration = useCallback(() => {
    if (cancelStreamRef.current) {
      cancelStreamRef.current();
      toast.info('Stopping generation...');
    }
  }, []);
  
  // ... rest of component ...
  
  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Messages */}
      <MessageList
        messages={messages}
        streamingContent={streamingState.accumulatedContent}
        isStreaming={streamingState.isStreaming}
        thinkingSteps={streamingState.thinkingSteps}
      />
      
      {/* Input */}
      <MessageInput
        onSend={handleStreamMessage}
        disabled={streamingState.isStreaming}
        showStopButton={streamingState.isStreaming}
        onStop={handleStopGeneration}
      />
    </div>
  );
};
```

---

### File 4: `components/chat/MessageInput.tsx` (Add Stop Button)

```typescript
// Location: /app/frontend/src/components/chat/MessageInput.tsx
// Action: ADD stop button support

import { StopCircle } from 'lucide-react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  showStopButton?: boolean;  // NEW
  onStop?: () => void;       // NEW
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  disabled = false,
  showStopButton = false,
  onStop,
  placeholder = 'Type your message...'
}) => {
  // ... existing state ...
  
  return (
    <div className="relative">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        className="..."
      />
      
      {/* Send/Stop Button */}
      {showStopButton ? (
        <button
          onClick={onStop}
          className="absolute bottom-4 right-4 p-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
          aria-label="Stop generation"
        >
          <StopCircle className="w-5 h-5 text-white" />
        </button>
      ) : (
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="absolute bottom-4 right-4 p-3 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50 transition-colors"
          aria-label="Send message"
        >
          <Send className="w-5 h-5 text-white" />
        </button>
      )}
    </div>
  );
};
```

---

## INTEGRATION CHECKLIST

### Phase 1: Backend Core (Week 1)

- [ ] **1.1** Add streaming schemas to `core/models.py`
  - [ ] StreamChunk base class
  - [ ] Event classes (StreamStartEvent, ContentChunk, etc.)
  - [ ] StreamErrorCode enum
  
- [ ] **1.2** Add streaming to `core/engine.py`
  - [ ] Implement `process_request_stream()` method
  - [ ] Add `_active_streams` tracking dict
  - [ ] Implement `cancel_generation()` method
  - [ ] Add `_check_cancelled()` helper
  
- [ ] **1.3** Add provider streaming to `core/ai_providers.py`
  - [ ] Implement `generate_stream()` method
  - [ ] Add `_stream_gemini()` for Gemini
  - [ ] Add `_stream_groq()` for Groq
  - [ ] Add fallback chunking for non-streaming providers
  
- [ ] **1.4** Update WebSocket service `services/websocket_service.py`
  - [ ] Add `chat_stream` handler in `handle_websocket_message()`
  - [ ] Add `stop_generation` handler
  - [ ] Test message routing

### Phase 2: Frontend Core (Week 2)

- [ ] **2.1** Add streaming types to `types/chat.types.ts`
  - [ ] StreamEvent union type
  - [ ] Individual event interfaces
  - [ ] StreamingState interface
  
- [ ] **2.2** Add streaming API to `services/api/chat.api.ts`
  - [ ] Implement `streamMessage()` function
  - [ ] Add event subscription logic
  - [ ] Add cancellation function
  
- [ ] **2.3** Update `ChatContainer.tsx`
  - [ ] Add `streamingState` state
  - [ ] Implement `handleStreamEvent()` callback
  - [ ] Add `handleStopGeneration()` function
  - [ ] Wire up streaming UI
  
- [ ] **2.4** Update `MessageInput.tsx`
  - [ ] Add stop button UI
  - [ ] Add `showStopButton` prop
  - [ ] Add `onStop` handler

### Phase 3: Testing & Refinement (Week 3)

- [ ] **3.1** Backend unit tests
  - [ ] Test `process_request_stream()` generator
  - [ ] Test cancellation logic
  - [ ] Test error handling
  
- [ ] **3.2** Frontend unit tests
  - [ ] Test streaming state machine
  - [ ] Test event handling
  - [ ] Test cancellation
  
- [ ] **3.3** Integration tests
  - [ ] End-to-end streaming flow
  - [ ] Cancellation mid-stream
  - [ ] Error recovery
  - [ ] WebSocket reconnection during stream
  
- [ ] **3.4** Performance testing
  - [ ] Measure latency (first token time)
  - [ ] Test concurrent streams
  - [ ] Test long-running streams (>5 min)

### Phase 4: Production Hardening (Week 4)

- [ ] **4.1** Add monitoring
  - [ ] Log streaming metrics
  - [ ] Track cancellation rates
  - [ ] Monitor WebSocket health during streams
  
- [ ] **4.2** Add graceful degradation
  - [ ] Fallback to HTTP if WebSocket unavailable
  - [ ] Auto-retry on stream errors
  - [ ] Handle network interruptions
  
- [ ] **4.3** Documentation
  - [ ] Update API docs with streaming endpoints
  - [ ] Add code examples
  - [ ] Update frontend README

---

## TESTING STRATEGY

### Backend Tests

```python
# File: /app/backend/tests/test_streaming_chat.py

import pytest
import asyncio
from core.engine import MasterXEngine

@pytest.mark.asyncio
async def test_process_request_stream_basic():
    """Test basic streaming flow"""
    engine = MasterXEngine()
    
    events = []
    async for event in engine.process_request_stream(
        websocket=mock_websocket,
        user_id="test-user",
        message="What is Python?",
        session_id="test-session",
        message_id="test-msg-123"
    ):
        events.append(event)
    
    # Verify event sequence
    assert events[0]['type'] == 'stream_start'
    assert any(e['type'] == 'emotion_update' for e in events)
    assert any(e['type'] == 'content_chunk' for e in events)
    assert events[-1]['type'] == 'stream_complete'


@pytest.mark.asyncio
async def test_stream_cancellation():
    """Test cancellation mid-stream"""
    engine = MasterXEngine()
    
    # Start stream
    stream_task = asyncio.create_task(
        collect_stream_events(engine, "test-msg-456")
    )
    
    # Cancel after 1 second
    await asyncio.sleep(1)
    engine.cancel_generation("test-msg-456")
    
    events = await stream_task
    
    # Should have stopped event
    assert any(e['type'] == 'generation_stopped' for e in events)
    assert events[-1]['data']['reason'] == 'user_cancelled'
```

### Frontend Tests

```typescript
// File: /app/frontend/src/components/chat/__tests__/ChatContainer.streaming.test.tsx

import { render, fireEvent, waitFor } from '@testing-library/react';
import { ChatContainer } from '../ChatContainer';
import { chatAPI } from '@/services/api/chat.api';

describe('ChatContainer - Streaming', () => {
  
  it('should stream message content in real-time', async () => {
    const { getByPlaceholderText, getByText } = render(
      <ChatContainer sessionId="test-session" />
    );
    
    // Mock streaming
    const mockCancel = jest.fn();
    jest.spyOn(chatAPI, 'streamMessage').mockImplementation((req, onEvent) => {
      // Simulate events
      setTimeout(() => onEvent({
        type: 'stream_start',
        data: { message_id: '123', session_id: 'test', ai_message_id: '456', timestamp: new Date().toISOString(), metadata: {} }
      }), 100);
      
      setTimeout(() => onEvent({
        type: 'content_chunk',
        data: { message_id: '123', session_id: 'test', content: 'Hello', chunk_index: 0, timestamp: new Date().toISOString() }
      }), 200);
      
      setTimeout(() => onEvent({
        type: 'content_chunk',
        data: { message_id: '123', session_id: 'test', content: ' World', chunk_index: 1, timestamp: new Date().toISOString() }
      }), 300);
      
      return mockCancel;
    });
    
    // Send message
    const input = getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.submit(input.closest('form')!);
    
    // Should see partial content
    await waitFor(() => {
      expect(getByText(/Hello/)).toBeInTheDocument();
    });
    
    // Should see full content
    await waitFor(() => {
      expect(getByText(/Hello World/)).toBeInTheDocument();
    });
  });
  
  it('should cancel stream when stop button clicked', async () => {
    const { getByLabelText } = render(
      <ChatContainer sessionId="test-session" />
    );
    
    const mockCancel = jest.fn();
    jest.spyOn(chatAPI, 'streamMessage').mockReturnValue(mockCancel);
    
    // Start stream (trigger via message send)
    // ...
    
    // Click stop
    const stopButton = getByLabelText('Stop generation');
    fireEvent.click(stopButton);
    
    expect(mockCancel).toHaveBeenCalled();
  });
});
```

---

## PERFORMANCE & SECURITY

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Token Latency | < 800ms | Time from send to first `content_chunk` |
| Token Throughput | > 20 tokens/sec | Average chunks per second |
| Cancellation Response | < 200ms | Time from cancel to `generation_stopped` |
| WebSocket Overhead | < 50ms | Latency vs HTTP baseline |
| Concurrent Streams | > 100 | Simultaneous active streams |

### Security Measures

1. **Authentication**: JWT token verified on WebSocket connect
2. **Rate Limiting**: Existing adaptive rate limiter applies
3. **Input Validation**: Pydantic schemas validate all events
4. **XSS Prevention**: Existing SecurityValidator checks content
5. **Cost Enforcement**: Track streaming costs same as HTTP
6. **Cancellation Auth**: Only message owner can cancel

### Monitoring Metrics

```python
# Add to utils/health_monitor.py

class StreamingMetrics:
    """Metrics for WebSocket streaming"""
    
    total_streams_started: int = 0
    total_streams_completed: int = 0
    total_streams_cancelled: int = 0
    total_streams_errored: int = 0
    
    avg_first_token_latency_ms: float = 0.0
    avg_token_throughput: float = 0.0
    avg_stream_duration_ms: float = 0.0
    
    active_streams: int = 0
```

---

## ROLLBACK PLAN

### Gradual Rollout Strategy

**Phase 1**: Feature Flag (Week 1-2)
```typescript
// Frontend feature flag
const ENABLE_STREAMING = import.meta.env.VITE_ENABLE_STREAMING === 'true';

if (ENABLE_STREAMING) {
  chatAPI.streamMessage(request, onEvent);
} else {
  // Fallback to HTTP
  chatAPI.sendMessage(request);
}
```

**Phase 2**: A/B Testing (Week 3)
- 10% users on streaming
- Monitor error rates
- Compare UX metrics

**Phase 3**: Full Rollout (Week 4)
- 100% users on streaming
- HTTP endpoint remains as fallback

### Rollback Triggers

Rollback to HTTP if:
1. Stream error rate > 5%
2. WebSocket disconnect rate > 10%
3. User complaints > threshold
4. Performance degradation detected

### Rollback Procedure

1. Set feature flag `VITE_ENABLE_STREAMING=false`
2. Deploy frontend update
3. No backend changes needed (HTTP endpoint unchanged)
4. Monitor for 24 hours

---

## APPENDIX: FUNCTION MODIFICATIONS SUMMARY

### Functions to Modify

| File | Function | Change Type | Reason |
|------|----------|-------------|--------|
| `core/engine.py` | `MasterXEngine.__init__()` | ADD | Add `_active_streams` tracking |
| `core/engine.py` | N/A | ADD | New `process_request_stream()` method |
| `core/engine.py` | N/A | ADD | New `cancel_generation()` method |
| `core/ai_providers.py` | `ProviderManager` | ADD | New `generate_stream()` method |
| `services/websocket_service.py` | `handle_websocket_message()` | MODIFY | Add `chat_stream` handler |
| `components/chat/ChatContainer.tsx` | Component | MODIFY | Add streaming state machine |
| `services/api/chat.api.ts` | `chatAPI` | ADD | New `streamMessage()` function |

### Functions to Keep Unchanged

| File | Function | Reason |
|------|----------|--------|
| `server.py` | `@app.websocket("/api/ws")` | Already handles routing ✓ |
| `server.py` | `@app.post("/api/v1/chat")` | Keep for fallback ✓ |
| `core/engine.py` | `process_request()` | Keep for HTTP endpoint ✓ |
| `services/websocket_service.py` | `ConnectionManager` | Already enterprise-grade ✓ |

---

## CONCLUSION

This guide provides a **complete architecture blueprint** for upgrading MasterX to bi-directional WebSocket streaming. The design:

✅ **Preserves existing infrastructure** - Builds on top of enterprise WebSocket service  
✅ **Maintains backward compatibility** - HTTP endpoint remains functional  
✅ **Follows AGENTS.md standards** - Modular, typed, production-ready  
✅ **Enables real-time UX** - Thinking phase + content streaming + cancellation  
✅ **Provides graceful degradation** - Fallback to HTTP if WebSocket fails  

**Next Steps:**
1. Review and approve this architecture document
2. Begin Phase 1 implementation (Backend Core)
3. Iterate based on testing feedback

---

**Document Status**: ✅ Ready for Implementation  
**Last Updated**: 2025-12-06  
**Version**: 1.0.0
