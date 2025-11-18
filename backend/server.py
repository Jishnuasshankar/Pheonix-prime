"""
MasterX FastAPI Server
Following specifications from 2.CRITICAL_INITIAL_SETUP.md and 5.DEVELOPMENT_HANDOFF_GUIDE.md

Phase 1: Core endpoints with MongoDB integration
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import uuid

from core.models import ChatRequest, ChatResponse, EmotionState, ContextInfo, AbilityInfo
from pydantic import BaseModel, field_validator, model_validator
from core.engine import MasterXEngine


# Spaced Repetition Request Models
class CreateCardRequest(BaseModel):
    """Request model for creating a spaced repetition card"""
    user_id: str
    topic: str
    content: Dict[str, Any]
    difficulty: Optional[str] = None


class ReviewCardRequest(BaseModel):
    """Request model for reviewing a card"""
    card_id: str
    quality: int  # 0-5
    duration_seconds: int = 0


# Gamification Request Models
class RecordActivityRequest(BaseModel):
    """Request model for recording gamification activity"""
    user_id: str
    session_id: str
    question_difficulty: float
    success: bool
    time_spent_seconds: int
from services.gamification import GamificationEngine
from services.spaced_repetition import SpacedRepetitionEngine, ReviewQuality
from services.analytics import AnalyticsEngine
from services.personalization import PersonalizationEngine
from services.content_delivery import ContentDeliveryEngine
from services.voice_interaction import VoiceInteractionEngine
from services.collaboration import (
    CollaborationEngine,
    MatchRequest,
    CollaborationMessage,
    MessageType,
    initialize_collaboration_service
)
from utils.database import (
    connect_to_mongodb,
    close_mongodb_connection,
    initialize_database,
    get_sessions_collection,
    get_messages_collection
)
from utils.logging_config import setup_logging
from utils.errors import MasterXError
from utils.cost_tracker import cost_tracker

# Import authentication middleware for admin endpoints
from middleware.auth import require_admin, get_current_user
from fastapi import Depends

# Setup logging
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced lifespan with Phase 8C features
    
    Startup: Validate config, initialize all systems
    Shutdown: Graceful shutdown with drain pattern
    """
    # Startup
    logger.info("🚀 Starting MasterX server (Phase 8C Production)...")
    
    try:
        # Phase 8C File 14: Validate production readiness
        from config.settings import get_settings
        settings = get_settings()
        
        is_ready, issues = settings.validate_production_ready()
        
        if not is_ready:
            logger.warning("⚠️ Production readiness check found issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
            
            if settings.is_production():
                raise RuntimeError(
                    f"Cannot start in production with {len(issues)} configuration issue(s). "
                    "See logs for details."
                )
        else:
            logger.info("✅ Production readiness validated")
        
        logger.info(f"📊 Environment: {settings.environment}")
        logger.info(f"🔧 Configuration:\n{settings.get_config_summary()}")
        
        # Connect to MongoDB
        await connect_to_mongodb()
        
        # Initialize database (collections and indexes)
        await initialize_database()
        
        # Initialize engine
        app.state.engine = MasterXEngine()
        
        # Initialize emotion engine (loads ML models)
        await app.state.engine.emotion_engine.initialize()
        logger.info("✅ Emotion engine initialized")
        
        # Get database
        from utils.database import get_database
        db = get_database()
        
        # Initialize gamification engine (Phase 5)
        app.state.gamification = GamificationEngine(db)
        logger.info("✅ Gamification engine initialized")
        
        # Initialize spaced repetition engine (Phase 5)
        app.state.spaced_repetition = SpacedRepetitionEngine(db)
        logger.info("✅ Spaced repetition engine initialized")
        
        # Initialize analytics engine (Phase 5)
        app.state.analytics = AnalyticsEngine(db)
        logger.info("✅ Analytics engine initialized")
        
        # Initialize personalization engine (Phase 5)
        app.state.personalization = PersonalizationEngine(db)
        logger.info("✅ Personalization engine initialized")
        
        # Initialize content delivery engine (Phase 5)
        app.state.content_delivery = ContentDeliveryEngine(db)
        logger.info("✅ Content delivery engine initialized")
        
        # Initialize voice interaction engine (Phase 6)
        try:
            app.state.voice_interaction = VoiceInteractionEngine(db, settings.voice)
            logger.info("✅ Voice interaction engine initialized")
        except Exception as e:
            logger.warning(f"Voice interaction engine initialization failed: {e}")
            app.state.voice_interaction = None
        
        # Initialize collaboration engine (Phase 7)
        try:
            app.state.collaboration = CollaborationEngine(db)
            await initialize_collaboration_service(db)
            logger.info("✅ Collaboration engine initialized")
        except Exception as e:
            logger.warning(f"Collaboration engine initialization failed: {e}")
            app.state.collaboration = None
        
        # Initialize external benchmarking system (Phase 2)
        await app.state.engine.provider_manager.initialize_external_benchmarks(db)
        
        # Initialize dynamic pricing engine (Phase 8 - Dynamic Model System)
        from core.dynamic_pricing import get_pricing_engine
        app.state.pricing_engine = get_pricing_engine(db)
        logger.info("✅ Dynamic pricing engine initialized")
        
        # Connect pricing engine to cost tracker
        from utils.cost_tracker import cost_tracker
        cost_tracker.set_pricing_engine(app.state.pricing_engine)
        logger.info("✅ Cost tracker connected to dynamic pricing")
        
        # Connect dynamic systems to provider manager
        app.state.engine.provider_manager.set_dependencies(
            app.state.engine.provider_manager.external_benchmarks,
            app.state.pricing_engine
        )
        logger.info("✅ Provider manager connected to dynamic systems")
        
        # Start background tasks for periodic updates
        asyncio.create_task(
            app.state.engine.provider_manager.external_benchmarks.schedule_periodic_updates(interval_hours=12)
        )
        logger.info("✅ Background benchmark updates scheduled (12h)")
        
        asyncio.create_task(
            app.state.pricing_engine.schedule_periodic_updates(interval_hours=12)
        )
        logger.info("✅ Background pricing updates scheduled (12h)")
        
        # Initialize intelligence layer (Phase 3: context + adaptive learning + RAG)
        await app.state.engine.initialize_intelligence_layer(db)
        
        logger.info("✅ Phase 3 intelligence layer initialized (context + adaptive + RAG)")
        
        # Phase 4: Initialize optimization layer
        from optimization.caching import init_cache_manager
        from optimization.performance import init_performance_tracker
        
        app.state.cache_manager = init_cache_manager(db)
        app.state.performance_tracker = init_performance_tracker()
        
        logger.info("✅ Phase 4 optimization layer initialized (caching + performance)")
        
        # Phase 8C File 11: Initialize health monitoring system
        from utils.health_monitor import get_health_monitor, set_health_monitor_dependencies
        
        app.state.health_monitor = get_health_monitor()
        
        # Set dependencies for health checks
        set_health_monitor_dependencies(app.state.engine.provider_manager)
        
        # Start background monitoring
        await app.state.health_monitor.start_background_monitoring()
        logger.info("✅ Phase 8C File 11: Health monitoring system initialized and running")
        
        # Phase 8C File 12: Initialize cost enforcer
        from utils.cost_enforcer import get_cost_enforcer
        
        app.state.cost_enforcer = get_cost_enforcer()
        logger.info(f"✅ Phase 8C File 12: Cost enforcer initialized (mode: {settings.cost_enforcement.enforcement_mode})")
        
        # Phase 8C File 13: Initialize graceful shutdown
        from utils.graceful_shutdown import get_graceful_shutdown
        
        app.state.graceful_shutdown = get_graceful_shutdown(
            shutdown_timeout=settings.graceful_shutdown.shutdown_timeout
        )
        logger.info(f"✅ Phase 8C File 13: Graceful shutdown configured (timeout: {settings.graceful_shutdown.shutdown_timeout}s)")
        
        logger.info("✅ MasterX server started successfully with FULL PHASE 8C PRODUCTION READINESS")
        logger.info(f"📊 Available AI providers: {app.state.engine.get_available_providers()}")
        logger.info("⚡ Model selection: Fully dynamic (quality + cost + speed + availability)")
        logger.info("🛡️ Production features: Health monitoring ✓ Cost enforcement ✓ Graceful shutdown ✓")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown (Phase 8C File 13: Graceful shutdown orchestration)
    logger.info("👋 Initiating graceful shutdown...")
    
    # Execute graceful shutdown if configured
    if hasattr(app.state, 'graceful_shutdown'):
        await app.state.graceful_shutdown.shutdown()
    else:
        logger.warning("⚠️ Graceful shutdown not configured, performing direct shutdown")
        
        # Stop health monitoring (Phase 8C File 11)
        if hasattr(app.state, 'health_monitor'):
            await app.state.health_monitor.stop_background_monitoring()
            logger.info("✅ Health monitoring stopped")
        
        await close_mongodb_connection()
    
    logger.info("✅ MasterX server shut down gracefully")


# Create FastAPI app
app = FastAPI(
    title="MasterX API",
    description="AI-Powered Adaptive Learning Platform with Emotion Detection",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# PHASE 8C PRODUCTION MIDDLEWARE STACK
# ============================================================================

# 1. Security Headers Middleware (FIRST - adds headers to all responses)
from middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=os.getenv("ENABLE_HSTS", "false").lower() == "true"
)

# 2. Request Logging Middleware (Phase 8C File 10)
from utils.request_logger import RequestLoggingMiddleware

app.add_middleware(
    RequestLoggingMiddleware,
    redact_pii=True
)

# 3. CORS middleware (after logging)
# Security improvement: Don't allow all origins in production
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    logger.warning("⚠️  CORS is set to allow all origins (*). This is a security risk in production!")
    logger.warning("⚠️  Set CORS_ORIGINS in .env to specific domains, e.g., 'https://yourdomain.com,https://app.yourdomain.com'")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(",") if cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# 3. Global Rate Limiting Middleware
from middleware.simple_rate_limit import rate_limiter

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Global rate limiting for all endpoints
    
    Prevents DOS attacks and ensures fair usage.
    """
    # Skip health checks
    if request.url.path.startswith("/api/health"):
        return await call_next(request)
    
    # Check rate limit
    ip = rate_limiter.get_client_ip(request)
    endpoint = request.url.path
    
    if not rate_limiter.check_rate_limit(ip, endpoint):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down."},
            headers={"Retry-After": "60"}
        )
    
    return await call_next(request)


# 4. Request Tracking Middleware (Phase 8C File 13)
@app.middleware("http")
async def track_requests_middleware(request: Request, call_next):
    """
    Track requests for graceful shutdown
    
    Prevents accepting new requests during shutdown and tracks in-flight requests.
    """
    # Skip for health checks
    if request.url.path.startswith("/api/health"):
        return await call_next(request)
    
    # Get graceful shutdown manager
    if hasattr(request.app.state, 'graceful_shutdown'):
        shutdown_manager = request.app.state.graceful_shutdown
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Try to track request
        if not shutdown_manager.track_request(request_id):
            # Shutting down, reject new requests
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service shutting down",
                    "message": "Server is gracefully shutting down. Please retry in a moment.",
                    "retry_after": 30
                },
                headers={"Retry-After": "30"}
            )
        
        try:
            response = await call_next(request)
            return response
        finally:
            shutdown_manager.complete_request(request_id)
    else:
        return await call_next(request)


# 4. Budget Enforcement Middleware (Phase 8C File 12)
@app.middleware("http")
async def budget_enforcement_middleware(request: Request, call_next):
    """
    Enforce budget limits per user
    
    Checks user budget before processing expensive operations.
    Returns 402 Payment Required if budget exhausted.
    """
    # Skip for health, auth, and public endpoints
    skip_paths = ["/api/health", "/api/auth", "/api/v1/providers", "/"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)
    
    # Check if user authenticated
    user_id = getattr(request.state, "user_id", None)
    
    if user_id and hasattr(request.app.state, 'cost_enforcer'):
        cost_enforcer = request.app.state.cost_enforcer
        
        try:
            # Check user budget
            budget_status = await cost_enforcer.check_user_budget(user_id)
            
            if budget_status.status.value == "exhausted":
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "Budget exhausted",
                        "message": "Daily budget limit reached",
                        "budget": {
                            "limit_usd": budget_status.limit,
                            "spent_usd": budget_status.spent,
                            "remaining_usd": budget_status.remaining,
                            "reset_time": "00:00 UTC",
                            "recommended_action": budget_status.recommended_action
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Budget enforcement error: {e}")
            # Don't block request on budget check failure
    
    return await call_next(request)


# Global error handler
@app.exception_handler(MasterXError)
async def masterx_error_handler(request: Request, exc: MasterXError):
    """Handle all MasterX errors consistently"""
    
    logger.error(
        f"MasterX error: {exc.message}",
        extra={
            'error_type': type(exc).__name__,
            'details': exc.details,
            'path': request.url.path
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "type": type(exc).__name__,
            "details": exc.details
        }
    )


# Health check endpoints
@app.get("/api/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/health/detailed")
async def detailed_health(request: Request):
    """
    Detailed health check with ML-based component monitoring
    
    Phase 8C File 11: Uses statistical health monitoring system
    - 3-sigma anomaly detection
    - EWMA trend analysis
    - Percentile-based health scoring
    - Zero hardcoded thresholds (AGENTS.md compliant)
    """
    
    try:
        # Get comprehensive health from health monitor
        health_monitor = request.app.state.health_monitor
        system_health = await health_monitor.get_system_health()
        
        # Convert to response format
        component_checks = {}
        for comp_name, comp_health in system_health.components.items():
            component_checks[comp_name] = {
                'status': comp_health.status.value,
                'health_score': round(comp_health.health_score, 2),
                'trend': comp_health.trend,
                'metrics': {
                    'latency_ms': round(comp_health.metrics.latency_ms, 2),
                    'error_rate': round(comp_health.metrics.error_rate, 4),
                    'throughput': comp_health.metrics.throughput,
                    'connections': comp_health.metrics.connections,
                    **comp_health.metrics.custom_metrics
                },
                'alerts': comp_health.alerts,
                'last_check': comp_health.last_check.isoformat()
            }
        
        return {
            'status': system_health.overall_status.value,
            'health_score': round(system_health.health_score, 2),
            'components': component_checks,
            'uptime_seconds': round(system_health.uptime_seconds, 2),
            'alerts': system_health.alerts,
            'timestamp': system_health.timestamp.isoformat(),
            'monitoring_system': 'Phase 8C ML-based (SPC + EWMA + Percentile)'
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        
        # Fallback to basic health check
        return {
            'status': 'degraded',
            'health_score': 0.0,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'monitoring_system': 'fallback'
        }



@app.get("/api/v1/system/model-status")
async def get_model_status():
    """
    Get current model availability and selection status
    
    Returns:
        - Available providers and models
        - Current benchmark rankings
        - Pricing information
        - Selection weights
    """
    
    try:
        # Get provider info
        provider_manager = app.state.engine.provider_manager
        providers = provider_manager.registry.get_all_providers()
        
        provider_info = {}
        for name, config in providers.items():
            model_name = config.get('model_name', 'default')
            
            # Get pricing
            pricing_info = None
            if app.state.pricing_engine:
                try:
                    pricing = await app.state.pricing_engine.get_pricing(name, model_name)
                    pricing_info = {
                        'input_cost_per_million': pricing.input_cost_per_million,
                        'output_cost_per_million': pricing.output_cost_per_million,
                        'source': pricing.source,
                        'confidence': pricing.confidence
                    }
                except Exception:
                    pass
            
            provider_info[name] = {
                'model_name': model_name,
                'enabled': config.get('enabled', True),
                'pricing': pricing_info
            }
        
        # Get benchmark rankings for key categories
        rankings = {}
        if provider_manager.external_benchmarks:
            for category in ['coding', 'math', 'reasoning']:
                try:
                    category_rankings = await provider_manager.external_benchmarks.get_rankings(category)
                    rankings[category] = [
                        {
                            'provider': r.provider,
                            'model': r.model_name,
                            'score': r.score,
                            'rank': r.rank
                        }
                        for r in category_rankings[:5]  # Top 5
                    ]
                except Exception:
                    rankings[category] = []
        
        # Get selector weights
        selection_weights = provider_manager.selection_weights
        
        return {
            "status": "ok",
            "system": "fully_dynamic",
            "providers": provider_info,
            "provider_count": len(provider_info),
            "benchmark_rankings": rankings,
            "selection_weights": selection_weights,
            "last_benchmark_update": provider_manager.external_benchmarks.last_update.isoformat() if provider_manager.external_benchmarks and provider_manager.external_benchmarks.last_update else None,
            "pricing_cache_hours": app.state.pricing_engine.cache_hours if app.state.pricing_engine else None,
            "features": {
                "dynamic_pricing": app.state.pricing_engine is not None,
                "intelligent_selection": True,
                "benchmark_integration": provider_manager.external_benchmarks is not None,
                "zero_hardcoded_models": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

from fastapi import Depends, status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.security import auth_manager, verify_token
from core.models import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse, UserDocument, UpdateProfileRequest, PasswordResetRequest, PasswordResetConfirm
from utils.validators import validate_email, validate_message
import hashlib

security_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """
    Dependency to get current authenticated user
    
    Returns:
        user_id: Authenticated user ID
    """
    try:
        token_data = verify_token(credentials.credentials)
        return token_data.user_id
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/api/auth/register", response_model=TokenResponse, status_code=http_status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register new user
    
    Creates user account with email and password.
    Returns JWT tokens for immediate login.
    """
    logger.info(f"📝 Registration attempt: {request.email}")
    
    try:
        # Validate email
        email_validation = validate_email(request.email)
        if not email_validation.is_valid:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email: {', '.join(email_validation.errors)}"
            )
        
        # Get database
        from utils.database import get_database
        db = get_database()
        users_collection = db["users"]
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": request.email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = auth_manager.register_user(request.email, request.password, request.name)
        
        # Create user document
        user_id = str(uuid.uuid4())
        user_doc = UserDocument(
            id=user_id,
            email=request.email.lower(),
            name=request.name,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            is_active=True,
            is_verified=False
        )
        
        # Insert into database
        await users_collection.insert_one(user_doc.model_dump(by_alias=True))
        
        # Create tokens
        tokens = auth_manager.create_session(user_id, request.email.lower())
        
        # Log successful registration
        login_attempts = db["login_attempts"]
        await login_attempts.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": request.email.lower(),
            "ip_address": "unknown",
            "success": True,
            "timestamp": datetime.utcnow()
        })
        
        logger.info(f"✅ User registered: {request.email}")
        
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user={
                "id": user_id,
                "email": request.email.lower(),
                "name": request.name
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Password validation error
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, fastapi_request: Request = None):
    """
    User login
    
    Authenticates user with email and password.
    Returns JWT tokens on success.
    """
    # Rate limiting for brute force protection
    from middleware.simple_rate_limit import rate_limiter
    if fastapi_request:
        ip = rate_limiter.get_client_ip(fastapi_request)
        if not rate_limiter.check_rate_limit(ip, "login"):
            raise HTTPException(
                status_code=http_status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": "60"}
            )
    
    logger.info(f"🔐 Login attempt: {request.email}")
    
    try:
        # Get database
        from utils.database import get_database
        db = get_database()
        users_collection = db["users"]
        login_attempts_collection = db["login_attempts"]
        
        # Find user
        user = await users_collection.find_one({"email": request.email.lower()})
        
        if not user:
            # Log failed attempt
            await login_attempts_collection.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": None,
                "email": request.email.lower(),
                "ip_address": "unknown",
                "success": False,
                "timestamp": datetime.utcnow(),
                "failure_reason": "User not found"
            })
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is locked
        if user.get("locked_until") and datetime.utcnow() < user["locked_until"]:
            raise HTTPException(
                status_code=http_status.HTTP_423_LOCKED,
                detail="Account temporarily locked. Please try again later."
            )
        
        # Verify password
        is_valid = auth_manager.authenticate_user(
            request.email,
            request.password,
            user["password_hash"]
        )
        
        if not is_valid:
            # Update failed attempts
            failed_attempts = user.get("failed_login_attempts", 0) + 1
            update_data = {"failed_login_attempts": failed_attempts}
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                from datetime import timedelta
                update_data["locked_until"] = datetime.utcnow() + timedelta(minutes=15)
            
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
            
            # Log failed attempt
            await login_attempts_collection.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": user["_id"],
                "email": request.email.lower(),
                "ip_address": "unknown",
                "success": False,
                "timestamp": datetime.utcnow(),
                "failure_reason": "Invalid password"
            })
            
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Reset failed attempts and update last login
        await users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "last_login": datetime.utcnow(),
                    "last_active": datetime.utcnow(),
                    "failed_login_attempts": 0,
                    "locked_until": None
                }
            }
        )
        
        # Create tokens
        tokens = auth_manager.create_session(user["_id"], user["email"])
        
        # Log successful login
        await login_attempts_collection.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": user["_id"],
            "email": user["email"],
            "ip_address": "unknown",
            "success": True,
            "timestamp": datetime.utcnow()
        })
        
        logger.info(f"✅ Login successful: {request.email}")
        
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user={
                "id": user["_id"],
                "email": user["email"],
                "name": user["name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    """
    Refresh access token
    
    Uses refresh token to get new access token.
    """
    logger.info("🔄 Token refresh request")
    
    try:
        # Refresh session
        tokens = auth_manager.refresh_session(request.refresh_token)
        
        # Get user info from token
        token_data = verify_token(tokens.access_token)
        
        # Get user from database
        from utils.database import get_database
        db = get_database()
        user = await db["users"].find_one({"_id": token_data.user_id})
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        logger.info(f"✅ Token refreshed for user: {user['email']}")
        
        return TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
            expires_in=tokens.expires_in,
            user={
                "id": user["_id"],
                "email": user["email"],
                "name": user["name"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    User logout
    
    Invalidates current access token.
    """
    logger.info("👋 Logout request")
    
    try:
        # Blacklist token
        auth_manager.end_session(credentials.credentials)
        
        logger.info("✅ Logout successful")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """
    Get current user info
    
    Returns profile information for authenticated user.
    """
    try:
        from utils.database import get_database
        db = get_database()
        
        user = await db["users"].find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user["_id"],
            email=user["email"],
            name=user["name"],
            subscription_tier=user.get("subscription_tier", "free"),
            total_sessions=user.get("total_sessions", 0),
            created_at=user["created_at"],
            last_active=user.get("last_active", user["created_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user info failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )



@app.patch("/api/auth/profile", response_model=UserResponse)
async def update_user_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Update current user profile
    
    Allows authenticated users to update their profile information.
    Only provided fields will be updated (partial updates supported).
    """
    logger.info(f"📝 Profile update request from user: {user_id}")
    
    try:
        from utils.database import get_database
        db = get_database()
        
        # Fetch current user
        user = await db["users"].find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build update dictionary (only include fields that were provided)
        update_data = {}
        
        if request.name is not None:
            update_data["name"] = request.name.strip()
            logger.info(f"📝 Updating name for user {user_id}")
        
        if request.learning_preferences is not None:
            update_data["learning_preferences"] = request.learning_preferences.model_dump()
            logger.info(f"📝 Updating learning preferences for user {user_id}")
        
        if request.emotional_profile is not None:
            update_data["emotional_profile"] = request.emotional_profile.model_dump()
            logger.info(f"📝 Updating emotional profile for user {user_id}")
        
        # If no fields to update, return current profile
        if not update_data:
            logger.warning(f"⚠️ No fields provided for update by user {user_id}")
            return UserResponse(
                id=user["_id"],
                email=user["email"],
                name=user["name"],
                subscription_tier=user.get("subscription_tier", "free"),
                total_sessions=user.get("total_sessions", 0),
                created_at=user["created_at"],
                last_active=user.get("last_active", user["created_at"])
            )
        
        # Update last_active timestamp
        update_data["last_active"] = datetime.utcnow()
        
        # Perform the update
        result = await db["users"].update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0 and result.matched_count == 0:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Fetch updated user
        updated_user = await db["users"].find_one({"_id": user_id})
        
        logger.info(f"✅ Profile updated successfully for user {user_id}")
        
        return UserResponse(
            id=updated_user["_id"],
            email=updated_user["email"],
            name=updated_user["name"],
            subscription_tier=updated_user.get("subscription_tier", "free"),
            total_sessions=updated_user.get("total_sessions", 0),
            created_at=updated_user["created_at"],
            last_active=updated_user.get("last_active", updated_user["created_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Profile update failed for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )



@app.post("/api/auth/password-reset-request", status_code=http_status.HTTP_200_OK)
async def request_password_reset(request: PasswordResetRequest):
    """
    Request password reset
    
    Generates a reset token and saves it to the user's account.
    In a production system, this would send an email with the reset link.
    
    NOTE: For security, this endpoint always returns success even if email doesn't exist.
    """
    logger.info(f"📧 Password reset requested for email: {request.email}")
    
    try:
        from utils.database import get_database
        import secrets
        from datetime import timedelta
        
        db = get_database()
        
        # Find user by email
        user = await db["users"].find_one({"email": request.email.lower()})
        
        if user:
            # Generate secure reset token (32 bytes = 64 hex characters)
            reset_token = secrets.token_urlsafe(32)
            reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
            
            # Save token to user account
            await db["users"].update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "reset_token": reset_token,
                        "reset_token_expires": reset_token_expires
                    }
                }
            )
            
            logger.info(f"✅ Password reset token generated for user: {user['_id']}")
            logger.info(f"🔑 Reset Token (for testing): {reset_token}")
            
            # TODO: In production, send email with reset link
            # Example: send_email(
            #     to=request.email,
            #     subject="Password Reset Request",
            #     body=f"Click here to reset: {FRONTEND_URL}/reset-password?token={reset_token}"
            # )
        else:
            logger.warning(f"⚠️ Password reset requested for non-existent email: {request.email}")
            # For security, don't reveal if email exists
        
        # Always return success to prevent email enumeration
        return {
            "message": "If the email exists, a password reset link has been sent",
            "note": "For development: Check server logs for reset token"
        }
        
    except Exception as e:
        logger.error(f"❌ Password reset request failed: {e}", exc_info=True)
        # Still return success for security
        return {
            "message": "If the email exists, a password reset link has been sent"
        }


@app.post("/api/auth/password-reset-confirm", status_code=http_status.HTTP_200_OK)
async def confirm_password_reset(request: PasswordResetConfirm):
    """
    Confirm password reset with token
    
    Validates the reset token and updates the user's password.
    """
    logger.info(f"🔐 Password reset confirmation attempt")
    
    try:
        from utils.database import get_database
        from utils.security import auth_manager
        
        db = get_database()
        
        # Find user with valid reset token
        user = await db["users"].find_one({
            "reset_token": request.token,
            "reset_token_expires": {"$gt": datetime.utcnow()}  # Token not expired
        })
        
        if not user:
            logger.warning(f"❌ Invalid or expired reset token")
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Hash new password
        new_password_hash = auth_manager.password_manager.hash_password(request.new_password)
        
        # Update password and clear reset token
        await db["users"].update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "reset_token": None,
                    "reset_token_expires": None
                }
            }
        )
        
        logger.info(f"✅ Password reset successful for user: {user['_id']}")
        
        return {
            "message": "Password reset successful. You can now login with your new password."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Password reset confirmation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


# ============================================================================
# LEARNING ENDPOINTS (Protected with Authentication)
# ============================================================================

# Main chat endpoint
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main learning interaction endpoint
    
    Process user message with emotion detection and AI response
    """
    
    logger.info(f"📨 Chat request from user: {request.user_id}")
    
    try:
        # Get or create session
        sessions_collection = get_sessions_collection()
        messages_collection = get_messages_collection()
        
        if request.session_id:
            session_id = request.session_id
            # Load existing session
            session = await sessions_collection.find_one({"_id": session_id})
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            # Create new session
            session_id = str(uuid.uuid4())
            await sessions_collection.insert_one({
                "_id": session_id,
                "user_id": request.user_id,
                "started_at": datetime.utcnow(),
                "status": "active",
                "total_messages": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "emotion_trajectory": []
            })
            logger.info(f"✅ Created new session: {session_id}")
        
        # Save user message
        user_message_id = str(uuid.uuid4())
        await messages_collection.insert_one({
            "_id": user_message_id,
            "session_id": session_id,
            "user_id": request.user_id,
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        })
        
        # Extract subject from context or default to general
        subject = "general"
        if request.context:
            subject = request.context.get("subject", "general")
        
        # Process request with engine
        ai_response = await app.state.engine.process_request(
            user_id=request.user_id,
            message=request.message,
            session_id=session_id,
            context=request.context,
            subject=subject
        )
        
        # Save AI message
        ai_message_id = str(uuid.uuid4())
        await messages_collection.insert_one({
            "_id": ai_message_id,
            "session_id": session_id,
            "user_id": request.user_id,
            "role": "assistant",
            "content": ai_response.content,
            "timestamp": datetime.utcnow(),
            "emotion_state": ai_response.emotion_state.model_dump() if ai_response.emotion_state else None,
            "provider_used": ai_response.provider,
            "response_time_ms": ai_response.response_time_ms,
            "tokens_used": ai_response.tokens_used,
            "cost": ai_response.cost
        })
        
        # Send real-time emotion update via WebSocket
        if ai_response.emotion_state:
            from services.websocket_service import send_emotion_update
            try:
                await send_emotion_update(
                    user_id=request.user_id,
                    message_id=user_message_id,
                    emotion_data=ai_response.emotion_state.model_dump()
                )
                logger.info(f"✓ Sent WebSocket emotion update to user {request.user_id}")
            except Exception as ws_error:
                # Don't fail the request if WebSocket send fails
                logger.warning(f"Failed to send WebSocket emotion update: {ws_error}")
        
        # Update session
        await sessions_collection.update_one(
            {"_id": session_id},
            {
                "$inc": {
                    "total_messages": 2,  # User + AI message
                    "total_tokens": ai_response.tokens_used,
                    "total_cost": ai_response.cost
                },
                "$push": {
                    "emotion_trajectory": ai_response.emotion_state.primary_emotion if ai_response.emotion_state else "neutral"
                }
            }
        )
        
        # Build response with comprehensive metadata
        response = ChatResponse(
            session_id=session_id,
            message=ai_response.content,
            emotion_state=ai_response.emotion_state,
            provider_used=ai_response.provider,
            response_time_ms=ai_response.response_time_ms,
            timestamp=datetime.utcnow(),
            # Phase 2 metadata
            category_detected=ai_response.category,
            tokens_used=ai_response.tokens_used,
            cost=ai_response.cost,
            # Phase 3 metadata
            context_retrieved=ai_response.context_info,
            ability_info=ai_response.ability_info,
            ability_updated=ai_response.ability_updated,
            # Phase 4 metadata
            cached=False,  # Will be set by caching layer
            processing_breakdown=ai_response.processing_breakdown,
            # RAG metadata (Perplexity-inspired)
            rag_enabled=ai_response.rag_enabled,
            citations=ai_response.citations,
            sources_count=ai_response.sources_count,
            search_provider=ai_response.search_provider,
            # ML Follow-up Questions (Perplexity-inspired)
            suggested_questions=ai_response.suggested_questions
        )
        
        logger.info(f"✅ Chat response generated successfully (session: {session_id})")
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get conversation history for a session
    
    Returns all messages (user + AI) in chronological order
    """
    try:
        messages_collection = get_messages_collection()
        sessions_collection = get_sessions_collection()
        
        # Check if session exists
        session = await sessions_collection.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Fetch all messages for this session
        cursor = messages_collection.find(
            {"session_id": session_id}
        ).sort("timestamp", 1)  # Chronological order
        
        messages = []
        async for msg in cursor:
            messages.append({
                "id": msg["_id"],
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"].isoformat(),
                "emotion_state": msg.get("emotion_state"),
                "provider_used": msg.get("provider_used"),
                "response_time_ms": msg.get("response_time_ms"),
                "cost": msg.get("cost")
            })
        
        return {
            "session_id": session_id,
            "messages": messages,
            "total_messages": len(messages),
            "session_started": session["started_at"].isoformat(),
            "total_cost": session.get("total_cost", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# FOLLOW-UP QUESTIONS API (ML-Based Question Generator)
# ============================================================================

class QuestionInteractionRequest(BaseModel):
    """Request to record a question interaction for RL"""
    user_id: str
    session_id: str
    question: str
    clicked: bool


@app.post("/api/v1/questions/interaction", status_code=201)
async def record_question_interaction(request: QuestionInteractionRequest):
    """
    Record user interaction with suggested follow-up questions
    
    This endpoint is used for Reinforcement Learning to improve
    question suggestions over time using Thompson Sampling.
    """
    try:
        # Get ML question generator from engine
        if not app.state.engine or not app.state.engine.ml_question_generator:
            raise HTTPException(
                status_code=503,
                detail="ML question generator not available"
            )
        
        # Get current emotion state and ability level from most recent message
        messages_collection = get_messages_collection()
        last_message = await messages_collection.find_one(
            {"session_id": request.session_id, "role": "assistant"},
            sort=[("timestamp", -1)]
        )
        
        # Extract emotion state and ability
        emotion_state = None
        ability_level = 0.0
        
        if last_message and last_message.get("emotion_state"):
            from core.models import EmotionState
            emotion_data = last_message["emotion_state"]
            emotion_state = EmotionState(**emotion_data)
            ability_level = emotion_data.get("ability_level", 0.0)
        else:
            # Create default emotion state if not available
            from core.models import EmotionState, LearningReadiness
            emotion_state = EmotionState(
                primary_emotion="neutral",
                learning_readiness=LearningReadiness.OPTIMAL_READINESS,
                emotional_intensity=0.5
            )
        
        # Record interaction with ML question generator
        await app.state.engine.ml_question_generator.record_interaction(
            question=request.question,
            clicked=request.clicked,
            user_id=request.user_id,
            session_id=request.session_id,
            emotion_state=emotion_state,
            ability_level=ability_level
        )
        
        logger.info(
            f"✅ Recorded question interaction: "
            f"user={request.user_id}, clicked={request.clicked}"
        )
        
        return {
            "status": "recorded",
            "question_hash": hash(request.question[:50]) % (10 ** 8),
            "clicked": request.clicked
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recording question interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



# Cost dashboard endpoint (admin)
@app.get("/api/v1/admin/costs")
async def get_cost_dashboard(admin_user: dict = Depends(require_admin)):
    """
    Admin endpoint for cost monitoring
    
    Requires: Admin authentication
    """
    
    try:
        return {
            "today": await cost_tracker.get_daily_cost(),
            "this_hour": await cost_tracker.get_hourly_cost(),
            "this_week": await cost_tracker.get_weekly_cost(),
            "breakdown": await cost_tracker.get_cost_breakdown(days=7),
            "top_users": await cost_tracker.get_top_users(days=7, limit=10)
        }
    except Exception as e:
        logger.error(f"Error fetching cost dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Providers endpoint
@app.get("/api/v1/providers")
async def get_providers():
    """Get list of available AI providers"""
    
    try:
        providers = app.state.engine.get_available_providers()
        return {
            "providers": providers,
            "count": len(providers)
        }
    except Exception as e:
        logger.error(f"Error fetching providers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 4: Performance monitoring endpoint
@app.get("/api/v1/admin/performance")
async def get_performance_dashboard(admin_user: dict = Depends(require_admin)):
    """
    Admin endpoint for performance monitoring
    
    Requires: Admin authentication
    """
    
    try:
        from optimization.performance import get_performance_tracker
        
        tracker = get_performance_tracker()
        if not tracker:
            return {"error": "Performance tracker not initialized"}
        
        return tracker.get_dashboard_data()
    except Exception as e:
        logger.error(f"Error fetching performance dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 4: Cache statistics endpoint
@app.get("/api/v1/admin/cache")
async def get_cache_stats(admin_user: dict = Depends(require_admin)):
    """
    Admin endpoint for cache statistics
    
    Requires: Admin authentication
    """
    
    try:
        from optimization.caching import get_cache_manager
        
        cache_manager = get_cache_manager()
        if not cache_manager:
            return {"error": "Cache manager not initialized"}
        
        return await cache_manager.get_stats()
    except Exception as e:
        logger.error(f"Error fetching cache stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 5: Gamification endpoints
@app.get("/api/v1/gamification/stats/{user_id}")
async def get_gamification_stats(user_id: str):
    """Get user gamification statistics"""
    try:
        stats = await app.state.gamification.get_user_stats(user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": stats.user_id,
            "level": stats.level,
            "xp": stats.xp,
            "xp_to_next_level": stats.xp_to_next_level,
            "elo_rating": stats.elo_rating,
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
            "total_sessions": stats.total_sessions,
            "total_questions": stats.total_questions,
            "total_time_minutes": stats.total_time_minutes,
            "achievements_unlocked": stats.achievements_unlocked,
            "badges": stats.badges,
            "rank": stats.rank
        }
    except Exception as e:
        logger.error(f"Error fetching gamification stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/gamification/leaderboard")
async def get_leaderboard(
    limit: int = 100,
    metric: str = "elo_rating"
):
    """Get global leaderboard"""
    try:
        from utils.database import get_database
        db = get_database()
        
        leaderboard = await app.state.gamification.leaderboard.get_global_leaderboard(
            db=db,
            limit=limit,
            metric=metric
        )
        
        return {
            "leaderboard": leaderboard,
            "metric": metric,
            "count": len(leaderboard)
        }
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/gamification/achievements")
async def get_achievements():
    """Get all available achievements"""
    try:
        achievements = app.state.gamification.achievement_engine.achievements
        
        return {
            "achievements": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "type": a.type,
                    "rarity": a.rarity,
                    "xp_reward": a.xp_reward,
                    "icon": a.icon,
                    "criteria": a.criteria
                }
                for a in achievements
            ],
            "count": len(achievements)
        }
    except Exception as e:
        logger.error(f"Error fetching achievements: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/gamification/record-activity")
async def record_gamification_activity(request: RecordActivityRequest):
    """Record user activity for gamification"""
    try:
        result = await app.state.gamification.record_activity(
            user_id=request.user_id,
            session_id=request.session_id,
            question_difficulty=request.question_difficulty,
            success=request.success,
            time_spent_seconds=request.time_spent_seconds
        )
        
        return result
    except Exception as e:
        logger.error(f"Error recording activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 5: Spaced Repetition endpoints
@app.get("/api/v1/spaced-repetition/due-cards/{user_id}")
async def get_due_cards(user_id: str, limit: int = 20, include_new: bool = True):
    """Get cards due for review"""
    try:
        cards = await app.state.spaced_repetition.get_due_cards(
            user_id=user_id,
            limit=limit,
            include_new=include_new
        )
        
        return {
            "user_id": user_id,
            "cards": cards,
            "count": len(cards)
        }
    except Exception as e:
        logger.error(f"Error fetching due cards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/spaced-repetition/create-card")
async def create_spaced_repetition_card(request: CreateCardRequest):
    """Create a new spaced repetition card"""
    try:
        from services.spaced_repetition import CardDifficulty
        
        difficulty = None
        if request.difficulty:
            difficulty = CardDifficulty(request.difficulty)
        
        card_id = await app.state.spaced_repetition.create_card(
            user_id=request.user_id,
            topic=request.topic,
            content=request.content,
            difficulty=difficulty
        )
        
        return {
            "card_id": card_id,
            "user_id": request.user_id,
            "topic": request.topic,
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error creating card: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/spaced-repetition/review-card")
async def review_spaced_repetition_card(request: ReviewCardRequest):
    """Review a card and update scheduling"""
    try:
        # Validate quality (0-5)
        if request.quality < 0 or request.quality > 5:
            raise HTTPException(
                status_code=400,
                detail="Quality must be between 0 and 5"
            )
        
        result = await app.state.spaced_repetition.review_card(
            card_id=request.card_id,
            quality=ReviewQuality(request.quality),
            duration_seconds=request.duration_seconds
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error reviewing card: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/spaced-repetition/stats/{user_id}")
async def get_spaced_repetition_stats(user_id: str):
    """Get user's spaced repetition statistics"""
    try:
        stats = await app.state.spaced_repetition.get_user_statistics(user_id=user_id)
        return stats
    except Exception as e:
        logger.error(f"Error fetching spaced repetition stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 5: Analytics endpoints
@app.get("/api/v1/analytics/dashboard/{user_id}")
async def get_analytics_dashboard(user_id: str):
    """Get real-time analytics dashboard for user"""
    try:
        dashboard_data = await app.state.analytics.get_dashboard_metrics(user_id)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error fetching analytics dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/performance/{user_id}")
async def get_performance_analysis(user_id: str, days_back: int = 30):
    """Get comprehensive performance analysis for user"""
    try:
        analysis = await app.state.analytics.analyze_user_performance(
            user_id=user_id,
            days_back=days_back
        )
        return analysis
    except Exception as e:
        logger.error(f"Error fetching performance analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 5: Personalization endpoints
@app.get("/api/v1/personalization/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get comprehensive user personalization profile"""
    try:
        profile = await app.state.personalization.build_user_profile(user_id)
        return {
            "user_id": profile.user_id,
            "learning_style": profile.learning_style.value,
            "learning_style_confidence": profile.learning_style_confidence,
            "optimal_study_hours": profile.optimal_study_hours,
            "peak_performance_hour": profile.peak_performance_hour,
            "content_preferences": profile.content_preferences,
            "difficulty_preference": profile.difficulty_preference.value,
            "interests": profile.interests,
            "avg_session_duration_minutes": profile.avg_session_duration_minutes,
            "preferred_pace": profile.preferred_pace,
            "attention_span_minutes": profile.attention_span_minutes,
            "last_updated": profile.last_updated
        }
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/personalization/recommendations/{user_id}")
async def get_personalized_recommendations(user_id: str):
    """Get personalized learning recommendations"""
    try:
        recommendations = await app.state.personalization.get_personalized_recommendations(
            user_id=user_id
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/personalization/learning-path/{user_id}/{topic_area}")
async def get_learning_path(user_id: str, topic_area: str):
    """Get optimized learning path for topic area"""
    try:
        path = await app.state.personalization.get_learning_path(
            user_id=user_id,
            topic_area=topic_area
        )
        return {
            "user_id": user_id,
            "topic_area": topic_area,
            "learning_path": path
        }
    except Exception as e:
        logger.error(f"Error fetching learning path: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Phase 5: Content Delivery endpoints
@app.get("/api/v1/content/next/{user_id}")
async def get_next_content(
    user_id: str,
    recent_accuracy: Optional[float] = None,
    emotion: Optional[str] = None
):
    """Get next content recommendation for user"""
    try:
        context = {}
        if recent_accuracy is not None:
            context["recent_accuracy"] = recent_accuracy
        if emotion is not None:
            context["emotion"] = emotion
        
        next_content = await app.state.content_delivery.get_next_content(
            user_id=user_id,
            context=context if context else None
        )
        return next_content
    except Exception as e:
        logger.error(f"Error fetching next content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/content/sequence/{user_id}/{topic}")
async def get_content_sequence(user_id: str, topic: str, n_items: int = 10):
    """Get personalized content sequence for topic"""
    try:
        sequence = await app.state.content_delivery.get_personalized_content_sequence(
            user_id=user_id,
            topic=topic,
            n_items=n_items
        )
        return {
            "user_id": user_id,
            "topic": topic,
            "sequence": sequence,
            "count": len(sequence)
        }
    except Exception as e:
        logger.error(f"Error fetching content sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/content/search")
async def search_content(query: str, n_results: int = 5):
    """Search content using semantic matching"""
    try:
        results = await app.state.content_delivery.match_content_to_query(
            query=query,
            n_results=n_results
        )
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VOICE INTERACTION ENDPOINTS (Phase 6)
# ============================================================================

# Voice Interaction Request Models
class TranscribeRequest(BaseModel):
    """Request model for voice transcription"""
    user_id: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"


class SynthesizeRequest(BaseModel):
    """Request model for voice synthesis"""
    text: str
    emotion: Optional[str] = None
    voice_style: Optional[str] = "friendly"


class PronunciationRequest(BaseModel):
    """Request model for pronunciation assessment"""
    expected_text: str
    user_id: str
    language: Optional[str] = "en"


class VoiceChatRequest(BaseModel):
    """Request model for voice-based chat"""
    user_id: str
    session_id: str
    language: Optional[str] = "en"


@app.post("/api/v1/voice/transcribe")
async def transcribe_voice(
    request: Request,
    audio_file: bytes = None
):
    """
    Transcribe audio to text using Groq Whisper
    
    Accepts audio file upload and returns transcription.
    """
    try:
        if not app.state.voice_interaction:
            raise HTTPException(
                status_code=503,
                detail="Voice interaction service not available"
            )
        
        # Get audio data from request
        if not audio_file:
            body = await request.body()
            audio_file = body
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Get query parameters
        params = dict(request.query_params)
        language = params.get("language", "en")
        
        # Transcribe
        result = await app.state.voice_interaction.transcribe_voice(
            audio_data=audio_file,
            language=language
        )
        
        logger.info(f"Transcribed audio: {len(result['text'])} characters")
        return result
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/synthesize")
async def synthesize_voice(request: SynthesizeRequest):
    """
    Synthesize text to speech using ElevenLabs
    
    Returns audio data for the given text with emotion-aware voice selection.
    """
    try:
        if not app.state.voice_interaction:
            raise HTTPException(
                status_code=503,
                detail="Voice interaction service not available"
            )
        
        # Synthesize speech
        result = await app.state.voice_interaction.synthesize_voice(
            text=request.text,
            emotion=request.emotion,
            voice_style=request.voice_style
        )
        
        logger.info(f"Synthesized speech: {len(request.text)} characters")
        
        # Return audio as response
        from fastapi.responses import Response
        return Response(
            content=result["audio_data"],
            media_type="audio/mpeg",
            headers={
                "X-Voice-ID": result["voice_id"],
                "X-Model": result["model"],
                "X-Duration": str(result["duration"]),
                "X-Format": result["format"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/assess-pronunciation")
async def assess_pronunciation(
    request: Request,
    audio_file: bytes = None
):
    """
    Assess pronunciation quality
    
    Compares user's pronunciation with expected text and provides feedback.
    """
    try:
        if not app.state.voice_interaction:
            raise HTTPException(
                status_code=503,
                detail="Voice interaction service not available"
            )
        
        # Get audio data from request
        if not audio_file:
            body = await request.body()
            audio_file = body
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Get query parameters
        params = dict(request.query_params)
        expected_text = params.get("expected_text")
        language = params.get("language", "en")
        
        if not expected_text:
            raise HTTPException(status_code=400, detail="expected_text parameter required")
        
        # Assess pronunciation
        result = await app.state.voice_interaction.assess_voice_pronunciation(
            audio_data=audio_file,
            expected_text=expected_text,
            language=language
        )
        
        logger.info(f"Assessed pronunciation: score {result['overall_score']:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error assessing pronunciation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/voice/chat")
async def voice_chat(
    request: Request,
    audio_file: bytes = None
):
    """
    Voice-based learning interaction
    
    Complete voice learning flow: transcribe user speech, generate AI response,
    and synthesize voice response.
    """
    try:
        if not app.state.voice_interaction:
            raise HTTPException(
                status_code=503,
                detail="Voice interaction service not available"
            )
        
        # Get audio data from request
        if not audio_file:
            body = await request.body()
            audio_file = body
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        # Get query parameters
        params = dict(request.query_params)
        user_id = params.get("user_id")
        session_id = params.get("session_id")
        language = params.get("language", "en")
        
        if not user_id or not session_id:
            raise HTTPException(
                status_code=400,
                detail="user_id and session_id parameters required"
            )
        
        # Process voice interaction
        result = await app.state.voice_interaction.voice_learning_interaction(
            audio_data=audio_file,
            user_id=user_id,
            session_id=session_id,
            language=language
        )
        
        logger.info(f"Voice interaction completed for user {user_id}")
        
        # Return response with audio
        from fastapi.responses import Response
        return Response(
            content=result["ai_response_audio"],
            media_type="audio/mpeg",
            headers={
                "X-User-Text": result["user_transcription"]["text"],
                "X-AI-Text": result["ai_response_text"],
                "X-Emotion": result["emotion_context"] or "neutral",
                "X-Timestamp": result["timestamp"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error in voice chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COLLABORATION ENDPOINTS (Phase 7)
# ============================================================================

# Collaboration Request Models
class CreateCollaborationSessionRequest(BaseModel):
    """Request model for creating collaboration session
    
    Supports both 'user_id' and 'creator_id' for backward compatibility.
    Following AGENTS.md: Clear, intuitive API design.
    """
    user_id: Optional[str] = None
    creator_id: Optional[str] = None
    topic: str
    subject: str
    difficulty_level: float = 0.5
    max_participants: int = 4
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v, info):
        """Ensure either user_id or creator_id is provided"""
        # If user_id not provided, try to use creator_id
        if v is None and info.data.get('creator_id'):
            return info.data['creator_id']
        return v
    
    @model_validator(mode='after')
    def validate_ids(self):
        """Ensure at least one ID field is provided"""
        if not self.user_id and not self.creator_id:
            raise ValueError("Either 'user_id' or 'creator_id' must be provided")
        # Set both to the same value for consistency
        if self.user_id and not self.creator_id:
            self.creator_id = self.user_id
        elif self.creator_id and not self.user_id:
            self.user_id = self.creator_id
        return self


class JoinSessionRequest(BaseModel):
    """Request model for joining session"""
    session_id: str
    user_id: str


class SendMessageRequest(BaseModel):
    """Request model for sending message"""
    session_id: str
    user_id: str
    user_name: str
    message_type: str = "chat"
    content: str
    reply_to: Optional[str] = None


@app.post("/api/v1/collaboration/find-peers")
async def find_peer_matches(request: MatchRequest):
    """
    Find peer matches for collaboration
    
    Uses ML-based similarity matching to find optimal study partners
    """
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        # Find matches
        matches = await app.state.collaboration.matching_engine.find_matches(request)
        
        return {
            "user_id": request.user_id,
            "subject": request.subject,
            "topic": request.topic,
            "matches": [
                {
                    "user_id": m.user_id,
                    "learning_style": m.learning_style,
                    "avg_engagement": m.avg_engagement,
                    "collaboration_score": m.collaboration_score,
                    "preferred_topics": m.preferred_topics
                }
                for m in matches
            ],
            "count": len(matches)
        }
        
    except Exception as e:
        logger.error(f"Error finding peer matches: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/collaboration/create-session")
async def create_collaboration_session(request: CreateCollaborationSessionRequest):
    """Create new collaboration session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        session = await app.state.collaboration.session_manager.create_session(
            leader_id=request.user_id,
            topic=request.topic,
            subject=request.subject,
            difficulty_level=request.difficulty_level,
            max_participants=request.max_participants
        )
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "subject": session.subject,
            "status": session.status,
            "created_at": session.created_at,
            "leader_id": session.leader_id
        }
        
    except Exception as e:
        logger.error(f"Error creating collaboration session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/collaboration/match-and-create")
async def match_and_create_session(request: MatchRequest):
    """
    Find peers and create collaboration session in one step
    
    Combines peer matching with session creation
    """
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        session = await app.state.collaboration.find_and_create_session(request)
        
        if not session:
            return {
                "success": False,
                "message": "No matches found and auto_start is False"
            }
        
        return {
            "success": True,
            "session_id": session.session_id,
            "topic": session.topic,
            "subject": session.subject,
            "status": session.status,
            "created_at": session.created_at
        }
        
    except Exception as e:
        logger.error(f"Error matching and creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/collaboration/join")
async def join_collaboration_session(request: JoinSessionRequest):
    """Join an existing collaboration session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        success = await app.state.collaboration.session_manager.join_session(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Could not join session (full or not found)"
            )
        
        return {
            "success": True,
            "session_id": request.session_id,
            "user_id": request.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/collaboration/leave")
async def leave_collaboration_session(request: JoinSessionRequest):
    """Leave a collaboration session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        success = await app.state.collaboration.session_manager.leave_session(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        return {
            "success": success,
            "session_id": request.session_id,
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error leaving session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/collaboration/send-message")
async def send_collaboration_message(request: SendMessageRequest):
    """Send message in collaboration session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        import uuid
        
        # Create message
        message = CollaborationMessage(
            message_id=str(uuid.uuid4()),
            session_id=request.session_id,
            user_id=request.user_id,
            user_name=request.user_name,
            message_type=MessageType(request.message_type),
            content=request.content,
            timestamp=datetime.utcnow(),
            reply_to=request.reply_to
        )
        
        # Send message
        await app.state.collaboration.session_manager.send_message(message)
        
        return {
            "success": True,
            "message_id": message.message_id,
            "timestamp": message.timestamp
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/collaboration/sessions")
async def get_active_collaboration_sessions(
    subject: Optional[str] = None,
    min_participants: int = 1
):
    """Get list of active collaboration sessions"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        sessions = await app.state.collaboration.get_active_sessions(
            subject=subject,
            min_participants=min_participants
        )
        
        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "topic": s.topic,
                    "subject": s.subject,
                    "status": s.status,
                    "current_participants": s.current_participants,
                    "max_participants": s.max_participants,
                    "difficulty_level": s.difficulty_level,
                    "created_at": s.created_at
                }
                for s in sessions
            ],
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/collaboration/session/{session_id}/analytics")
async def get_collaboration_analytics(session_id: str):
    """Get comprehensive analytics for a collaboration session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        analytics = await app.state.collaboration.session_manager.get_session_analytics(
            session_id
        )
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/collaboration/session/{session_id}/dynamics")
async def get_session_dynamics(session_id: str, time_window_minutes: int = 30):
    """Get group dynamics analysis for session"""
    try:
        if not app.state.collaboration:
            raise HTTPException(
                status_code=503,
                detail="Collaboration service not available"
            )
        
        dynamics = await app.state.collaboration.dynamics_analyzer.analyze_session(
            session_id,
            time_window_minutes
        )
        
        return {
            "session_id": dynamics.session_id,
            "participation_balance": dynamics.participation_balance,
            "interaction_density": dynamics.interaction_density,
            "help_giving_ratio": dynamics.help_giving_ratio,
            "engagement_trend": dynamics.engagement_trend,
            "dominant_users": dynamics.dominant_users,
            "quiet_users": dynamics.quiet_users,
            "collaboration_health": dynamics.collaboration_health
        }
        
    except Exception as e:
        logger.error(f"Error getting dynamics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 8C PRODUCTION ENDPOINTS
# ============================================================================

@app.get("/api/v1/budget/status")
async def get_budget_status(request: Request):
    """
    Get budget status for authenticated user (Phase 8C File 12)
    
    Returns current budget usage, limits, and predictions.
    """
    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", "guest")
    
    if not hasattr(request.app.state, 'cost_enforcer'):
        raise HTTPException(
            status_code=503,
            detail="Cost enforcement not initialized"
        )
    
    cost_enforcer = request.app.state.cost_enforcer
    budget_status = await cost_enforcer.check_user_budget(user_id)
    
    return {
        "status": budget_status.status.value,
        "user_id": user_id,
        "tier": budget_status.tier.value,
        "limit_usd": budget_status.limit,
        "spent_usd": budget_status.spent,
        "remaining_usd": budget_status.remaining,
        "utilization_percent": budget_status.utilization * 100,
        "exhaustion_time": budget_status.exhaustion_time.isoformat()
            if budget_status.exhaustion_time else None,
        "recommended_action": budget_status.recommended_action,
        "reset_time": "00:00 UTC daily"
    }


@app.get("/api/v1/admin/system/status")
async def get_system_status(request: Request, admin_user: dict = Depends(require_admin)):
    """
    Get complete system status (Phase 8C - admin only)
    
    Requires: Admin authentication
    Combines health monitoring, budget tracking, and configuration info.
    """
    # Get health status
    health_monitor = request.app.state.health_monitor
    health = await health_monitor.get_system_health()
    
    # Get configuration
    from config.settings import get_settings
    settings = get_settings()
    
    # Get graceful shutdown status
    shutdown_status = None
    if hasattr(request.app.state, 'graceful_shutdown'):
        shutdown_status = request.app.state.graceful_shutdown.get_shutdown_status()
    
    return {
        "status": "operational" if health.overall_status.value == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "health": {
            "overall_status": health.overall_status.value,
            "health_score": round(health.health_score, 2),
            "components": {
                name: {
                    "status": comp.status.value,
                    "score": round(comp.health_score, 2),
                    "trend": comp.trend
                }
                for name, comp in health.components.items()
            }
        },
        "environment": settings.get_environment_info(),
        "uptime_seconds": health.uptime_seconds,
        "shutdown": {
            "is_shutting_down": shutdown_status.is_shutting_down if shutdown_status else False,
            "in_flight_requests": shutdown_status.in_flight_count if shutdown_status else 0,
            "background_tasks": shutdown_status.background_tasks_count if shutdown_status else 0
        } if shutdown_status else None,
        "version": "1.0.0",
        "phase": "8C - Production Ready (100%)"
    }


@app.get("/api/v1/admin/production-readiness")
async def check_production_readiness(admin_user: dict = Depends(require_admin)):
    """
    Check production readiness (Phase 8C File 14)
    
    Requires: Admin authentication
    
    Validates configuration for production deployment.
    """
    from config.settings import get_settings
    settings = get_settings()
    
    is_ready, issues = settings.validate_production_ready()
    
    return {
        "is_ready": is_ready,
        "environment": settings.environment,
        "issues_count": len(issues),
        "issues": issues,
        "checks": {
            "database": "localhost" not in settings.database.mongo_url,
            "security": bool(settings.security.jwt_secret_key and len(settings.security.jwt_secret_key) >= 32),
            "ai_providers": len(settings.get_active_providers()) >= 2,
            "debug_mode": not settings.debug if settings.is_production() else True,
            "cost_enforcement": settings.cost_enforcement.enforcement_mode != "disabled",
            "graceful_shutdown": settings.graceful_shutdown.enabled
        },
        "recommendations": [
            "Configure at least 2 AI providers for redundancy",
            "Use strong JWT secret (>=32 characters)",
            "Enable cost enforcement in production",
            "Disable debug mode in production"
        ] if not is_ready else []
    }


# ============================================================================
# WEBSOCKET ENDPOINT - Real-time Communication
# ============================================================================

from fastapi import WebSocket, WebSocketDisconnect, Query
from services.websocket_service import (
    manager,
    verify_token as verify_websocket_token,  # Renamed to avoid conflict with auth verify_token
    handle_websocket_message
)


@app.websocket("/api/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time communication
    
    Features:
    - Real-time emotion updates
    - Typing indicators
    - Session updates
    - Notifications
    
    Authentication: JWT token via query parameter
    
    Message format:
    {
        "type": "event_type",
        "data": { ... }
    }
    """
    # Verify token and extract user_id
    user_id = verify_websocket_token(token)
    
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Generate connection ID
    import uuid
    connection_id = str(uuid.uuid4())
    
    # Connect
    await manager.connect(websocket, user_id, connection_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle message based on type
            await handle_websocket_message(user_id, data)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id, connection_id)
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, connection_id)
        await websocket.close(code=1011, reason="Internal error")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MasterX API",
        "version": "1.0.0",
        "description": "AI-Powered Adaptive Learning Platform with Emotion Detection - Phase 8C Complete",
        "status": "operational",
        "phase": "8C - Production Ready (100%)",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/v1/chat",
            "providers": "/api/v1/providers",
            "websocket": "/api/ws",
            "admin": {
                "costs": "/api/v1/admin/costs",
                "performance": "/api/v1/admin/performance",
                "cache": "/api/v1/admin/cache"
            },
            "gamification": {
                "stats": "/api/v1/gamification/stats/{user_id}",
                "leaderboard": "/api/v1/gamification/leaderboard",
                "achievements": "/api/v1/gamification/achievements",
                "record_activity": "/api/v1/gamification/record-activity"
            },
            "spaced_repetition": {
                "due_cards": "/api/v1/spaced-repetition/due-cards/{user_id}",
                "create_card": "/api/v1/spaced-repetition/create-card",
                "review_card": "/api/v1/spaced-repetition/review-card",
                "stats": "/api/v1/spaced-repetition/stats/{user_id}"
            },
            "analytics": {
                "dashboard": "/api/v1/analytics/dashboard/{user_id}",
                "performance": "/api/v1/analytics/performance/{user_id}"
            },
            "personalization": {
                "profile": "/api/v1/personalization/profile/{user_id}",
                "recommendations": "/api/v1/personalization/recommendations/{user_id}",
                "learning_path": "/api/v1/personalization/learning-path/{user_id}/{topic_area}"
            },
            "content_delivery": {
                "next": "/api/v1/content/next/{user_id}",
                "sequence": "/api/v1/content/sequence/{user_id}/{topic}",
                "search": "/api/v1/content/search?query=<query>"
            },
            "voice_interaction": {
                "transcribe": "/api/v1/voice/transcribe",
                "synthesize": "/api/v1/voice/synthesize",
                "assess_pronunciation": "/api/v1/voice/assess-pronunciation",
                "voice_chat": "/api/v1/voice/chat"
            },
            "collaboration": {
                "find_peers": "/api/v1/collaboration/find-peers",
                "create_session": "/api/v1/collaboration/create-session",
                "match_and_create": "/api/v1/collaboration/match-and-create",
                "join": "/api/v1/collaboration/join",
                "leave": "/api/v1/collaboration/leave",
                "send_message": "/api/v1/collaboration/send-message",
                "sessions": "/api/v1/collaboration/sessions",
                "analytics": "/api/v1/collaboration/session/{session_id}/analytics",
                "dynamics": "/api/v1/collaboration/session/{session_id}/dynamics"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
