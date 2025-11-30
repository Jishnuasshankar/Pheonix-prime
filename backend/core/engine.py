"""
MasterX Engine - Main Orchestrator
Following specifications from 5.DEVELOPMENT_HANDOFF_GUIDE.md

Phase 3: COMPLETE INTEGRATION
- Process user message with emotion detection
- Context-aware conversation management
- Adaptive difficulty based on performance
- Intelligent AI provider selection
- Real-time ability estimation
- Flow state optimization
"""

import logging
import time
import uuid
from typing import Optional, List
from datetime import datetime

from core.models import (
    AIResponse, EmotionState, LearningReadiness, 
    Message, MessageRole, ContextInfo, AbilityInfo
)
from core.ai_providers import ProviderManager
from core.context_manager import ContextManager
from core.adaptive_learning import AdaptiveLearningEngine, PerformanceMetrics as AdaptivePerformanceMetrics
from services.emotion.emotion_engine import EmotionEngine, EmotionEngineConfig
from services.rag_engine import RAGEngine, create_rag_engine
from services.ml_question_generator import MLQuestionGenerator, create_ml_question_generator
from utils.errors import MasterXError
from utils.cost_tracker import cost_tracker
from utils.database import get_database

# PHASE 4: Deep Thinking Integration
from core.reasoning import (
    MetacognitiveController,
    DualProcessEngine,
    ThinkingMode,
    ReasoningChain,
    ReasoningStep
)

logger = logging.getLogger(__name__)


class MasterXEngine:
    """
    Main orchestrator for MasterX learning platform
    
    PHASE 3 COMPLETE - Full Intelligence Integration:
    - Emotion detection (18 emotions, BERT/RoBERTa)
    - Multi-AI provider routing (dynamic benchmarking)
    - Context management (conversation memory, semantic search)
    - Adaptive learning (IRT, cognitive load, flow state)
    - Performance tracking (ability estimation, velocity)
    """
    
    # Response size categories (model-independent)
    RESPONSE_SIZES = {
        'minimal': 400,          # Very quick answers
        'concise': 800,          # Short answers
        'standard': 1500,        # Normal responses
        'detailed': 2500,        # Explanations with examples
        'comprehensive': 3500,   # Complex topics, multiple examples
        'extensive': 4500        # Maximum detail for struggling students
    }
    
    def __init__(self, model_max_tokens: int = 4096):
        """
        Initialize MasterX engine with all intelligence components
        
        Args:
            model_max_tokens: Maximum tokens your model can generate (default: 4096)
        """
        self.provider_manager = ProviderManager()
        self.emotion_engine = EmotionEngine(config=EmotionEngineConfig())
        
        # Phase 3: Initialize context and adaptive learning components
        # Database will be set during server startup
        self.context_manager = None
        self.adaptive_engine = None
        self.rag_engine = None  # RAG engine for real-time knowledge
        self.ml_question_generator = None  # ML-based question generator (Perplexity-grade)
        
        # Phase 4: Deep Thinking components
        self.metacognitive_controller = None  # Reasoning orchestrator
        self.reasoning_enabled = False  # Enable/disable reasoning per request
        
        self._db_initialized = False
        
        # Token management
        self.model_max_tokens = model_max_tokens
        # Use 90% of max as safe upper limit
        self.safe_max = int(model_max_tokens * 0.90)
        
        logger.info("✅ MasterXEngine initialized (Phase 4: Deep Thinking Ready)")
    
    async def initialize_intelligence_layer(self, db):
        """
        Initialize Phase 3 & 4 intelligence components with database
        
        Args:
            db: MongoDB database instance
        """
        if not self._db_initialized:
            try:
                # Initialize context manager
                self.context_manager = ContextManager(
                    db=db,
                    max_context_tokens=8000,
                    short_term_memory_size=20
                )
                
                # Initialize adaptive learning engine
                self.adaptive_engine = AdaptiveLearningEngine(db=db)
                
                # Initialize RAG engine (Perplexity-inspired)
                self.rag_engine = await create_rag_engine()
                
                # Initialize ML-based question generator (Perplexity-grade)
                self.ml_question_generator = await create_ml_question_generator(
                    provider_manager=self.provider_manager,
                    db=db
                )
                
                # Phase 4: Initialize Deep Thinking components
                self.metacognitive_controller = MetacognitiveController(
                    db=db, 
                    provider_manager=self.provider_manager
                )
                
                # Ensure collections exist
                await db.create_collection("question_interactions", check_exists=False)
                await db.question_interactions.create_index("question_hash")
                await db.question_interactions.create_index("timestamp")
                
                # Phase 4: Reasoning sessions collection
                await db.create_collection("reasoning_sessions", check_exists=False)
                await db.reasoning_sessions.create_index("user_id")
                await db.reasoning_sessions.create_index("session_id")
                await db.reasoning_sessions.create_index("timestamp")
                
                self._db_initialized = True
                logger.info("✅ Intelligence layer initialized (Phase 4: Full System with Deep Thinking)")
            except Exception as e:
                logger.error(f"Failed to initialize intelligence layer: {e}")
                raise
    
    async def process_request(
        self,
        user_id: str,
        message: str,
        session_id: str,
        context: Optional[dict] = None,
        subject: str = "general"
    ) -> AIResponse:
        """
        Process user request with full Phase 3 intelligence
        
        PHASE 3 COMPLETE FLOW:
        1. Retrieve conversation context (semantic memory)
        2. Analyze emotion (18 emotions, learning readiness)
        3. Get ability estimate and recommend difficulty
        4. Detect category and select best AI provider
        5. Generate context-aware, difficulty-adapted response
        6. Store message with embeddings
        7. Update ability based on interaction
        
        Args:
            user_id: User identifier
            message: User message
            session_id: Session identifier
            context: Additional context (optional)
            subject: Learning subject/topic
        
        Returns:
            AIResponse with emotion, context, and difficulty information
        """
        
        start_time = time.time()
        
        try:
            # Ensure intelligence layer is initialized
            if not self._db_initialized:
                logger.warning("Intelligence layer not initialized, using basic mode")
                return await self._process_basic(user_id, message, session_id, context)
            
            # ====================================================================
            # PHASE 3 STEP 1: RETRIEVE CONVERSATION CONTEXT
            # ====================================================================
            logger.info(f"🧠 Retrieving conversation context for session {session_id}...")
            context_start = time.time()
            
            conversation_context = await self.context_manager.get_context(
                session_id=session_id,
                include_semantic=True,
                semantic_query=message
            )
            
            recent_messages = conversation_context.get('recent_messages', [])
            relevant_messages = conversation_context.get('relevant_messages', [])
            
            context_time_ms = (time.time() - context_start) * 1000
            logger.info(
                f"✅ Context retrieved: {len(recent_messages)} recent, "
                f"{len(relevant_messages)} relevant ({context_time_ms:.0f}ms)"
            )
            
            # ====================================================================
            # PHASE 3 STEP 2: ANALYZE EMOTION
            # ====================================================================
            logger.info(f"📊 Analyzing emotion for message: {message[:50]}...")
            emotion_start = time.time()
            
            emotion_result = await self.emotion_engine.analyze_emotion(
                text=message,
                user_id=user_id,
                session_id=session_id,
                interaction_context=context
            )
            
            emotion_time_ms = (time.time() - emotion_start) * 1000
            logger.info(f"✅ Emotion detected: {emotion_result.primary_emotion} ({emotion_time_ms:.0f}ms)")
            
            # Map EmotionCore LearningReadiness to Models LearningReadiness
            readiness_map = {
                "optimal": LearningReadiness.OPTIMAL_READINESS,
                "good": LearningReadiness.HIGH_READINESS,
                "moderate": LearningReadiness.MODERATE_READINESS,
                "low": LearningReadiness.LOW_READINESS,
                "blocked": LearningReadiness.NOT_READY
            }
            
            # Create EmotionState for response
            emotion_state = EmotionState(
                primary_emotion=emotion_result.primary_emotion,
                arousal=emotion_result.pad_dimensions.arousal,
                valence=emotion_result.pad_dimensions.pleasure,
                learning_readiness=readiness_map.get(
                    emotion_result.learning_readiness,
                    LearningReadiness.MODERATE_READINESS
                )
            )
            
            # ====================================================================
            # PHASE 3 STEP 3: ADAPTIVE DIFFICULTY RECOMMENDATION
            # ====================================================================
            logger.info(f"🎯 Calculating optimal difficulty for {user_id}/{subject}...")
            difficulty_start = time.time()
            
            # Get current ability
            ability = await self.adaptive_engine.ability_estimator.get_ability(
                user_id=user_id,
                subject=subject
            )
            
            # Recommend difficulty based on ability and emotion
            difficulty_level = await self.adaptive_engine.recommend_difficulty(
                user_id=user_id,
                subject=subject,
                emotion_state=emotion_state,
                recent_performance=None  # Will be calculated from context
            )
            
            difficulty_time_ms = (time.time() - difficulty_start) * 1000
            logger.info(
                f"✅ Difficulty recommended: {difficulty_level.label} "
                f"({difficulty_level.value:.2f}, ability: {ability:.2f}) "
                f"({difficulty_time_ms:.0f}ms)"
            )
            
            # ====================================================================
            # PHASE 3 STEP 3.5: DETECT CATEGORY (needed for RAG decision)
            # ====================================================================
            category = self.provider_manager.detect_category_from_message(
                message, 
                emotion_state
            )
            logger.info(f"📂 Detected category: {category}")
            
            # =========================================
            # PHASE 3.5: RAG - REAL-TIME WEB KNOWLEDGE 
            # =========================================
            rag_context = None
            rag_time_ms = 0.0
            
            # Determine if RAG should be enabled for this query
            enable_rag = self._should_enable_rag(message, category)
            
            if enable_rag and self.rag_engine:
                logger.info(f"🌐 Augmenting with real-time web knowledge...")
                rag_start = time.time()
                
                try:
                    rag_context = await self.rag_engine.augment_query(
                        query=message,
                        emotion_state=emotion_state,
                        ability_level=ability,
                        enable_search=True
                    )
                    
                    rag_time_ms = (time.time() - rag_start) * 1000
                    
                    if rag_context:
                        logger.info(
                            f"✅ RAG complete: {len(rag_context.sources)} sources, "
                            f"{rag_context.provider_used.value} provider "
                            f"({rag_time_ms:.0f}ms)"
                        )
                    else:
                        logger.info("⚠️  RAG returned no results, proceeding without")
                except Exception as e:
                    logger.warning(f"⚠️  RAG failed (non-critical): {e}")
                    rag_context = None
            
            # ====================================================================
            # PHASE 3 STEP 4: INTELLIGENT PROVIDER SELECTION
            # ====================================================================
            logger.info(f"🤖 Selecting best AI provider...")
            ai_start = time.time()
            
            # Select best provider for this category
            selected_provider = await self.provider_manager.select_best_provider_for_category(
                category,
                emotion_state
            )
            
            # ====================================================================
            # PHASE 3 STEP 5: GENERATE CONTEXT-AWARE RESPONSE (with RAG)
            # ====================================================================
            # Enhance prompt with emotion, context, difficulty, and RAG
            enhanced_prompt = self._enhance_prompt_phase3(
                message=message,
                emotion_result=emotion_result,
                recent_messages=recent_messages,
                relevant_messages=relevant_messages,
                difficulty_level=difficulty_level,
                ability=ability,
                rag_context=rag_context  # Add RAG sources to prompt
            )
            
            # Dynamic token allocation based on context
            token_limit = self.calculate_token_limit(message, emotion_result)
            
            response = await self.provider_manager.generate(
                prompt=enhanced_prompt,
                provider_name=selected_provider,
                max_tokens=token_limit
            )
            
            ai_time_ms = (time.time() - ai_start) * 1000
            logger.info(f"✅ AI response generated ({ai_time_ms:.0f}ms)")
            
            # ====================================================================
            # PHASE 3 STEP 6: STORE MESSAGES WITH EMBEDDINGS
            # ====================================================================
            logger.info(f"💾 Storing messages with embeddings...")
            storage_start = time.time()
            
            # Store user message
            user_message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.USER,
                content=message,
                timestamp=datetime.utcnow(),
                emotion_state=emotion_state
            )
            
            await self.context_manager.add_message(
                session_id=session_id,
                message=user_message,
                generate_embedding=True
            )
            
            # Store AI response message
            ai_message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=response.content,
                timestamp=datetime.utcnow(),
                emotion_state=emotion_state,
                provider_used=response.provider,
                response_time_ms=response.response_time_ms,
                tokens_used=response.tokens_used,
                cost=response.cost
            )
            
            await self.context_manager.add_message(
                session_id=session_id,
                message=ai_message,
                generate_embedding=True
            )
            
            storage_time_ms = (time.time() - storage_start) * 1000
            logger.info(f"✅ Messages stored with embeddings ({storage_time_ms:.0f}ms)")
            
            # ====================================================================
            # PHASE 3 STEP 7: UPDATE ABILITY ESTIMATE
            # ====================================================================
            # Infer performance from interaction
            # (In full system, this would be based on correctness checks)
            # For now, use emotion and engagement as proxy
            interaction_success = self._infer_success_from_emotion(emotion_state)
            
            await self.adaptive_engine.ability_estimator.update_ability(
                user_id=user_id,
                subject=subject,
                item_difficulty=difficulty_level.value,
                result=interaction_success
            )
            
            # ====================================================================
            # FINALIZE RESPONSE WITH COMPREHENSIVE METADATA
            # ====================================================================
            response.emotion_state = emotion_state
            response.response_time_ms = (time.time() - start_time) * 1000
            
            # Track costs
            if response.tokens_used > 0:
                cost = await cost_tracker.track_request(
                    provider=response.provider,
                    model=response.model_name,
                    input_tokens=len(message.split()) * 2,
                    output_tokens=response.tokens_used,
                    user_id=user_id,
                    category=category
                )
                response.cost = cost
            
            # Add Phase 2 metadata
            response.category = category
            
            # Add Phase 3 metadata - Context Info
            response.context_info = ContextInfo(
                recent_messages_count=len(recent_messages),
                relevant_messages_count=len(relevant_messages),
                has_context=len(recent_messages) > 0 or len(relevant_messages) > 0,
                retrieval_time_ms=context_time_ms
            )
            
            # Add Phase 3 metadata - Ability Info
            response.ability_info = AbilityInfo(
                ability_level=ability,
                recommended_difficulty=difficulty_level.value,
                cognitive_load=emotion_result.pad_dimensions.arousal,  # Using arousal as proxy
                flow_state_score=None  # Could be calculated from emotion trajectory
            )
            
            # Mark that ability was updated
            response.ability_updated = True
            
            # Add Phase 4 metadata - Processing breakdown
            response.processing_breakdown = {
                "context_retrieval_ms": context_time_ms,
                "emotion_detection_ms": emotion_time_ms,
                "difficulty_calculation_ms": difficulty_time_ms,
                "rag_search_ms": rag_time_ms,  # RAG timing
                "ai_generation_ms": ai_time_ms,
                "storage_ms": storage_time_ms,
                "total_ms": (time.time() - start_time) * 1000
            }
            
            # Add RAG metadata 
            # Store as custom attributes for server to access
            if rag_context:
                response.rag_enabled = True
                response.citations = rag_context.citations
                response.sources_count = len(rag_context.sources)
                response.search_provider = rag_context.provider_used.value
            else:
                response.rag_enabled = False
                response.citations = None
                response.sources_count = 0
                response.search_provider = None
            
            # ====================================================================
            # GENERATE FOLLOW-UP QUESTIONS (ML)
            # ====================================================================
            logger.info(f"💡 Generating ML-based follow-up questions...")
            followup_start = time.time()
            
            try:
                if self.ml_question_generator:
                    response.suggested_questions = await self.ml_question_generator.generate_follow_ups(
                        user_message=message,
                        ai_response=response.content,
                        emotion_state=emotion_state,
                        ability_level=ability,
                        category=category,
                        recent_messages=recent_messages,
                        max_questions=5
                    )
                else:
                    logger.warning("⚠️  ML question generator not initialized")
                    response.suggested_questions = []
                
                followup_time_ms = (time.time() - followup_start) * 1000
                logger.info(
                    f"✅ Generated {len(response.suggested_questions)} ML-based follow-up questions "
                    f"({followup_time_ms:.0f}ms)"
                )
            except Exception as e:
                logger.warning(f"⚠️  Failed to generate follow-up questions: {e}")
                response.suggested_questions = []
            
            total_time_ms = (time.time() - start_time) * 1000
            logger.info(
                f"✅ Request processed in {total_time_ms:.0f}ms "
                f"(context: {context_time_ms:.0f}ms, "
                f"emotion: {emotion_time_ms:.0f}ms, "
                f"difficulty: {difficulty_time_ms:.0f}ms, "
                f"AI: {ai_time_ms:.0f}ms, "
                f"storage: {storage_time_ms:.0f}ms)"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}", exc_info=True)
            raise MasterXError(
                f"Failed to process request: {str(e)}",
                details={
                    'user_id': user_id,
                    'session_id': session_id,
                    'error': str(e)
                }
            )
    
    async def process_request_with_reasoning(
        self,
        user_id: str,
        message: str,
        session_id: str,
        context: Optional[dict] = None,
        subject: str = "general",
        enable_reasoning: bool = True,
        thinking_mode: Optional[str] = None,
        max_reasoning_depth: Optional[int] = None
    ) -> dict:
        """
        PHASE 4: Process request with Deep Thinking reasoning
        
        Enhanced version of process_request that includes:
        1. Thinking mode selection (System 1 vs System 2)
        2. Dynamic token budget allocation
        3. MCTS-based reasoning chain generation
        4. Visible step-by-step thinking process
        5. Reasoning-enhanced AI response
        
        Flow:
        1-2. Same as process_request (context + emotion)
        3. Select thinking mode (System 1/2/Hybrid)
        4. Allocate token budget (reasoning vs response)
        5. Generate reasoning chain (if System 2)
        6. Enhanced AI response with reasoning context
        7. Store reasoning session
        8. Return response with reasoning chain
        
        Args:
            user_id: User identifier
            message: User message
            session_id: Session identifier
            context: Additional context (optional)
            subject: Learning subject/topic
            enable_reasoning: Enable deep thinking (default: True)
        
        Returns:
            AIResponse with reasoning chain
        """
        
        start_time = time.time()
        
        try:
            # Ensure intelligence layer is initialized
            if not self._db_initialized or not self.metacognitive_controller:
                logger.warning("Deep Thinking not initialized, falling back to standard processing")
                return await self.process_request(user_id, message, session_id, context, subject)
            
            # ====================================================================
            # PHASE 4 STEP 1-2: STANDARD PROCESSING (Context + Emotion)
            # ====================================================================
            logger.info(f"🧠 Phase 4: Processing with Deep Thinking enabled={enable_reasoning}")
            
            # Get context (same as Phase 3)
            context_start = time.time()
            conversation_context = await self.context_manager.get_context(
                session_id=session_id,
                include_semantic=True,
                semantic_query=message
            )
            
            recent_messages = conversation_context.get('recent_messages', [])
            relevant_messages = conversation_context.get('relevant_messages', [])
            context_time_ms = (time.time() - context_start) * 1000
            
            # Emotion analysis (same as Phase 3)
            emotion_start = time.time()
            emotion_result = await self.emotion_engine.analyze_emotion(
                text=message,
                user_id=user_id,
                session_id=session_id,
                interaction_context=context
            )
            emotion_time_ms = (time.time() - emotion_start) * 1000
            
            # Map to LearningReadiness
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
            
            # Adaptive difficulty (same as Phase 3)
            difficulty_start = time.time()
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
            difficulty_time_ms = (time.time() - difficulty_start) * 1000
            
            # Cognitive load from emotion analysis (ensure float type)
            try:
                cognitive_load = float(emotion_result.cognitive_load) if hasattr(emotion_result, 'cognitive_load') and emotion_result.cognitive_load is not None else 0.5
                cognitive_load = max(0.0, min(1.0, cognitive_load))  # Clamp to [0, 1]
            except (TypeError, ValueError):
                logger.warning(f"⚠️ Invalid cognitive_load from emotion analysis, using default 0.5")
                cognitive_load = 0.5
            
            # ====================================================================
            # PHASE 4 STEP 3: SELECT THINKING MODE
            # ====================================================================
            reasoning_chain = None
            thinking_mode = None
            budget = None
            reasoning_time_ms = 0.0
            
            if enable_reasoning:
                logger.info(f"🤔 Selecting thinking mode...")
                thinking_start = time.time()
                
                # Select thinking mode (System 1 vs System 2)
                thinking_decision = await self.metacognitive_controller.select_thinking_mode(
                    query=message,
                    emotion_state=emotion_state,
                    cognitive_load=cognitive_load,
                    learning_readiness=emotion_state.learning_readiness
                )
                
                thinking_mode = thinking_decision.mode
                logger.info(
                    f"✅ Thinking mode selected: {thinking_mode.value} "
                    f"(confidence: {thinking_decision.confidence:.2f})"
                )
                
                # ====================================================================
                # PHASE 4 STEP 4: ALLOCATE TOKEN BUDGET
                # ====================================================================
                logger.info(f"💰 Allocating token budget...")
                
                budget = await self.metacognitive_controller.allocate_budget(
                    query=message,
                    emotion_state=emotion_state,
                    cognitive_load=cognitive_load,
                    learning_readiness=emotion_state.learning_readiness
                )
                
                logger.info(
                    f"✅ Budget allocated: {budget.total_tokens} tokens "
                    f"(reasoning: {budget.reasoning_tokens}, response: {budget.response_tokens})"
                )
                
                # ====================================================================
                # PHASE 4 STEP 5: GENERATE REASONING CHAIN (if System 2)
                # ====================================================================
                if thinking_mode in [ThinkingMode.SYSTEM2, ThinkingMode.HYBRID]:
                    logger.info(f"🧠 Generating reasoning chain...")
                    
                    # Get AI provider for reasoning generation
                    category = self.provider_manager.detect_category_from_message(message, emotion_state)
                    selected_provider = await self.provider_manager.select_best_provider_for_category(
                        category, emotion_state
                    )
                    provider_client = self.provider_manager.get_provider_client(selected_provider)
                    
                    reasoning_chain = await self.metacognitive_controller.generate_reasoning_chain(
                        query=message,
                        emotion_state=emotion_state,
                        cognitive_load=cognitive_load,
                        thinking_mode=thinking_mode,
                        token_budget=budget,
                        provider_client=provider_client
                    )
                    
                    reasoning_time_ms = (time.time() - thinking_start) * 1000
                    logger.info(
                        f"✅ Reasoning chain generated: {len(reasoning_chain.steps)} steps "
                        f"({reasoning_time_ms:.0f}ms)"
                    )
                else:
                    logger.info(f"⚡ System 1 mode: Skipping explicit reasoning chain")
                    reasoning_time_ms = (time.time() - thinking_start) * 1000
            
            # ====================================================================
            # PHASE 4 STEP 6: ENHANCED AI RESPONSE
            # ====================================================================
            logger.info(f"🤖 Generating reasoning-enhanced response...")
            ai_start = time.time()
            
            # Detect category and select provider
            category = self.provider_manager.detect_category_from_message(message, emotion_state)
            selected_provider = await self.provider_manager.select_best_provider_for_category(
                category, emotion_state
            )
            
            # RAG augmentation (if applicable)
            rag_context = None
            enable_rag = self._should_enable_rag(message, category)
            
            if enable_rag and self.rag_engine:
                try:
                    rag_context = await self.rag_engine.augment_query(
                        query=message,
                        emotion_state=emotion_state,
                        ability_level=ability,
                        enable_search=True
                    )
                except Exception as e:
                    logger.warning(f"⚠️  RAG failed: {e}")
            
            # Enhanced prompt with reasoning context
            enhanced_prompt = self._enhance_prompt_with_reasoning(
                message=message,
                emotion_result=emotion_result,
                recent_messages=recent_messages,
                relevant_messages=relevant_messages,
                difficulty_level=difficulty_level,
                ability=ability,
                reasoning_chain=reasoning_chain,
                rag_context=rag_context
            )
            
            # Token limit (use response budget if reasoning enabled)
            token_limit = budget.response_tokens if budget else self.calculate_token_limit(message, emotion_result)
            
            response = await self.provider_manager.generate(
                prompt=enhanced_prompt,
                provider_name=selected_provider,
                max_tokens=token_limit
            )
            
            ai_time_ms = (time.time() - ai_start) * 1000
            logger.info(f"✅ AI response generated ({ai_time_ms:.0f}ms)")
            
            # ====================================================================
            # PHASE 4 STEP 7: STORE MESSAGES & REASONING SESSION
            # ====================================================================
            logger.info(f"💾 Storing messages and reasoning session...")
            storage_start = time.time()
            
            # Store user message
            user_message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.USER,
                content=message,
                timestamp=datetime.utcnow(),
                emotion_state=emotion_state
            )
            
            await self.context_manager.add_message(
                session_id=session_id,
                message=user_message,
                generate_embedding=True
            )
            
            # Store AI response message
            ai_message = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=response.content,
                timestamp=datetime.utcnow(),
                emotion_state=emotion_state,
                provider_used=response.provider,
                response_time_ms=response.response_time_ms,
                tokens_used=response.tokens_used,
                cost=response.cost
            )
            
            await self.context_manager.add_message(
                session_id=session_id,
                message=ai_message,
                generate_embedding=True
            )
            
            # Store reasoning session (if generated)
            if reasoning_chain and self.metacognitive_controller.db:
                try:
                    reasoning_doc = {
                        'id': reasoning_chain.id,
                        'user_id': user_id,
                        'session_id': session_id,
                        'query': message,
                        'thinking_mode': thinking_mode.value if thinking_mode else 'system1',
                        'steps': [
                            {
                                'step_number': step.step_number,
                                'content': step.content,
                                'strategy': step.strategy.value,
                                'confidence': step.confidence,
                                'timestamp': step.timestamp.isoformat()
                            }
                            for step in reasoning_chain.steps
                        ],
                        'conclusion': reasoning_chain.conclusion,
                        'total_confidence': reasoning_chain.total_confidence,
                        'processing_time_ms': reasoning_chain.processing_time_ms,
                        'complexity_score': reasoning_chain.complexity_score,
                        'token_budget_used': reasoning_chain.token_budget_used,
                        'token_budget_allocated': reasoning_chain.token_budget_allocated,
                        'emotion_state': {
                            'primary_emotion': emotion_state.primary_emotion,
                            'arousal': emotion_state.arousal,
                            'valence': emotion_state.valence,
                            'learning_readiness': emotion_state.learning_readiness.value
                        },
                        'timestamp': datetime.utcnow()
                    }
                    
                    await self.metacognitive_controller.db.reasoning_sessions.insert_one(reasoning_doc)
                    logger.info(f"✅ Reasoning session stored: {reasoning_chain.id}")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to store reasoning session: {e}")
            
            storage_time_ms = (time.time() - storage_start) * 1000
            logger.info(f"✅ Storage complete ({storage_time_ms:.0f}ms)")
            
            # Update ability estimate
            interaction_success = self._infer_success_from_emotion(emotion_state)
            await self.adaptive_engine.ability_estimator.update_ability(
                user_id=user_id,
                subject=subject,
                item_difficulty=difficulty_level.value,
                result=interaction_success
            )
            
            # ====================================================================
            # PHASE 4 STEP 8: FINALIZE RESPONSE WITH REASONING
            # ====================================================================
            response.emotion_state = emotion_state
            response.response_time_ms = (time.time() - start_time) * 1000
            
            # Track costs
            if response.tokens_used > 0:
                cost = await cost_tracker.track_request(
                    provider=response.provider,
                    model=response.model_name,
                    input_tokens=len(message.split()) * 2,
                    output_tokens=response.tokens_used,
                    user_id=user_id,
                    category=category
                )
                response.cost = cost
            
            # Add metadata
            response.category = category
            response.context_info = ContextInfo(
                recent_messages_count=len(recent_messages),
                relevant_messages_count=len(relevant_messages),
                has_context=len(recent_messages) > 0 or len(relevant_messages) > 0,
                retrieval_time_ms=context_time_ms
            )
            
            response.ability_info = AbilityInfo(
                ability_level=ability,
                recommended_difficulty=difficulty_level.value,
                cognitive_load=cognitive_load,
                flow_state_score=None
            )
            
            response.ability_updated = True
            
            # Phase 4: Add reasoning metadata
            response.reasoning_enabled = enable_reasoning
            if reasoning_chain:
                response.reasoning_chain = reasoning_chain.to_dict_for_frontend()
                response.thinking_mode = thinking_mode.value if thinking_mode else None
            else:
                response.reasoning_chain = None
                response.thinking_mode = 'system1' if enable_reasoning else None
            
            # Processing breakdown
            response.processing_breakdown = {
                "context_retrieval_ms": context_time_ms,
                "emotion_detection_ms": emotion_time_ms,
                "difficulty_calculation_ms": difficulty_time_ms,
                "reasoning_generation_ms": reasoning_time_ms,
                "ai_generation_ms": ai_time_ms,
                "storage_ms": storage_time_ms,
                "total_ms": response.response_time_ms
            }
            
            # RAG metadata
            if rag_context:
                response.rag_enabled = True
                response.citations = rag_context.citations
                response.sources_count = len(rag_context.sources)
                response.search_provider = rag_context.provider_used.value
            else:
                response.rag_enabled = False
                response.citations = None
                response.sources_count = 0
                response.search_provider = None
            
            # Generate follow-up questions
            try:
                if self.ml_question_generator:
                    response.suggested_questions = await self.ml_question_generator.generate_follow_ups(
                        user_message=message,
                        ai_response=response.content,
                        emotion_state=emotion_state,
                        ability_level=ability,
                        category=category,
                        recent_messages=recent_messages,
                        max_questions=5
                    )
                else:
                    response.suggested_questions = []
            except Exception as e:
                logger.warning(f"⚠️  Failed to generate follow-up questions: {e}")
                response.suggested_questions = []
            
            total_time_ms = response.response_time_ms
            logger.info(
                f"✅ Deep Thinking request processed in {total_time_ms:.0f}ms "
                f"(reasoning: {reasoning_time_ms:.0f}ms, "
                f"AI: {ai_time_ms:.0f}ms) | "
                f"Mode: {thinking_mode.value if thinking_mode else 'system1'}"
            )
            
            # Convert AIResponse to dict for server.py compatibility
            return {
                "message": response.content,
                "provider_used": response.provider,
                "model_name": response.model_name,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time_ms": response.response_time_ms,
                "emotion_state": response.emotion_state.model_dump() if response.emotion_state else None,
                "category_detected": response.category,
                "context_retrieved": response.context_info.model_dump() if response.context_info else None,
                "ability_info": response.ability_info.model_dump() if response.ability_info else None,
                "ability_updated": response.ability_updated,
                "processing_breakdown": response.processing_breakdown,
                "rag_enabled": response.rag_enabled,
                "citations": response.citations,
                "sources_count": response.sources_count,
                "search_provider": response.search_provider,
                "suggested_questions": [q.model_dump() for q in response.suggested_questions] if response.suggested_questions else [],
                "reasoning_enabled": response.reasoning_enabled if hasattr(response, 'reasoning_enabled') else enable_reasoning,
                "reasoning_chain": response.reasoning_chain if hasattr(response, 'reasoning_chain') else None,
                "thinking_mode": response.thinking_mode if hasattr(response, 'thinking_mode') else (thinking_mode.value if thinking_mode else 'system1'),
                "cached": False
            }
        
        except Exception as e:
            logger.error(f"❌ Error in Deep Thinking processing: {e}", exc_info=True)
            raise MasterXError(
                f"Failed to process request with reasoning: {str(e)}",
                details={
                    'user_id': user_id,
                    'session_id': session_id,
                    'error': str(e)
                }
            )
    
    async def _process_basic(
        self,
        user_id: str,
        message: str,
        session_id: str,
        context: Optional[dict] = None
    ) -> AIResponse:
        """
        Fallback to basic processing if intelligence layer not initialized
        (Phase 1 mode for backwards compatibility)
        """
        logger.warning("Using basic processing mode (Phase 1 fallback)")
        
        # Basic emotion detection
        emotion_result = await self.emotion_engine.analyze_emotion(
            text=message,
            user_id=user_id,
            session_id=session_id,
            interaction_context=context
        )
        
        # Map EmotionCore LearningReadiness to Models LearningReadiness
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
        
        # Basic provider selection
        category = self.provider_manager.detect_category_from_message(message, emotion_state)
        selected_provider = await self.provider_manager.select_best_provider_for_category(
            category, emotion_state
        )
        
        # Basic prompt enhancement
        enhanced_prompt = self._enhance_prompt_with_emotion(message, emotion_result)
        
        # Dynamic token allocation
        token_limit = self.calculate_token_limit(message, emotion_result)
        
        # Generate response
        response = await self.provider_manager.generate(
            prompt=enhanced_prompt,
            provider_name=selected_provider,
            max_tokens=token_limit
        )
        
        response.emotion_state = emotion_state
        
        return response
    
    def _enhance_prompt_with_emotion(self, message: str, emotion_result) -> str:
        """
        Enhance prompt with emotion context (Phase 1 basic version)
        """
        emotion_guidance = self._get_emotion_guidance(emotion_result)
        
        enhanced_prompt = f"""{emotion_guidance}

User message: {message}

Provide a helpful, clear, and supportive response."""
        
        return enhanced_prompt
    
    def _enhance_prompt_phase3(
        self,
        message: str,
        emotion_result,
        recent_messages: List[Message],
        relevant_messages: List[Message],
        difficulty_level,
        ability: float,
        rag_context = None
    ) -> str:
        """
        Phase 3: Advanced prompt enhancement with context and difficulty
        
        ENHANCED :
        - Explicit continuity instructions
        - Context-aware response requirements
        - Building on previous conversation
        - Real-time web knowledge (RAG)
        
        Args:
            message: Current user message
            emotion_result: Emotion analysis result
            recent_messages: Recent conversation history
            relevant_messages: Semantically relevant past messages
            difficulty_level: Recommended difficulty level
            ability: Current ability estimate
            rag_context: RAG context with real-time web sources (optional)
        
        Returns:
            Enhanced prompt with full context and RAG sources
        """
        
        # Build conversation history with FULL context (not truncated)
        history_text = ""
        continuity_instruction = ""
        
        if recent_messages:
            history_text = "\n🗨️ CONVERSATION HISTORY (Your memory of this session):\n"
            history_text += "=" * 60 + "\n"
            
            # Show more context for continuity (last 8 messages or all if less)
            context_messages = recent_messages[-8:] if len(recent_messages) > 8 else recent_messages
            
            for idx, msg in enumerate(context_messages, 1):
                role_label = "Student" if msg.role == MessageRole.USER else "You (AI Tutor)"
                # Show full content for recent messages (don't truncate)
                content = msg.content if len(msg.content) < 300 else msg.content[:300] + "..."
                history_text += f"\n[Message {idx}] {role_label}:\n{content}\n"
            
            history_text += "=" * 60 + "\n"
            
            # CRITICAL: Add explicit continuity instruction
            continuity_instruction = f"""
🔗 CONTINUITY REQUIREMENT (CRITICAL):
You MUST explicitly acknowledge and build upon the conversation above.
- Start your response by REFERENCING something specific from the conversation
- Use phrases like "Building on what we discussed...", "Following up on...", "As we covered earlier..."
- Show that you REMEMBER and are CONTINUING the conversation, not starting fresh
- If the student asks for clarification, reference the SPECIFIC thing you explained before
- Create a SEAMLESS flow from previous messages to your current response

{
    "⚠️ SPECIAL NOTE: The student seems to be asking for MORE DETAIL or CLARIFICATION about what you just explained. Make sure to EXPLICITLY reference your previous explanation and expand on it."
    if any(word in message.lower() for word in ['more', 'explain', 'clarify', 'again', 'slowly', 'confused', 'understand', 'what do you mean'])
    else ""
}
"""
        
        # Build relevant context from past sessions
        relevant_text = ""
        if relevant_messages:
            relevant_text = "\n📚 RELEVANT PAST CONTEXT (from earlier in this learning journey):\n"
            for msg in relevant_messages[:2]:  # Top 2 relevant
                role_label = "Student" if msg.role == MessageRole.USER else "You"
                relevant_text += f"- {role_label}: {msg.content[:150]}...\n"
            relevant_text += "\n"
        
        # Build RAG context (real-time web knowledge)
        rag_text = ""
        citation_instruction = ""
        if rag_context and rag_context.sources:
            rag_text = f"\n🌐 {rag_context.context_text}\n"
            citation_instruction = """
📎 CITATION REQUIREMENT:
When using information from the web sources above:
1. Include inline citations like [1], [2], [3]
2. Be specific about which source supports which claim
3. Combine your knowledge with these current sources
4. If sources conflict with your training, prioritize recent sources and note the update
"""
        
        # Get emotion guidance
        emotion_guidance = self._get_emotion_guidance(emotion_result)
        
        # Build difficulty guidance
        difficulty_guidance = f"""
📊 LEARNER PROFILE:
- Current Ability: {ability:.2f} (scale: -3.0=beginner to +3.0=expert, 0.0=average)
- Target Difficulty: {difficulty_level.label} ({difficulty_level.value:.2f})
- Guidance: {difficulty_level.explanation}

⚙️ ADAPTATION REQUIREMENT:
Calibrate your response complexity to match the target difficulty level above.
"""
        
        # Combine everything with clear structure
        enhanced_prompt = f"""You are an adaptive AI tutor having an ONGOING conversation with a student.

{continuity_instruction}

EMOTIONAL STATE & TEACHING STRATEGY:
{emotion_guidance}

{difficulty_guidance}
{history_text}
{relevant_text}
{rag_text}
{citation_instruction}

CURRENT STUDENT MESSAGE:
"{message}"

📝 RESPONSE REQUIREMENTS:
✅ EXPLICITLY reference the conversation history above (use "Building on...", "As we discussed...")
✅ Show continuity - you're continuing a conversation, not answering in isolation
✅ Match the student's current emotional state (see guidance above)
✅ Calibrate difficulty to their ability level ({difficulty_level.label})
✅ Use clear structure (headings, bullet points) if it helps understanding
✅ Check for understanding before advancing to new concepts
✅ Be supportive, patient, and educational
{("✅ Include citations [1], [2], etc. when using web sources" if rag_context else "")}

Remember: This is a CONTINUING conversation. Build on what came before."""
        
        return enhanced_prompt

    def _enhance_prompt_with_reasoning(
        self,
        message: str,
        emotion_result,
        recent_messages: List[Message],
        relevant_messages: List[Message],
        difficulty_level,
        ability: float,
        reasoning_chain: Optional[ReasoningChain] = None,
        rag_context = None
    ) -> str:
        """
        Phase 4: Prompt enhancement with reasoning chain
        
        Extends Phase 3 prompt with visible reasoning steps to help AI:
        1. Understand the thinking process
        2. Build upon reasoning steps
        3. Provide coherent conclusion
        
        Args:
            message: Current user message
            emotion_result: Emotion analysis result
            recent_messages: Recent conversation history
            relevant_messages: Semantically relevant past messages
            difficulty_level: Recommended difficulty level
            ability: Current ability estimate
            reasoning_chain: Generated reasoning chain (optional)
            rag_context: RAG context with web sources (optional)
        
        Returns:
            Enhanced prompt with reasoning context
        """
        
        # Start with Phase 3 base prompt
        base_prompt = self._enhance_prompt_phase3(
            message=message,
            emotion_result=emotion_result,
            recent_messages=recent_messages,
            relevant_messages=relevant_messages,
            difficulty_level=difficulty_level,
            ability=ability,
            rag_context=rag_context
        )
        
        # If no reasoning chain, return base prompt
        if not reasoning_chain or not reasoning_chain.steps:
            return base_prompt
        
        # Add reasoning chain context
        reasoning_text = f"""

🧠 REASONING PROCESS (Your step-by-step thinking):
{"=" * 60}
This is how you approached this problem. Use these steps to inform your final response.

"""
        
        for step in reasoning_chain.steps:
            reasoning_text += f"""
Step {step.step_number} [{step.strategy.value.upper()}] (confidence: {step.confidence:.0%}):
{step.content}

"""
        
        reasoning_text += f"""{"=" * 60}

📋 REASONING INTEGRATION INSTRUCTIONS:
1. Review the reasoning steps above - they represent your thinking process
2. Synthesize these steps into a coherent, student-friendly explanation
3. Don't repeat the steps verbatim, but use them to structure your response
4. Maintain the logical flow from the reasoning chain
5. Ensure your conclusion aligns with the reasoning process
6. If a reasoning step has low confidence, acknowledge uncertainty appropriately

"""
        
        # Insert reasoning before the final response requirements
        enhanced_with_reasoning = base_prompt.replace(
            "📝 RESPONSE REQUIREMENTS:",
            reasoning_text + "📝 RESPONSE REQUIREMENTS:"
        )
        
        return enhanced_with_reasoning

    
    
    def _should_enable_rag(self, message: str, category: str) -> bool:
        """
        Determine if RAG (real-time web search) should be enabled for this query
        
        RAG is beneficial for:
        - Current events, news, recent developments
        - Specific facts, data, statistics
        - Technology documentation, tutorials
        - Research topics requiring latest information
        
        RAG is NOT needed for:
        - Math problems (unless asking about new methods)
        - General concept explanations
        - Practice/homework help
        - Emotional support conversations
        
        Args:
            message: User message
            query: User query text
            category: Detected category
        
        Returns:
            True if RAG should be enabled
        """
        message_lower = message.lower()
        
        # Strong indicators FOR RAG
        rag_keywords = [
            'current', 'latest', 'recent', 'new', 'today', 'this year',
            'update', 'news', 'what happened', '2024', '2025',
            'documentation', 'tutorial', 'guide', 'how to',
            'research', 'study', 'paper', 'article',
            'statistics', 'data', 'facts about'
        ]
        
        for keyword in rag_keywords:
            if keyword in message_lower:
                logger.debug(f"RAG enabled: found keyword '{keyword}'")
                return True
        
        # Strong indicators AGAINST RAG
        no_rag_keywords = [
            'solve this', 'calculate', 'what is the result',
            'homework', 'practice problem', 'exercise',
            'feeling', 'emotion', 'support', 'help me understand my'
        ]
        
        for keyword in no_rag_keywords:
            if keyword in message_lower:
                logger.debug(f"RAG disabled: found keyword '{keyword}'")
                return False
        
        # Category-based decision
        # Enable for research-heavy categories
        if category in ['research', 'general']:
            return True
        
        # Disable for math-heavy (usually doesn't need current info)
        if category == 'math':
            return False
        
        # Default: enable for medium+ length queries (indicates depth)
        # Short queries like "hi" or "thanks" don't need RAG
        if len(message.split()) >= 8:
            logger.debug("RAG enabled: query length >= 8 words")
            return True
        
        logger.debug("RAG disabled: default (short query, no indicators)")
        return False

    def _infer_success_from_emotion(self, emotion_state: EmotionState) -> bool:
        """
        Infer interaction success from emotional state
        
        Uses multiple signals:
        1. Primary emotion (positive vs negative)
        2. Valence (positive vs negative affect)
        3. Learning readiness (indicator of engagement)
        
        In full system, this would be based on correctness checks.
        
        Args:
            emotion_state: Current emotional state
        
        Returns:
            True if interaction seems successful
        """
        positive_emotions = [
            'joy', 'achievement', 'flow_state', 'engagement',
            'curiosity', 'confidence', 'satisfaction', 'excitement'
        ]
        
        negative_emotions = [
            'frustration', 'confusion', 'anxiety', 'boredom',
            'overwhelmed', 'disappointment'
        ]
        
        # Multi-signal approach
        emotion_positive = emotion_state.primary_emotion in positive_emotions
        emotion_negative = emotion_state.primary_emotion in negative_emotions
        
        # Valence: > 0.55 = positive, < 0.45 = negative
        valence_positive = emotion_state.valence > 0.55
        valence_negative = emotion_state.valence < 0.45
        
        # Readiness: high/moderate = engaged, low = struggling
        readiness_engaged = emotion_state.learning_readiness in [
            LearningReadiness.HIGH_READINESS,
            LearningReadiness.MODERATE_READINESS
        ]
        
        # Weighted decision (prioritize valence and readiness over emotion label)
        # This helps when emotion detection is inaccurate
        if emotion_negative or valence_negative:
            return False  # Clearly struggling
        elif emotion_positive and valence_positive and readiness_engaged:
            return True  # Clearly succeeding
        elif valence_positive or readiness_engaged:
            return True  # Probably succeeding (valence/readiness are more reliable)
        else:
            # Default: neutral/uncertain
            # Use valence as tiebreaker (0.5 = neutral)
            return emotion_state.valence >= 0.5
    
    def _get_emotion_guidance(self, emotion_result) -> str:
        """
        Get guidance for AI based on detected emotion
        
        ENHANCED (Perplexity-Inspired):
        - More specific teaching strategies
        - Emotional intelligence in response
        - Clear action items for AI
        """
        
        emotion = emotion_result.primary_emotion
        readiness = emotion_result.learning_readiness
        confidence = getattr(emotion_result, 'confidence', 0.0)
        
        # Build comprehensive guidance
        guidance = f"""
😊 DETECTED EMOTION: {emotion} (confidence: {confidence:.0%})
📊 LEARNING READINESS: {readiness}
"""
        
        # Emotion-specific teaching strategies
        if emotion in ['frustration', 'anxiety', 'overwhelmed']:
            guidance += """
🎯 TEACHING STRATEGY - Student is STRUGGLING:
- Primary Emotion: Frustration/Anxiety (they're feeling stuck or worried)
- ⚠️ CRITICAL: Be EXTRA patient and encouraging
- ⚠️ CRITICAL: Provide DETAILED, step-by-step explanations (300+ words minimum)
- Validate their feelings: "I can see this is challenging..."
- Break down into MICRO-steps (smaller than usual)
- Use multiple examples and analogies
- Offer: "Would you like me to explain this differently?"
- Reassure: "This is a difficult concept - you're doing great by asking!"
- Check understanding FREQUENTLY at each step"""
        
        elif emotion in ['confusion', 'uncertainty']:
            guidance += """
🎯 TEACHING STRATEGY - Student is CONFUSED:
- Primary Emotion: Confusion (they don't understand something)
- ⚠️ IMPORTANT: Clarify with CONCRETE examples
- Use analogies related to everyday experiences
- Ask: "What specific part is confusing?" (help them pinpoint)
- Rephrase explanations in different ways
- Use visual descriptions when possible
- Check: "Does this make sense so far?"
- Offer alternative approaches: "Another way to think about it..."
"""
        
        elif emotion in ['joy', 'achievement', 'flow_state', 'admiration']:
            guidance += """
🎯 TEACHING STRATEGY - Student is ENGAGED and POSITIVE:
- Primary Emotion: Joy/Achievement (they're excited or feeling successful)
- 🚀 OPPORTUNITY: Build on this momentum!
- Celebrate their understanding: "Great insight!"
- Challenge them appropriately (can push slightly harder)
- Maintain flow state - keep them engaged
- Ask thought-provoking questions
- Introduce next-level concepts: "Ready to explore...?"
- Encourage curiosity: "What do you think happens if..."
"""
        
        elif emotion in ['boredom', 'disengagement']:
            guidance += """
🎯 TEACHING STRATEGY - Student seems BORED:
- Primary Emotion: Boredom (content may be too easy or uninteresting)
- ⚡ SPARK INTEREST: Make it engaging and relevant
- Use FASCINATING examples or surprising facts
- Connect to real-world applications they care about
- Ask: "Have you ever wondered why...?"
- Increase challenge slightly (may be too easy)
- Use storytelling: "Imagine you're..."
- Make it interactive: "What would you do if..."
"""
        
        elif emotion in ['curiosity', 'interest']:
            guidance += """
🎯 TEACHING STRATEGY - Student is CURIOUS:
- Primary Emotion: Curiosity (they want to learn more!)
- 🌟 PERFECT STATE: Feed their curiosity!
- Provide rich, detailed explanations
- Add interesting insights and connections
- Encourage exploration: "Great question! This relates to..."
- Share fascinating details
- Suggest follow-up investigations
"""
        
        else:
            guidance += """
🎯 TEACHING STRATEGY - Student is NEUTRAL/READY:
- Primary Emotion: Neutral or Moderate engagement
- Provide clear, structured explanations
- Balance detail with conciseness
- Check engagement: "Is this making sense?"
- Adjust based on their responses
"""
        
        return guidance
    
    def get_available_providers(self):
        """Get list of available AI providers"""
        return self.provider_manager.get_available_providers()

    
    
    
    def calculate_token_limit(
        self, 
        message: str, 
        emotion_result,
        complexity_boost: float = 1.0
    ) -> int:
        """
        Dynamically calculate token limit based on message and emotional state.
        
        Args:
            message: User's input message
            emotion_result: Object with learning_readiness attribute
            complexity_boost: Multiplier for domain complexity (default 1.0)
                            Use 1.2 for math/science, 0.8 for casual chat
        
        Returns:
            Token limit (int) suitable for the model and context
        """
        message_lower = message.lower()
        word_count = len(message.split())
        
        # === STEP 1: BASE SIZE FROM MESSAGE LENGTH ===
        base_tokens = self._get_base_from_length(word_count)
        
        # === STEP 2: ADJUST FOR QUESTION TYPE ===
        base_tokens = self._adjust_for_question_type(message_lower, base_tokens)
        
        # === STEP 3: ADJUST FOR LEARNING READINESS ===
        base_tokens = self._adjust_for_readiness(
            emotion_result.learning_readiness, 
            base_tokens
        )
        
        # === STEP 4: ADJUST FOR STRUGGLE INDICATORS ===
        base_tokens = self._adjust_for_struggle(message_lower, base_tokens)
        
        # === STEP 5: APPLY COMPLEXITY BOOST ===
        base_tokens = int(base_tokens * complexity_boost)
        
        # === STEP 6: ENSURE WITHIN MODEL LIMITS ===
        final_tokens = self._apply_model_constraints(base_tokens)
        
        return final_tokens
    
    def _get_base_from_length(self, word_count: int) -> int:
        """Determine base token allocation from message length"""
        if word_count < 5:
            return self.RESPONSE_SIZES['minimal']
        elif word_count < 15:
            return self.RESPONSE_SIZES['concise']
        elif word_count < 30:
            return self.RESPONSE_SIZES['standard']
        elif word_count < 60:
            return self.RESPONSE_SIZES['detailed']
        else:
            return self.RESPONSE_SIZES['comprehensive']
    
    def _adjust_for_question_type(self, message_lower: str, base: int) -> int:
        """Adjust tokens based on question type patterns"""
        
        # Explanation requests need more space
        explanation_keywords = [
            'explain', 'how does', 'how do', 'why', 'what is', 'what are',
            'tell me about', 'describe', 'teach me', 'help me understand',
            'learn about', 'walk me through', 'show me', 'demonstrate',
            'tutorial', 'guide me', 'break down'
        ]
        
        if any(keyword in message_lower for keyword in explanation_keywords):
            base = max(base, self.RESPONSE_SIZES['detailed'])
        
        # Multiple questions need more space
        question_count = message_lower.count('?')
        if question_count > 2:
            base = max(base, self.RESPONSE_SIZES['comprehensive'])
        
        # Step-by-step requests
        step_keywords = ['step by step', 'steps to', 'walkthrough', 'process']
        if any(keyword in message_lower for keyword in step_keywords):
            base = max(base, self.RESPONSE_SIZES['detailed'])
        
        # Code/technical requests
        code_keywords = ['code', 'function', 'implement', 'algorithm', 'debug']
        if any(keyword in message_lower for keyword in code_keywords):
            base = max(base, self.RESPONSE_SIZES['detailed'])
        
        # Comparison questions
        comparison_keywords = ['compare', 'difference between', 'vs', 'versus']
        if any(keyword in message_lower for keyword in comparison_keywords):
            base = max(base, self.RESPONSE_SIZES['detailed'])
        
        return base
    
    def _adjust_for_readiness(self, readiness: str, base: int) -> int:
        """
        Adjust based on student's emotional/learning state
        
        ENHANCED :
        - More aggressive token allocation for struggling students
        - Ensure minimum response length requirements
        - Prioritize student support over efficiency
        """
        
        if readiness == 'blocked':
            # Maximum support - needs extensive help
            # ENHANCED: Force extensive responses (4500+ tokens = ~350+ words)
            return max(base, self.RESPONSE_SIZES['extensive'])
        
        elif readiness in ['not_ready', 'low_readiness', 'low']:
            # Struggling - needs comprehensive, detailed explanations
            # ENHANCED: Ensure at least comprehensive (3500+ tokens = ~270+ words)
            # This ensures struggling students get 300+ word responses
            return max(base, self.RESPONSE_SIZES['extensive'])  # INCREASED from comprehensive
        
        elif readiness in ['moderate_readiness', 'moderate']:
            # Normal learning - standard to detailed
            return max(base, self.RESPONSE_SIZES['detailed'])
        
        elif readiness in ['optimal_readiness', 'optimal', 'good']:
            # Doing well - can be efficient but still thorough
            return min(base, self.RESPONSE_SIZES['comprehensive'])
        
        else:
            # Unknown readiness - err on side of being helpful
            return max(base, self.RESPONSE_SIZES['standard'])
    
    def _adjust_for_struggle(self, message_lower: str, base: int) -> int:
        """Boost tokens if explicit struggle indicators present"""
        
        struggle_indicators = [
            'confused', "don't understand", "can't understand",
            "doesn't make sense", "can't figure out", 'lost', 'stuck',
            'help', 'struggling', 'difficult', 'hard to understand',
            'not getting', "can't get", 'keep failing', 'tried multiple times',
            'frustrated', "still don't get", 'really need help'
        ]
        
        if any(indicator in message_lower for indicator in struggle_indicators):
            return max(base, self.RESPONSE_SIZES['extensive'])
        
        return base
    
    def _apply_model_constraints(self, tokens: int) -> int:
        """Ensure token count is within model's safe operating range"""
        
        # Never exceed model's safe maximum
        tokens = min(tokens, self.safe_max)
        
        # Ensure minimum quality threshold (never too short)
        tokens = max(tokens, self.RESPONSE_SIZES['minimal'])
        
        return tokens
    
    def get_recommended_limit_for_scenario(self, scenario: str) -> int:
        """
        Get pre-calculated token limits for common scenarios.
        Useful for quick testing or default values.
        """
        scenarios = {
            'quick_fact': self.RESPONSE_SIZES['minimal'],
            'simple_answer': self.RESPONSE_SIZES['concise'],
            'normal_question': self.RESPONSE_SIZES['standard'],
            'explanation': self.RESPONSE_SIZES['detailed'],
            'complex_topic': self.RESPONSE_SIZES['comprehensive'],
            'struggling_student': self.RESPONSE_SIZES['extensive']
        }
        
        limit = scenarios.get(scenario, self.RESPONSE_SIZES['standard'])
        limit = scenarios.get(scenario, self.RESPONSE_SIZES['standard'])
        return limit
    
    def generate_follow_up_questions(
        self,
        user_message: str,
        ai_response: str,
        emotion_state: EmotionState,
        ability_level: float,
        category: str,
        recent_messages: List[Message] = None
    ) -> List['SuggestedQuestion']:
        """
        Generate contextually relevant follow-up questions (Perplexity-inspired)
        
        Uses ML-based analysis to create 3-5 thought-provoking questions based on:
        - Student's emotional state (struggling vs confident)
        - Difficulty progression (easier/same/harder)
        - Topic connections (broaden/deepen/apply)
        - Conversation context
        
        Args:
            user_message: Original user question
            ai_response: AI's response content
            emotion_state: Student's emotional state
            ability_level: Current ability level (-3.0 to +3.0)
            category: Detected category (math, coding, etc.)
            recent_messages: Recent conversation messages
            
        Returns:
            List of 3-5 SuggestedQuestion objects
        """
        from core.models import SuggestedQuestion
        
        suggested_questions = []
        
        # ================================================================
        # ANALYSIS PHASE: Understand context and student state
        # ================================================================
        
        # 1. Assess student's current state
        is_struggling = emotion_state.learning_readiness in [
            LearningReadiness.LOW_READINESS,
            LearningReadiness.NOT_READY
        ]
        
        is_confident = emotion_state.learning_readiness in [
            LearningReadiness.HIGH_READINESS,
            LearningReadiness.OPTIMAL_READINESS
        ]
        
        # 2. Extract topic from conversation
        topic = self._extract_topic(user_message, ai_response)
        
        # 3. Determine complexity level
        message_complexity = self._estimate_question_complexity(user_message)
        
        # ================================================================
        # GENERATION PHASE: Create diverse question types
        # ================================================================
        
        # Strategy 1: CLARIFICATION (if struggling or confused)
        if is_struggling or emotion_state.primary_emotion in ['confusion', 'anxiety']:
            clarification_q = self._generate_clarification_question(
                topic, user_message, ability_level
            )
            if clarification_q:
                suggested_questions.append(SuggestedQuestion(
                    question=clarification_q,
                    rationale="clarification_needed",
                    difficulty_delta=-0.2,  # Easier
                    category="clarification"
                ))
        
        # Strategy 2: PRACTICE (same difficulty level)
        practice_q = self._generate_practice_question(
            topic, category, ability_level, message_complexity
        )
        if practice_q:
            suggested_questions.append(SuggestedQuestion(
                question=practice_q,
                rationale="practice_same_level",
                difficulty_delta=0.0,  # Same level
                category="practice"
            ))
        
        # Strategy 3: CHALLENGE (if confident, push harder)
        if is_confident and not is_struggling:
            challenge_q = self._generate_challenge_question(
                topic, category, ability_level
            )
            if challenge_q:
                suggested_questions.append(SuggestedQuestion(
                    question=challenge_q,
                    rationale="building_on_success",
                    difficulty_delta=0.3,  # Harder
                    category="challenge"
                ))
        
        # Strategy 4: CONNECTION (relate to other concepts)
        connection_q = self._generate_connection_question(
            topic, category, recent_messages
        )
        if connection_q:
            suggested_questions.append(SuggestedQuestion(
                question=connection_q,
                rationale="connecting_concepts",
                difficulty_delta=0.1,  # Slightly harder
                category="exploration"
            ))
        
        # Strategy 5: APPLICATION (real-world use)
        if message_complexity > 0.4 or category in ['coding', 'math', 'science']:
            application_q = self._generate_application_question(
                topic, category
            )
            if application_q:
                suggested_questions.append(SuggestedQuestion(
                    question=application_q,
                    rationale="practical_application",
                    difficulty_delta=0.2,
                    category="application"
                ))
        
        # ================================================================
        # FILTERING & RANKING: Select best 3-5 questions
        # ================================================================
        
        # Ensure we have variety (no duplicate categories)
        unique_questions = []
        seen_categories = set()
        
        for q in suggested_questions:
            if q.category not in seen_categories:
                unique_questions.append(q)
                seen_categories.add(q.category)
        
        # Limit to 5 questions maximum
        final_questions = unique_questions[:5]
        
        # Ensure minimum of 3 questions (add generic if needed)
        while len(final_questions) < 3:
            generic_q = self._generate_generic_exploration(topic, len(final_questions))
            if generic_q:
                final_questions.append(SuggestedQuestion(
                    question=generic_q,
                    rationale="general_exploration",
                    difficulty_delta=0.0,
                    category="exploration"
                ))
            else:
                break
        
        logger.info(f"✅ Generated {len(final_questions)} follow-up questions")
        return final_questions
    
    def _extract_topic(self, user_message: str, ai_response: str) -> str:
        """
        Extract main topic from conversation using keyword extraction
        
        Simple but effective: find most frequent meaningful words
        """
        import re
        from collections import Counter
        
        # Combine both messages
        text = f"{user_message} {ai_response[:500]}"  # Limit response length
        
        # Remove common words (stopwords)
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'shall', 'of', 'to', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'about', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between',
            'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'what', 'which', 'who', 'you', 'your',
            'i', 'me', 'my', 'we', 'us', 'our', 'they', 'them', 'their', 'this',
            'that', 'these', 'those', 'am', 'it', 'its', 'if', 'or', 'because',
            'explain', 'show', 'tell', 'help', 'understand', 'learn', 'know'
        }
        
        # Extract words (lowercase, alphabetic only)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Count meaningful words
        meaningful_words = [w for w in words if w not in stopwords]
        
        if not meaningful_words:
            return "this topic"
        
        # Get most common word
        word_counts = Counter(meaningful_words)
        top_word = word_counts.most_common(1)[0][0]
        
        return top_word
    
    def _estimate_question_complexity(self, message: str) -> float:
        """
        Estimate question complexity (0.0-1.0) using heuristics
        
        Factors:
        - Length (longer = potentially more complex)
        - Technical vocabulary
        - Question structure
        """
        # Normalize length (0.0-1.0 scale)
        word_count = len(message.split())
        length_score = min(word_count / 50.0, 1.0)  # 50+ words = max
        
        # Technical vocabulary indicators
        technical_words = [
            'algorithm', 'function', 'variable', 'equation', 'derivative',
            'integral', 'matrix', 'vector', 'probability', 'statistics',
            'framework', 'architecture', 'implementation', 'optimization',
            'complexity', 'efficiency', 'polynomial', 'exponential'
        ]
        
        message_lower = message.lower()
        tech_count = sum(1 for word in technical_words if word in message_lower)
        tech_score = min(tech_count / 3.0, 1.0)  # 3+ technical terms = max
        
        # Weighted average
        complexity = (length_score * 0.4) + (tech_score * 0.6)
        
        return complexity
    
    def _generate_clarification_question(
        self, topic: str, user_message: str, ability_level: float
    ) -> Optional[str]:
        """Generate a clarifying question for struggling students"""
        
        # Templates based on ability level
        if ability_level < -1.0:  # Very beginner
            templates = [
                f"Can you break down {topic} into simpler steps?",
                f"What's the easiest way to start with {topic}?",
                f"Could you show me a very basic example of {topic}?"
            ]
        else:
            templates = [
                f"Could you explain the main concept of {topic} differently?",
                f"What specific part of {topic} should I focus on first?",
                f"Can you clarify how {topic} works with a simple example?"
            ]
        
        import random
        return random.choice(templates)
    
    def _generate_practice_question(
        self, topic: str, category: str, ability_level: float, complexity: float
    ) -> Optional[str]:
        """Generate a practice question at same difficulty level"""
        
        # Category-specific templates
        if category == 'math':
            templates = [
                f"Can you give me another {topic} problem to practice?",
                f"Show me a similar {topic} example",
                f"What's another way to solve {topic} problems?"
            ]
        elif category == 'coding':
            templates = [
                f"Can you show me another example using {topic}?",
                f"What's a common use case for {topic}?",
                f"Give me another coding challenge with {topic}"
            ]
        elif category == 'science':
            templates = [
                f"Can you explain another example of {topic}?",
                f"What's a related concept to {topic}?",
                f"Show me how {topic} applies in different scenarios"
            ]
        else:
            templates = [
                f"Can you give me more practice with {topic}?",
                f"Show me another example of {topic}",
                f"What else should I know about {topic}?"
            ]
        
        import random
        return random.choice(templates)
    
    def _generate_challenge_question(
        self, topic: str, category: str, ability_level: float
    ) -> Optional[str]:
        """Generate a harder challenge question for confident students"""
        
        if category == 'math':
            templates = [
                f"Can you show me a harder {topic} problem?",
                f"What's an advanced application of {topic}?",
                f"How does {topic} extend to more complex scenarios?"
            ]
        elif category == 'coding':
            templates = [
                f"What's a more advanced pattern using {topic}?",
                f"How can I optimize {topic} for better performance?",
                f"Show me a real-world challenge involving {topic}"
            ]
        else:
            templates = [
                f"What's a more challenging aspect of {topic}?",
                f"How does {topic} relate to advanced concepts?",
                f"Can you push me further with {topic}?"
            ]
        
        import random
        return random.choice(templates)
    
    def _generate_connection_question(
        self, topic: str, category: str, recent_messages: Optional[List[Message]]
    ) -> Optional[str]:
        """Generate a question connecting to related concepts"""
        
        # Try to find previous topics from conversation
        previous_topic = None
        if recent_messages and len(recent_messages) >= 2:
            # Get a message from 2-3 messages ago
            old_message = recent_messages[-3] if len(recent_messages) >= 3 else recent_messages[-2]
            # Extract a keyword from it
            import re
            words = re.findall(r'\b[a-z]{4,}\b', old_message.content.lower())
            if words:
                previous_topic = words[0]
        
        if previous_topic and previous_topic != topic:
            return f"How does {topic} relate to {previous_topic}?"
        
        # Generic connection templates
        templates = [
            f"How does {topic} connect to other concepts?",
            f"What builds on the foundation of {topic}?",
            f"Where does {topic} fit in the bigger picture?"
        ]
        
        import random
        return random.choice(templates)
    
    def _generate_application_question(self, topic: str, category: str) -> Optional[str]:
        """Generate a real-world application question"""
        
        templates = [
            f"What real-world problems can I solve with {topic}?",
            f"How is {topic} used in practice?",
            f"Can you show me a practical example of {topic}?",
            f"Where would I use {topic} outside of studying?"
        ]
        
        import random
        return random.choice(templates)
    
    def _generate_generic_exploration(self, topic: str, index: int) -> Optional[str]:
        """Generate a generic exploration question as fallback"""
        
        templates = [
            f"What else should I know about {topic}?",
            f"Can you tell me more about {topic}?",
            f"What are the key points about {topic}?",
            f"Help me understand {topic} better"
        ]
        
        if index < len(templates):
            return templates[index]
        return None
        return min(limit, self.safe_max)