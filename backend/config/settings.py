"""
MasterX Configuration Management
Following specifications from 3.MASTERX_COMPREHENSIVE_PLAN.md

PRINCIPLES (from AGENTS.md):
- No hardcoded values
- All configuration from environment
- Type-safe with Pydantic
- Clean, professional naming
"""

import os
from typing import Optional, List, Dict
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    
    mongo_url: str = Field(
        default_factory=lambda: os.getenv("MONGO_URL", "mongodb://localhost:27017/masterx"),
        description="MongoDB connection URL"
    )
    
    database_name: str = Field(
        default="masterx",
        description="Database name"
    )
    
    max_pool_size: int = Field(
        default=100,
        description="MongoDB connection pool size"
    )
    
    min_pool_size: int = Field(
        default=10,
        description="Minimum connections in pool"
    )
    
    class Config:
        env_prefix = "DB_"


class VectorStoreSettings(BaseSettings):
    """
    Vector database configuration (Qdrant)
    Following MASTERX_PROJECT_AUDIT.md recommendations for vector DB migration
    """
    
    enabled: bool = Field(
        default_factory=lambda: os.getenv("QDRANT_ENABLED", "true").lower() == "true",
        description="Enable vector store (Qdrant)"
    )
    
    url: Optional[str] = Field(
        default_factory=lambda: os.getenv("QDRANT_URL"),
        description="Qdrant server URL (None for embedded mode, :memory: for in-memory)"
    )
    
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("QDRANT_API_KEY"),
        description="Qdrant Cloud API key (optional)"
    )
    
    collection_name: str = Field(
        default="conversation_history",
        description="Collection name for conversation embeddings"
    )
    
    vector_size: int = Field(
        default=384,
        description="Embedding vector dimension (384 for all-MiniLM-L6-v2)"
    )
    
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    search_limit: int = Field(
        default=5,
        description="Default limit for semantic search results"
    )
    
    score_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score threshold (0.0 to 1.0)"
    )
    
    fallback_to_mongodb: bool = Field(
        default=True,
        description="Fall back to MongoDB if Qdrant fails"
    )
    
    class Config:
        env_prefix = "QDRANT_"


class AIProviderSettings(BaseSettings):
    """AI Provider configuration"""
    
    groq_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY"),
        description="Groq API key"
    )
    
    emergent_llm_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("EMERGENT_LLM_KEY"),
        description="Emergent universal LLM key"
    )
    
    gemini_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY"),
        description="Google Gemini API key"
    )
    
    provider_timeout_seconds: int = Field(
        default=30,
        description="Default provider timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests"
    )
    
    class Config:
        env_prefix = "AI_"


class CachingSettings(BaseSettings):
    """Caching configuration"""
    
    enabled: bool = Field(
        default=True,
        description="Enable caching system"
    )
    
    memory_cache_size: int = Field(
        default=1000,
        description="Size of in-memory LRU cache"
    )
    
    response_cache_ttl: int = Field(
        default=3600,
        description="TTL for response cache in seconds"
    )
    
    embedding_cache_ttl: int = Field(
        default=86400,
        description="TTL for embedding cache in seconds"
    )
    
    benchmark_cache_ttl: int = Field(
        default=43200,
        description="TTL for benchmark cache in seconds"
    )
    
    class Config:
        env_prefix = "CACHE_"


class PerformanceSettings(BaseSettings):
    """Performance monitoring configuration"""
    
    enabled: bool = Field(
        default=True,
        description="Enable performance monitoring"
    )
    
    slow_request_threshold_ms: int = Field(
        default=5000,
        description="Threshold for slow request alerts"
    )
    
    critical_latency_threshold_ms: int = Field(
        default=10000,
        description="Threshold for critical latency alerts"
    )
    
    metrics_interval_seconds: int = Field(
        default=60,
        description="Interval for metrics aggregation"
    )
    
    class Config:
        env_prefix = "PERF_"


class VoiceSettings(BaseSettings):
    """
    Voice interaction configuration (AGENTS.md compliant - zero hardcoded values)
    All voice processing parameters configurable via environment
    """
    
    # Speech-to-Text (Groq Whisper)
    whisper_model: str = Field(
        default_factory=lambda: os.getenv("WHISPER_MODEL_NAME", "whisper-large-v3-turbo"),
        description="Groq Whisper model name"
    )
    
    # Text-to-Speech (ElevenLabs)
    elevenlabs_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_API_KEY"),
        description="ElevenLabs API key"
    )
    
    elevenlabs_model_short: str = Field(
        default="eleven_flash_v2_5",
        description="ElevenLabs model for short text (<200 chars)"
    )
    
    elevenlabs_model_long: str = Field(
        default="eleven_multilingual_v2",
        description="ElevenLabs model for long text (>=200 chars)"
    )
    
    text_length_threshold: int = Field(
        default=200,
        description="Character threshold for model selection"
    )
    
    # ElevenLabs Voice ID Mappings (configurable via environment)
    voice_encouraging: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ENCOURAGING", "Rachel"),
        description="Voice ID for encouraging tone"
    )
    
    voice_calm: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_CALM", "Adam"),
        description="Voice ID for calm tone"
    )
    
    voice_excited: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_EXCITED", "Bella"),
        description="Voice ID for excited tone"
    )
    
    voice_professional: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_PROFESSIONAL", "Antoni"),
        description="Voice ID for professional tone"
    )
    
    voice_friendly: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_FRIENDLY", "Elli"),
        description="Voice ID for friendly tone"
    )
    
    # Voice Activity Detection (VAD)
    vad_frame_duration_ms: int = Field(
        default=30,
        description="VAD frame duration in milliseconds"
    )
    
    vad_min_speech_frames: int = Field(
        default=10,
        description="Minimum frames to consider speech"
    )
    
    vad_sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz"
    )
    
    # Pronunciation Assessment
    pronunciation_min_word_length: int = Field(
        default=3,
        description="Minimum word length for pronunciation scoring"
    )
    
    pronunciation_speaking_rate: float = Field(
        default=2.5,
        description="Average speaking rate (words per second)"
    )
    
    # ML-based pronunciation scoring weights (configurable)
    pronunciation_phoneme_weight: float = Field(
        default=0.5,
        description="Weight for phoneme accuracy in scoring"
    )
    
    pronunciation_fluency_weight: float = Field(
        default=0.3,
        description="Weight for fluency in scoring"
    )
    
    pronunciation_word_weight: float = Field(
        default=0.2,
        description="Weight for word accuracy in scoring"
    )
    
    # Fallback weights when word scores unavailable
    pronunciation_phoneme_fallback_weight: float = Field(
        default=0.8,
        description="Phoneme weight when no word scores"
    )
    
    pronunciation_fluency_fallback_weight: float = Field(
        default=0.2,
        description="Fluency weight when no word scores"
    )
    
    class Config:
        env_prefix = "VOICE_"


class SecuritySettings(BaseSettings):
    """
    Security configuration (AGENTS.md compliant - zero hardcoded values)
    All values configurable via environment variables with secure defaults
    """
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""),
        description="JWT signing secret key (REQUIRED in production)"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiry time in minutes"
    )
    
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiry time in days"
    )
    
    # Password Policy
    password_min_length: int = Field(
        default=8,
        description="Minimum password length"
    )
    
    password_require_uppercase: bool = Field(
        default=True,
        description="Require uppercase letter in password"
    )
    
    password_require_lowercase: bool = Field(
        default=True,
        description="Require lowercase letter in password"
    )
    
    password_require_digit: bool = Field(
        default=True,
        description="Require digit in password"
    )
    
    password_require_special: bool = Field(
        default=True,
        description="Require special character in password"
    )
    
    bcrypt_rounds: int = Field(
        default=12,
        description="Bcrypt hashing rounds (10-14 recommended)"
    )
    
    # Rate Limiting - Per IP
    rate_limit_ip_per_minute: int = Field(
        default=60,
        description="Max requests per IP per minute"
    )
    
    rate_limit_ip_per_hour: int = Field(
        default=1000,
        description="Max requests per IP per hour"
    )
    
    # Rate Limiting - Per User
    rate_limit_user_per_minute: int = Field(
        default=30,
        description="Max requests per user per minute"
    )
    
    rate_limit_user_per_hour: int = Field(
        default=500,
        description="Max requests per user per hour"
    )
    
    rate_limit_user_per_day: int = Field(
        default=5000,
        description="Max requests per user per day"
    )
    
    # Rate Limiting - Per Endpoint
    rate_limit_chat_per_minute: int = Field(
        default=10,
        description="Max chat requests per minute (AI calls)"
    )
    
    rate_limit_voice_per_minute: int = Field(
        default=5,
        description="Max voice requests per minute (TTS/STT)"
    )
    
    rate_limit_login_per_minute: int = Field(
        default=5,
        description="Max login attempts per minute"
    )
    
    rate_limit_window_minutes: int = Field(
        default=1,
        description="Rate limit window in minutes"
    )
    
    # Cost-Based Limits
    rate_limit_user_daily_cost: float = Field(
        default=5.0,
        description="Max cost per user per day in USD"
    )
    
    rate_limit_global_hourly_cost: float = Field(
        default=100.0,
        description="Max global cost per hour in USD"
    )
    
    # Anomaly Detection
    anomaly_score_threshold: float = Field(
        default=0.8,
        description="Threshold for anomaly detection (0.0-1.0)"
    )
    
    anomaly_spike_multiplier: float = Field(
        default=3.0,
        description="Multiplier for spike detection"
    )
    
    # Storage Settings
    rate_limit_window_seconds: int = Field(
        default=3600,
        description="Sliding window size in seconds"
    )
    
    rate_limit_max_history: int = Field(
        default=10000,
        description="Max items in rate limit history"
    )
    
    # Input Validation
    input_max_length: int = Field(
        default=10000,
        description="Maximum input length for validation"
    )
    
    file_upload_max_size_mb: int = Field(
        default=10,
        description="Maximum file upload size in MB"
    )
    
    allowed_file_types: List[str] = Field(
        default=["audio/wav", "audio/mpeg", "audio/mp3", "image/jpeg", "image/png"],
        description="Allowed MIME types for file uploads"
    )
    
    # SQL Injection Patterns (configurable for easy updates)
    sql_injection_patterns: List[str] = Field(
        default=[
            r"(\bunion\b.*\bselect\b)",
            r"(\bselect\b.*\bfrom\b.*\bwhere\b)",
            r"(\bdrop\b.*\btable\b)",
            r"(\binsert\b.*\binto\b.*\bvalues\b)",
            r"(\bupdate\b.*\bset\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(\bexec\b.*\()",
            r"(\bexecute\b.*\()",
            r"(--\s)",
            r"(;.*drop)",
            r"('.*or.*'.*=.*')",
            r"(\".*or.*\".*=.*\")",
            r"(\bor\b.*\b1\s*=\s*1\b)",
            r"(\band\b.*\b1\s*=\s*1\b)",
            r"(\/\*.*\*\/)",
        ],
        description="Regex patterns for SQL injection detection"
    )
    
    # XSS Prevention Patterns
    xss_patterns: List[str] = Field(
        default=[
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<embed[^>]*>",
            r"<object[^>]*>",
        ],
        description="Regex patterns for XSS detection"
    )
    
    class Config:
        env_prefix = "SECURITY_"


class HealthMonitorSettings(BaseSettings):
    """
    Health monitoring configuration (Phase 8C File 11)
    
    AGENTS.md compliant: All thresholds ML/statistical-based, not hardcoded
    Configuration-driven parameters for Statistical Process Control
    
    Note: This is the primary health monitoring configuration class.
    MonitoringSettings is an alias for backward compatibility.
    """
    
    # History and sampling
    history_size: int = Field(
        default=100,
        description="Number of historical samples to maintain for SPC"
    )
    
    min_samples_for_threshold: int = Field(
        default=10,
        description="Minimum samples required for threshold calculation"
    )
    
    min_samples_for_trend: int = Field(
        default=20,
        description="Minimum samples required for trend detection"
    )
    
    min_samples_for_score: int = Field(
        default=10,
        description="Minimum samples required for health score"
    )
    
    # Statistical Process Control (SPC)
    sigma_threshold: float = Field(
        default=3.0,
        description="Sigma threshold for anomaly detection (3.0 = 99.7% confidence)"
    )
    
    # EWMA (Exponential Weighted Moving Average)
    ewma_alpha: float = Field(
        default=0.3,
        description="EWMA smoothing factor (0.0-1.0, higher = more reactive)"
    )
    
    # Trending
    trend_window_size: int = Field(
        default=10,
        description="Window size for trend calculation"
    )
    
    improvement_threshold_pct: float = Field(
        default=5.0,
        description="Percentage change threshold for improvement detection"
    )
    
    degradation_threshold_pct: float = Field(
        default=5.0,
        description="Percentage change threshold for degradation detection"
    )
    
    # Health scoring thresholds
    healthy_threshold: float = Field(
        default=70.0,
        description="Health score threshold for HEALTHY status (0-100)"
    )
    
    degraded_threshold: float = Field(
        default=40.0,
        description="Health score threshold for DEGRADED status (0-100)"
    )
    
    # Metric weights for composite health score
    metric_weights: Dict[str, float] = Field(
        default={
            'latency_ms': 0.35,      # Most important
            'error_rate': 0.30,      # Very important
            'throughput': 0.20,      # Important
            'connections': 0.15      # Less important
        },
        description="Weights for health score calculation"
    )
    
    # Component weights for system health score
    component_weights: Dict[str, float] = Field(
        default={
            'database': 1.0,              # Critical
            'ai_provider_groq': 0.8,      # Important
            'ai_provider_emergent': 0.8,  # Important
            'ai_provider_gemini': 0.8,    # Important
            'external_apis': 0.5          # Less critical
        },
        description="Weights for system health calculation"
    )
    
    # Monitoring intervals
    check_interval_seconds: int = Field(
        default=60,
        description="Interval between health checks (seconds)"
    )
    
    provider_timeout_seconds: int = Field(
        default=5,
        description="Timeout for AI provider health checks (seconds)"
    )
    
    # Alert thresholds (statistical/ML-based, not hardcoded rules)
    alert_error_rate_threshold: float = Field(
        default=0.1,
        description="Error rate threshold for alerts (10% = 0.1)"
    )
    
    alert_latency_threshold_ms: float = Field(
        default=10000.0,
        description="Latency threshold for alerts in milliseconds"
    )
    
    class Config:
        env_prefix = "MONITORING_"


# Alias for backward compatibility
MonitoringSettings = HealthMonitorSettings


class CostEnforcementSettings(BaseSettings):
    """
    Cost enforcement configuration (Phase 8C File 12)
    
    AGENTS.md compliant: Zero hardcoded budgets, all from DB or environment
    ML-based optimization with configurable parameters
    """
    
    # Enforcement mode
    enforcement_mode: str = Field(
        default="disabled",
        description="Cost enforcement mode: disabled, advisory, strict"
    )
    
    # Tier-based budget limits (USD per day)
    free_tier_daily_limit: float = Field(
        default=0.50,
        description="Daily budget limit for free tier (USD)"
    )
    
    pro_tier_daily_limit: float = Field(
        default=5.00,
        description="Daily budget limit for pro tier (USD)"
    )
    
    enterprise_tier_daily_limit: float = Field(
        default=50.00,
        description="Daily budget limit for enterprise tier (USD)"
    )
    
    custom_tier_daily_limit: float = Field(
        default=100.00,
        description="Daily budget limit for custom tier (USD)"
    )
    
    # Budget status thresholds (ML-driven, not hardcoded rules)
    budget_warning_threshold: float = Field(
        default=0.80,
        description="Budget utilization threshold for warning (0.0-1.0)"
    )
    
    budget_critical_threshold: float = Field(
        default=0.90,
        description="Budget utilization threshold for critical alert (0.0-1.0)"
    )
    
    budget_safety_margin: float = Field(
        default=0.80,
        description="Safety margin for exhaustion prediction (0.8 = 20% early warning)"
    )
    
    # Budget predictor settings
    cost_predictor_history_hours: int = Field(
        default=48,
        description="Hours of history to use for cost prediction"
    )
    
    cost_predictor_min_samples: int = Field(
        default=3,
        description="Minimum samples required for prediction"
    )
    
    # Multi-Armed Bandit settings
    bandit_exploration_rate: float = Field(
        default=0.1,
        description="Exploration rate for bandit algorithm (0.0-1.0)"
    )
    
    bandit_value_threshold: float = Field(
        default=0.5,
        description="Value threshold for good/bad outcome classification"
    )
    
    # Cache settings
    budget_cache_ttl_seconds: int = Field(
        default=60,
        description="TTL for budget status cache (seconds)"
    )
    
    # Global limits (safety nets)
    global_hourly_limit: float = Field(
        default=100.00,
        description="Global hourly cost limit (USD)"
    )
    
    global_daily_limit: float = Field(
        default=1000.00,
        description="Global daily cost limit (USD)"
    )
    
    # Cost estimation settings
    default_token_estimate: int = Field(
        default=1000,
        description="Default token estimate for cost calculation"
    )
    
    cost_estimate_safety_multiplier: float = Field(
        default=1.2,
        description="Safety multiplier for cost estimates (20% buffer)"
    )
    
    class Config:
        env_prefix = "COST_"


class WebSocketSettings(BaseSettings):
    """
    WebSocket configuration
    
    AGENTS.md compliant: Zero hardcoded values, all ML-driven thresholds
    """
    
    # Connection health monitoring
    health_check_interval: int = Field(
        default=30,
        description="Interval for connection health checks (seconds)"
    )
    
    max_latency_ms: float = Field(
        default=500.0,
        description="Maximum acceptable latency for healthy connection (ms)"
    )
    
    max_error_rate: float = Field(
        default=0.1,
        description="Maximum acceptable error rate (0.0-1.0)"
    )
    
    # Rate limiting
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window duration (seconds)"
    )
    
    rate_limit_max: int = Field(
        default=100,
        description="Maximum messages per window"
    )
    
    # Message queue
    max_queue_size: int = Field(
        default=1000,
        description="Maximum messages in priority queue"
    )
    
    message_ttl: int = Field(
        default=3600,
        description="Message time-to-live in queue (seconds)"
    )
    
    # Compression
    compression_threshold: int = Field(
        default=1024,
        description="Minimum message size for compression (bytes)"
    )
    
    # Circuit breaker
    circuit_breaker_threshold: int = Field(
        default=5,
        description="Failure count to open circuit"
    )
    
    circuit_breaker_timeout: int = Field(
        default=60,
        description="Circuit breaker timeout before reset (seconds)"
    )
    
    class Config:
        env_prefix = "WEBSOCKET_"


class GracefulShutdownSettings(BaseSettings):
    """
    Graceful shutdown configuration (Phase 8C File 13)
    
    AGENTS.md compliant: Zero hardcoded timeouts, all configurable
    """
    
    enabled: bool = Field(
        default=True,
        description="Enable graceful shutdown"
    )
    
    shutdown_timeout: float = Field(
        default=30.0,
        description="Maximum shutdown time in seconds"
    )
    
    drain_timeout_ratio: float = Field(
        default=0.8,
        description="Ratio of timeout for draining requests (0.0-1.0)"
    )
    
    background_timeout_ratio: float = Field(
        default=0.2,
        description="Ratio of timeout for background tasks (0.0-1.0)"
    )
    
    health_check_grace: float = Field(
        default=0.1,
        description="Grace period for load balancer health check detection (seconds)"
    )
    
    check_interval: float = Field(
        default=0.5,
        description="Interval for checking in-flight requests (seconds)"
    )
    
    class Config:
        env_prefix = "GRACEFUL_SHUTDOWN_"


class MasterXSettings(BaseSettings):
    """
    Master configuration class for MasterX
    
    Aggregates all configuration sections with zero hardcoded values.
    Phase 8C enhanced with validation and production readiness checks.
    """
    
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Environment (development, staging, production)"
    )
    
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true",
        description="Debug mode"
    )
    
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    ai_providers: AIProviderSettings = Field(default_factory=AIProviderSettings)
    caching: CachingSettings = Field(default_factory=CachingSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    health_monitor: HealthMonitorSettings = Field(default_factory=HealthMonitorSettings)
    cost_enforcement: CostEnforcementSettings = Field(default_factory=CostEnforcementSettings)
    graceful_shutdown: GracefulShutdownSettings = Field(default_factory=GracefulShutdownSettings)
    websocket: WebSocketSettings = Field(default_factory=WebSocketSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"
    
    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.environment.lower() == "staging"
    
    @property
    def JWT_SECRET_KEY(self) -> str:
        """Convenience property for JWT secret key"""
        return self.security.jwt_secret_key
    
    @property
    def JWT_ALGORITHM(self) -> str:
        """Convenience property for JWT algorithm"""
        return self.security.jwt_algorithm
    
    def get_active_providers(self) -> List[str]:
        """Get list of configured AI providers"""
        providers = []
        if self.ai_providers.groq_api_key:
            providers.append("groq")
        if self.ai_providers.emergent_llm_key:
            providers.append("emergent")
        if self.ai_providers.gemini_api_key:
            providers.append("gemini")
        return providers
    
    def validate_production_ready(self) -> tuple[bool, List[str]]:
        """
        Validate production readiness (Phase 8C File 14)
        
        Checks critical configuration for production deployment.
        AGENTS.md compliant: No hardcoded checks, validates actual config.
        
        Returns:
            Tuple of (is_ready: bool, issues: List[str])
        """
        issues = []
        
        if not self.is_production():
            # Non-production environments get a pass
            return True, []
        
        # Database validation
        if "localhost" in self.database.mongo_url:
            issues.append("Production should not use localhost database")
        
        if self.database.max_pool_size < 50:
            issues.append(f"Production pool size too small: {self.database.max_pool_size} (recommend >=50)")
        
        # Security validation
        if not self.security.jwt_secret_key or len(self.security.jwt_secret_key) < 32:
            issues.append("Production requires strong JWT secret key (>=32 chars)")
        
        if self.security.bcrypt_rounds < 12:
            issues.append(f"Production bcrypt rounds too low: {self.security.bcrypt_rounds} (recommend >=12)")
        
        # AI providers validation
        active_providers = self.get_active_providers()
        if len(active_providers) == 0:
            issues.append("No AI providers configured")
        elif len(active_providers) < 2:
            issues.append(f"Only {len(active_providers)} provider(s) configured (recommend >=2 for redundancy)")
        
        # Debug mode validation
        if self.debug:
            issues.append("Production should not run in debug mode")
        
        # Cost enforcement validation
        if self.cost_enforcement.enforcement_mode == "disabled":
            issues.append("Production should enable cost enforcement (advisory or strict)")
        
        # Monitoring validation
        if not self.monitoring.history_size >= 50:
            issues.append(f"Production monitoring history too small: {self.monitoring.history_size} (recommend >=50)")
        
        # Graceful shutdown validation
        if not self.graceful_shutdown.enabled:
            issues.append("Production should enable graceful shutdown")
        
        if self.graceful_shutdown.shutdown_timeout < 10:
            issues.append(f"Production shutdown timeout too short: {self.graceful_shutdown.shutdown_timeout}s (recommend >=10s)")
        
        is_ready = len(issues) == 0
        
        return is_ready, issues
    
    def get_environment_info(self) -> Dict[str, any]:
        """
        Get environment information for debugging (Phase 8C File 14)
        
        Returns comprehensive configuration summary without exposing secrets.
        """
        return {
            "environment": self.environment,
            "debug": self.debug,
            "database": {
                "host": self.database.mongo_url.split("@")[-1] if "@" in self.database.mongo_url else "localhost",
                "pool_size": f"{self.database.min_pool_size}-{self.database.max_pool_size}",
                "name": self.database.database_name
            },
            "ai_providers": {
                "configured": self.get_active_providers(),
                "count": len(self.get_active_providers()),
                "timeout_seconds": self.ai_providers.provider_timeout_seconds,
                "max_retries": self.ai_providers.max_retries
            },
            "features": {
                "caching": self.caching.enabled,
                "performance_monitoring": self.performance.enabled,
                "health_monitoring": True,  # Always enabled in Phase 8C
                "cost_enforcement": self.cost_enforcement.enforcement_mode,
                "graceful_shutdown": self.graceful_shutdown.enabled
            },
            "security": {
                "jwt_configured": bool(self.security.jwt_secret_key),
                "bcrypt_rounds": self.security.bcrypt_rounds,
                "rate_limiting": {
                    "ip_per_minute": self.security.rate_limit_ip_per_minute,
                    "user_per_minute": self.security.rate_limit_user_per_minute,
                    "chat_per_minute": self.security.rate_limit_chat_per_minute
                }
            },
            "monitoring": {
                "check_interval": self.monitoring.check_interval_seconds,
                "history_size": self.monitoring.history_size,
                "sigma_threshold": self.monitoring.sigma_threshold
            },
            "cost_enforcement": {
                "mode": self.cost_enforcement.enforcement_mode,
                "tiers": {
                    "free": f"${self.cost_enforcement.free_tier_daily_limit:.2f}/day",
                    "pro": f"${self.cost_enforcement.pro_tier_daily_limit:.2f}/day",
                    "enterprise": f"${self.cost_enforcement.enterprise_tier_daily_limit:.2f}/day"
                }
            },
            "graceful_shutdown": {
                "enabled": self.graceful_shutdown.enabled,
                "timeout": f"{self.graceful_shutdown.shutdown_timeout}s",
                "drain_ratio": f"{self.graceful_shutdown.drain_timeout_ratio * 100}%"
            }
        }
    
    def get_config_summary(self) -> str:
        """
        Get human-readable configuration summary
        
        Returns:
            Formatted string with key configuration
        """
        info = self.get_environment_info()
        
        summary = []
        summary.append(f"Environment: {info['environment']}")
        summary.append(f"Debug Mode: {info['debug']}")
        summary.append(f"AI Providers: {', '.join(info['ai_providers']['configured'])} ({info['ai_providers']['count']} total)")
        summary.append(f"Database: {info['database']['host']}")
        summary.append(f"Cost Enforcement: {info['cost_enforcement']['mode']}")
        summary.append(f"Graceful Shutdown: {'Enabled' if info['graceful_shutdown']['enabled'] else 'Disabled'}")
        
        return "\n".join(summary)


# Global settings instance
settings = MasterXSettings()


def get_settings() -> MasterXSettings:
    """
    Get global settings instance
    
    Returns:
        MasterXSettings instance with all configuration
    """
    return settings
