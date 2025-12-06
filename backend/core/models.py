"""
Database Models & Schemas for MasterX
Following specifications from 2.CRITICAL_INITIAL_SETUP.md Section 1

All models use UUID4 for IDs (NOT MongoDB ObjectId)
Full type hints, Pydantic V2 validation
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class LearningReadiness(str, Enum):
    OPTIMAL_READINESS = "optimal_readiness"
    HIGH_READINESS = "high_readiness"
    MODERATE_READINESS = "moderate_readiness"
    LOW_READINESS = "low_readiness"
    NOT_READY = "not_ready"


class ProviderStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# ============================================================================
# USER MODELS
# ============================================================================

class LearningPreferences(BaseModel):
    """User learning preferences"""
    preferred_subjects: List[str] = Field(default_factory=list)
    learning_style: LearningStyle = LearningStyle.VISUAL
    difficulty_preference: str = "adaptive"


class EmotionalProfile(BaseModel):
    """User emotional baseline profile"""
    baseline_engagement: float = Field(default=0.7, ge=0.0, le=1.0)
    frustration_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    celebration_responsiveness: float = Field(default=0.8, ge=0.0, le=1.0)


class UserProfile(BaseModel):
    """User profile model - matches MongoDB users collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: EmailStr
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    emotional_profile: EmotionalProfile = Field(default_factory=EmotionalProfile)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    total_sessions: int = 0
    last_active: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john@example.com",
                "name": "John Doe",
                "subscription_tier": "free"
            }
        }


class UserDocument(BaseModel):
    """
    User document with authentication - MongoDB users collection
    Extends UserProfile with authentication fields
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    email: EmailStr
    name: str
    password_hash: str  # bcrypt hash from security.py
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    
    # Profile fields
    learning_preferences: LearningPreferences = Field(default_factory=LearningPreferences)
    emotional_profile: EmotionalProfile = Field(default_factory=EmotionalProfile)
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    total_sessions: int = 0
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    # Security fields
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class LoginAttempt(BaseModel):
    """Login attempt tracking - MongoDB login_attempts collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: Optional[str] = None
    email: EmailStr
    ip_address: str
    user_agent: Optional[str] = None
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None
    
    class Config:
        populate_by_name = True


class RefreshToken(BaseModel):
    """Refresh token tracking - MongoDB refresh_tokens collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    token_hash: str  # SHA256 hash of the token
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


# ============================================================================
# SESSION MODELS
# ============================================================================

class LearningSession(BaseModel):
    """Learning session model - matches MongoDB sessions collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    current_topic: Optional[str] = None
    assigned_provider: Optional[str] = None
    total_messages: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time_ms: float = 0.0
    emotion_trajectory: List[str] = Field(default_factory=list)
    performance_score: float = 0.75
    status: SessionStatus = SessionStatus.ACTIVE

    class Config:
        populate_by_name = True


# ============================================================================
# MESSAGE MODELS
# ============================================================================

class EmotionState(BaseModel):
    """Emotion analysis state"""
    primary_emotion: str
    arousal: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=-1.0, le=1.0)  # Fixed: valence can be negative (PAD model)
    learning_readiness: LearningReadiness


class Message(BaseModel):
    """Message model - matches MongoDB messages collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    session_id: str
    user_id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emotion_state: Optional[EmotionState] = None
    provider_used: Optional[str] = None
    response_time_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    embedding: Optional[List[float]] = None
    quality_rating: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        populate_by_name = True


# ============================================================================
# BENCHMARK MODELS
# ============================================================================

class BenchmarkTestResult(BaseModel):
    """Individual benchmark test result"""
    test_id: str
    quality: float = Field(ge=0.0, le=100.0)
    time_ms: float
    passed: bool


class BenchmarkResult(BaseModel):
    """Provider benchmark results - matches MongoDB benchmark_results collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    category: str
    provider: str
    model_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    quality_score: float = Field(ge=0.0, le=100.0)
    speed_score: float = Field(ge=0.0, le=100.0)
    cost_score: float = Field(ge=0.0, le=100.0)
    final_score: float = Field(ge=0.0, le=100.0)
    avg_response_time_ms: float
    avg_cost: float
    tests_passed: int
    tests_total: int
    test_results: List[BenchmarkTestResult] = Field(default_factory=list)

    class Config:
        populate_by_name = True


# ============================================================================
# PROVIDER HEALTH MODELS
# ============================================================================

class ProviderHealth(BaseModel):
    """Provider health status - matches MongoDB provider_health collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ProviderStatus
    success_rate: float = Field(ge=0.0, le=1.0)
    avg_response_time_ms: float
    requests_last_hour: int
    errors_last_hour: int
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

    class Config:
        populate_by_name = True


# ============================================================================
# USER PERFORMANCE MODELS
# ============================================================================

class UserPerformance(BaseModel):
    """User learning performance - matches MongoDB user_performance collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    subject: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ability_level: float = Field(ge=0.0, le=1.0)
    difficulty_preference: float = Field(ge=0.0, le=1.0)
    learning_velocity: float
    mastery_topics: List[str] = Field(default_factory=list)
    struggling_topics: List[str] = Field(default_factory=list)
    total_practice_time_hours: float = 0.0
    improvement_rate: float = 0.0

    class Config:
        populate_by_name = True


# ============================================================================
# COST TRACKING MODELS
# ============================================================================

class CategoryBreakdown(BaseModel):
    """Cost breakdown by category"""
    coding: float = 0.0
    math: float = 0.0
    empathy: float = 0.0
    research: float = 0.0
    general: float = 0.0


class CostTracking(BaseModel):
    """API cost tracking - matches MongoDB cost_tracking collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    date: str  # YYYY-MM-DD format
    provider: str
    user_id: Optional[str] = None
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    category_breakdown: CategoryBreakdown = Field(default_factory=CategoryBreakdown)

    class Config:
        populate_by_name = True


# ============================================================================
# AI RESPONSE MODELS
# ============================================================================

# Define supporting models first
class ContextInfo(BaseModel):
    """Context retrieval information"""
    recent_messages_count: int = 0
    relevant_messages_count: int = 0
    has_context: bool = False
    retrieval_time_ms: Optional[float] = None


class AbilityInfo(BaseModel):
    """Adaptive learning ability information"""
    ability_level: float
    recommended_difficulty: float
    cognitive_load: float
    flow_state_score: Optional[float] = None


class SuggestedQuestion(BaseModel):
    """
    Perplexity-inspired suggested follow-up question
    
    Generated using ML-based context analysis to provide
    thought-provoking, contextually relevant questions.
    """
    question: str = Field(..., description="The follow-up question text")
    rationale: str = Field(..., description="Why this question is suggested (e.g., 'building_on_success', 'connecting_concepts')")
    difficulty_delta: float = Field(default=0.0, description="Change in difficulty (-1.0 to +1.0, where 0 = same level)")
    category: str = Field(default="exploration", description="Question type: 'exploration', 'application', 'challenge', 'clarification'")


class AIResponse(BaseModel):
    """AI provider response with comprehensive metadata"""
    content: str
    provider: str
    model_name: str
    tokens_used: int
    cost: float
    response_time_ms: float
    emotion_state: Optional[EmotionState] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata
    category: Optional[str] = None
    context_info: Optional[ContextInfo] = None
    ability_info: Optional[AbilityInfo] = None
    ability_updated: bool = False
    processing_breakdown: Optional[Dict[str, float]] = None
    
    # RAG metadata (Perplexity-inspired)
    rag_enabled: bool = False
    citations: Optional[List[str]] = None
    sources_count: Optional[int] = None
    search_provider: Optional[str] = None
    
    # Follow-up questions (Perplexity-inspired)
    suggested_questions: Optional[List[SuggestedQuestion]] = None
    
    # Deep Thinking / Reasoning metadata (Phase 4)
    reasoning_enabled: bool = False
    reasoning_chain: Optional[Dict[str, Any]] = None
    thinking_mode: Optional[str] = None


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat API request"""
    user_id: str
    session_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat API response with comprehensive metadata"""
    session_id: str
    message: str
    emotion_state: Optional[EmotionState] = None
    provider_used: str
    response_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Enhanced metadata (Phase 2-4)
    category_detected: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    
    # Phase 3 metadata
    context_retrieved: Optional[ContextInfo] = None
    ability_info: Optional[AbilityInfo] = None
    ability_updated: bool = False
    
    # Phase 4 metadata
    cached: bool = False
    processing_breakdown: Optional[Dict[str, float]] = None
    
    # RAG metadata (Perplexity-inspired)
    rag_enabled: bool = False
    citations: Optional[List[str]] = None
    sources_count: Optional[int] = None
    search_provider: Optional[str] = None
    
    # Follow-up questions (Perplexity-inspired)
    suggested_questions: Optional[List[SuggestedQuestion]] = None
    
    # Deep Thinking / Reasoning metadata (Phase 4)
    reasoning_enabled: bool = False
    reasoning_chain: Optional[Dict[str, Any]] = None
    thinking_mode: Optional[str] = None


class ReasoningRequest(BaseModel):
    """Request for reasoning-enabled chat with visible thinking"""
    user_id: str
    session_id: Optional[str] = None
    message: str
    enable_reasoning: bool = Field(default=True, description="Enable visible reasoning")
    thinking_mode: Optional[str] = Field(None, description="Force mode: system1, system2, hybrid, or auto")
    max_reasoning_depth: int = Field(default=5, ge=1, le=10, description="Maximum reasoning steps")
    context: Optional[Dict[str, Any]] = None


class ReasoningResponse(BaseModel):
    """Enhanced chat response with visible reasoning chain"""
    session_id: str
    message: str
    
    # Reasoning data
    reasoning_enabled: bool = Field(default=False)
    reasoning_chain: Optional[Dict[str, Any]] = None  # ReasoningChain.to_dict_for_frontend()
    thinking_mode: Optional[str] = None
    
    # Standard metadata
    emotion_state: Optional[EmotionState] = None
    provider_used: str
    response_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Token usage
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    
    # Context
    category_detected: Optional[str] = None
    context_retrieved: Optional[ContextInfo] = None
    ability_info: Optional[AbilityInfo] = None
    
    # Processing metadata
    cached: bool = False
    processing_breakdown: Optional[Dict[str, float]] = None
    
    # RAG metadata
    rag_enabled: bool = False
    citations: Optional[List[str]] = None
    sources_count: Optional[int] = None
    search_provider: Optional[str] = None
    
    # Follow-up questions
    suggested_questions: Optional[List[SuggestedQuestion]] = None


# ============================================================================
# AUTHENTICATION API MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds
    user: Dict[str, Any]  # User info (id, email, name)


class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User profile response"""
    id: str
    email: EmailStr
    name: str
    subscription_tier: str
    total_sessions: int
    created_at: datetime
    last_active: datetime


class UpdateProfileRequest(BaseModel):
    """
    Update user profile request
    All fields are optional - only provided fields will be updated
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    learning_preferences: Optional[LearningPreferences] = None
    emotional_profile: Optional[EmotionalProfile] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            # Strip whitespace
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty or just whitespace")
        return v



class PasswordResetRequest(BaseModel):
    """Request password reset (send reset token via email)"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token and new password"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase, one lowercase, and one number
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, and one number")
        
        return v


# ============================================================================
# DATABASE INDEXES CONFIGURATION
# ============================================================================

INDEXES = {
    "users": [
        {"keys": [("email", 1)], "unique": True},
        {"keys": [("last_active", -1)]},
        {"keys": [("is_active", 1)]}
    ],
    "login_attempts": [
        {"keys": [("email", 1), ("timestamp", -1)]},
        {"keys": [("ip_address", 1), ("timestamp", -1)]},
        {"keys": [("timestamp", -1)]}
    ],
    "refresh_tokens": [
        {"keys": [("user_id", 1), ("created_at", -1)]},
        {"keys": [("expires_at", 1)]},
        {"keys": [("revoked", 1)]}
    ],
    "sessions": [
        {"keys": [("user_id", 1), ("started_at", -1)]},
        {"keys": [("status", 1), ("started_at", -1)]},
        {"keys": [("current_topic", 1)]}
    ],
    "messages": [
        {"keys": [("session_id", 1), ("timestamp", 1)]},
        {"keys": [("user_id", 1), ("timestamp", -1)]}
    ],
    "benchmark_results": [
        {"keys": [("category", 1), ("timestamp", -1)]},
        {"keys": [("provider", 1), ("category", 1), ("timestamp", -1)]},
        {"keys": [("timestamp", -1)]}
    ],
    "provider_health": [
        {"keys": [("provider", 1), ("timestamp", -1)]},
        {"keys": [("status", 1), ("timestamp", -1)]}
    ],
    "user_performance": [
        {"keys": [("user_id", 1), ("subject", 1), ("timestamp", -1)]},
        {"keys": [("timestamp", -1)]}
    ],
    "cost_tracking": [
        {"keys": [("date", -1), ("provider", 1)]},
        {"keys": [("user_id", 1), ("date", -1)]}
    ],
    "reasoning_sessions": [
        {"keys": [("user_id", 1), ("created_at", -1)]},
        {"keys": [("session_id", 1)]},
        {"keys": [("thinking_mode", 1)]},
        {"keys": [("complexity_score", 1)]},
        {"keys": [("created_at", -1)]}
    ]
}


# ============================================================================
# DEEP THINKING / REASONING MODELS
# ============================================================================

class ReasoningSessionDocument(BaseModel):
    """
    Reasoning session - MongoDB reasoning_sessions collection
    
    Stores complete reasoning chains for analysis and improvement
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    session_id: str
    query: str
    
    # Thinking mode
    thinking_mode: str = Field(..., description="system1, system2, or hybrid")
    
    # Reasoning chain
    reasoning_steps: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_depth: int = Field(default=0, ge=0)
    conclusion: Optional[str] = None
    
    # Emotion context
    emotion_state: Optional[Dict[str, Any]] = None
    cognitive_load: float = Field(default=0.5, ge=0.0, le=1.0)
    learning_readiness: str = Field(default="moderate_readiness")
    
    # Token usage
    token_budget_allocated: int = Field(default=0, ge=0)
    token_budget_used: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    response_tokens: int = Field(default=0, ge=0)
    
    # Performance
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    total_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    processing_time_ms: float = Field(default=0.0, ge=0.0)
    
    # Quality feedback (optional, from user)
    user_feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback_helpful: Optional[bool] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ReasoningAnalytics(BaseModel):
    """
    Aggregated reasoning analytics
    
    Used for performance monitoring and improvement
    """
    date: str  # YYYY-MM-DD
    thinking_mode_distribution: Dict[str, int] = Field(default_factory=dict)
    avg_steps_per_session: float = 0.0
    avg_processing_time_ms: float = 0.0
    avg_complexity: float = 0.0
    avg_confidence: float = 0.0
    total_sessions: int = 0



# ============================================================================
# WEBSOCKET STREAMING MODELS (Phase: Real-Time Streaming)
# ============================================================================

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


class ChatStreamRequest(BaseModel):
    """Client request to start chat streaming"""
    message_id: str = Field(..., description="Client-generated message ID")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message", min_length=1)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")
    
    @field_validator('message_id', 'session_id', 'user_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")


class StopGenerationRequest(BaseModel):
    """Client request to stop ongoing generation"""
    message_id: str = Field(..., description="ID of message to cancel")
    session_id: str = Field(..., description="Session identifier")
    
    @field_validator('message_id', 'session_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")


class ThinkingStep(BaseModel):
    """Reasoning step in thinking phase"""
    step_number: int = Field(..., ge=1)
    thinking_mode: Literal["analytical", "creative", "metacognitive"]
    description: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StreamChunk(BaseModel):
    """Base class for streaming chunks"""
    message_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ThinkingChunk(StreamChunk):
    """Thinking phase chunk"""
    type: Literal["thinking_chunk"] = "thinking_chunk"
    reasoning_step: ThinkingStep


class ContentChunk(StreamChunk):
    """Content phase chunk"""
    type: Literal["content_chunk"] = "content_chunk"
    content: str
    chunk_index: int = Field(..., ge=0)
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


class EmotionUpdateEvent(StreamChunk):
    """Real-time emotion update"""
    type: Literal["emotion_update"] = "emotion_update"
    emotion: Dict[str, Any]


class ContextInfoEvent(StreamChunk):
    """Context retrieval info"""
    type: Literal["context_info"] = "context_info"
    context: Dict[str, Any]

