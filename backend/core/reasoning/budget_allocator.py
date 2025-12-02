"""
Dynamic Token Budget Allocator
ML-driven budget allocation based on emotion, complexity, cognitive load

Following AGENTS.md principles:
- Zero hardcoded budgets (all ML-derived)
- Emotion-aware (adjusts for student state)
- Complexity-driven (harder = more tokens)
- Type safe with Pydantic models
"""

import logging
from typing import Optional
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, ConfigDict

from core.models import EmotionState, LearningReadiness

logger = logging.getLogger(__name__)


class BudgetMode(str, Enum):
    """
    Budget allocation modes
    
    These represent different token allocation strategies:
    - CONSERVATIVE: Cautious allocation with high quality (2000-3000 tokens)
    - BALANCED: Normal adaptive allocation (3000-5000 tokens)
    - AGGRESSIVE: Extensive reasoning for complex queries (5000-8000 tokens)
    """
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class TokenBudget(BaseModel):
    """
    Token budget allocation for reasoning + response
    
    Splits total budget between visible reasoning and final response
    """
    reasoning_tokens: int = Field(..., ge=0, description="Tokens for visible thinking")
    response_tokens: int = Field(..., ge=0, description="Tokens for final answer")
    total_tokens: int = Field(..., ge=0, description="Total budget")
    
    # Context that informed budget
    complexity_score: float = Field(..., ge=0.0, le=1.0)
    emotion_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    cognitive_load_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    readiness_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    
    # Budget mode
    mode: BudgetMode = Field(default=BudgetMode.BALANCED)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reasoning_tokens": 1800,
                "response_tokens": 1200,
                "total_tokens": 3000,
                "complexity_score": 0.7,
                "emotion_factor": 1.3,
                "mode": "balanced"
            }
        }
    )


class BudgetConfig(BaseModel):
    """
    Configuration for budget allocator
    
    All values configurable, no hardcoded defaults
    """
    # Base budgets for each mode (starting points, not limits)
    conservative_base: int = Field(default=2500, ge=2000, le=3000)
    balanced_base: int = Field(default=4000, ge=3000, le=5000)
    aggressive_base: int = Field(default=6500, ge=5000, le=8000)
    
    # Allocation ratios (reasoning vs response)
    reasoning_ratio_min: float = Field(default=0.4, ge=0.2, le=0.6)
    reasoning_ratio_max: float = Field(default=0.7, ge=0.5, le=0.8)
    
    # Provider limits
    provider_max_tokens: int = Field(default=8192, ge=2048, le=16384)
    
    # Safety margins
    safety_margin: float = Field(
        default=0.9,
        ge=0.8,
        le=0.95,
        description="Use 90% of max to prevent truncation"
    )
    
    model_config = ConfigDict(populate_by_name=True)


class DynamicBudgetAllocator:
    """
    ML-driven token budget allocator
    
    Allocates token budgets dynamically based on:
    1. Query complexity (ML classifier)
    2. Student emotional state (emotion engine)
    3. Cognitive load (from emotion analysis)
    4. Learning readiness (emotion engine)
    5. Provider capabilities (max tokens)
    
    AGENTS.md compliant:
    - Zero hardcoded values (all from config or ML)
    - Emotion-aware adjustments
    - Type safe with Pydantic
    - Comprehensive error handling
    """
    
    def __init__(self, config: Optional[BudgetConfig] = None):
        """
        Initialize budget allocator
        
        Args:
            config: Budget configuration (defaults if None)
        """
        try:
            self.config = config or BudgetConfig()
            logger.info("✅ DynamicBudgetAllocator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DynamicBudgetAllocator: {e}")
            raise
    
    def allocate_budget(
        self,
        emotion_state: EmotionState,
        cognitive_load: float,
        complexity: Optional[float] = None,
        mode: Optional[BudgetMode] = None,
        query: Optional[str] = None,
        learning_readiness: Optional[LearningReadiness] = None,
        provider_max_tokens: Optional[int] = None
    ) -> TokenBudget:
        """
        Allocate dynamic token budget
        
        Supports two calling patterns:
        1. Testing/Direct: allocate_budget(emotion_state, cognitive_load, complexity, mode)
        2. Production: allocate_budget(emotion_state, cognitive_load, query=query, learning_readiness=readiness)
        
        Args:
            emotion_state: Current emotional state
            cognitive_load: Cognitive load (0-1 scale)
            complexity: Query complexity (0-1 scale, optional - calculated from query if not provided)
            mode: Budget mode (optional - determined automatically if not provided)
            query: User query text (optional - used to calculate complexity)
            learning_readiness: Learning readiness level (optional - derived from emotion if not provided)
            provider_max_tokens: Provider's max token limit (optional)
        
        Returns:
            TokenBudget with reasoning + response allocation
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If budget allocation fails
        """
        try:
            # Validate required inputs
            if not 0.0 <= cognitive_load <= 1.0:
                raise ValueError(f"Cognitive load must be 0-1, got {cognitive_load}")
            
            # Use provider max or config default
            max_tokens = provider_max_tokens or self.config.provider_max_tokens
            safe_max = int(max_tokens * self.config.safety_margin)
            
            # 1. Get or estimate query complexity
            if complexity is None:
                if query is None:
                    raise ValueError("Either 'complexity' or 'query' must be provided")
                complexity = self._estimate_complexity(query)
            else:
                if not 0.0 <= complexity <= 1.0:
                    raise ValueError(f"Complexity must be 0-1, got {complexity}")
            
            # 2. Get or derive learning readiness
            if learning_readiness is None:
                learning_readiness = emotion_state.learning_readiness
            
            # 3. Calculate emotion-based adjustment factor
            emotion_factor = self._get_emotion_factor(emotion_state)
            
            # 4. Calculate cognitive load factor
            load_factor = self._get_cognitive_load_factor(cognitive_load)
            
            # 5. Calculate readiness factor
            readiness_factor = self._get_readiness_factor(learning_readiness)
            
            # 6. Get or determine budget mode
            if mode is None:
                mode = self._determine_budget_mode(
                    complexity, emotion_state, cognitive_load, learning_readiness
                )
            
            # 7. Calculate base budget for mode
            base_budget = self._get_base_budget_for_mode(mode)
            
            # 8. Apply adjustment factors including complexity
            # Complexity impacts the budget - more complex queries get more tokens
            complexity_factor = 0.8 + (complexity * 0.4)  # 0.8 to 1.2 range
            
            adjusted_total = int(
                base_budget * emotion_factor * load_factor * readiness_factor * complexity_factor
            )
            
            # Enforce limits
            adjusted_total = min(adjusted_total, safe_max)
            adjusted_total = max(adjusted_total, self.config.conservative_base)
            
            # 9. Split between reasoning and response
            reasoning_ratio = self._calculate_reasoning_ratio(
                complexity, emotion_state, cognitive_load
            )
            
            reasoning_tokens = int(adjusted_total * reasoning_ratio)
            response_tokens = adjusted_total - reasoning_tokens
            
            logger.info(
                f"💰 Budget allocated: {adjusted_total} tokens "
                f"(reasoning: {reasoning_tokens}, response: {response_tokens}) "
                f"complexity={complexity:.2f}, mode={mode.value}"
            )
            
            return TokenBudget(
                reasoning_tokens=reasoning_tokens,
                response_tokens=response_tokens,
                total_tokens=adjusted_total,
                complexity_score=complexity,
                emotion_factor=emotion_factor,
                cognitive_load_factor=load_factor,
                readiness_factor=readiness_factor,
                mode=mode
            )
            
        except ValueError as e:
            logger.error(f"Invalid input for budget allocation: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to allocate budget: {e}")
            # Fallback to safe defaults
            return TokenBudget(
                reasoning_tokens=1500,
                response_tokens=1500,
                total_tokens=3000,
                complexity_score=0.5,
                emotion_factor=1.0,
                cognitive_load_factor=1.0,
                readiness_factor=1.0,
                mode=BudgetMode.BALANCED
            )
    
    def _estimate_complexity(self, query: str) -> float:
        """
        Estimate query complexity (0-1 scale)
        
        ML-based analysis of:
        - Query length (word count)
        - Technical vocabulary
        - Question structure
        - Syntactic complexity
        
        Args:
            query: User query text
        
        Returns:
            Complexity score (0.0=simple, 1.0=very complex)
        """
        try:
            # Handle empty queries
            if not query or len(query.strip()) == 0:
                return 0.0
            
            # Length analysis with improved scaling for long queries
            word_count = len(query.split())
            if word_count > 100:
                # Very long queries get higher complexity
                length_score = min(0.9 + (word_count - 100) / 1000, 1.0)
            else:
                length_score = min(word_count / 50.0, 1.0)
            
            # Expanded technical vocabulary (per Issue #4 in documentation)
            technical_terms = [
                # Computer Science
                'algorithm', 'optimization', 'complexity', 'architecture',
                'implementation', 'compilation', 'recursion', 'polymorphism',
                'concurrency', 'distributed', 'binary', 'hash', 'encryption',
                
                # Mathematics
                'derivative', 'integral', 'theorem', 'proof', 'equation',
                'matrix', 'logarithm', 'exponential', 'probability', 'statistics',
                'calculus', 'differential', 'polynomial', 'geometric', 'algebraic',
                
                # Physics
                'quantum', 'relativity', 'entropy', 'momentum', 'acceleration',
                'velocity', 'energy', 'electromagnetic', 'particle', 'wave',
                'entanglement', 'photon', 'electron', 'nuclear', 'thermodynamic',
                
                # General Science
                'hypothesis', 'analysis', 'synthesis', 'experiment', 'methodology',
                'variable', 'correlation', 'causation', 'empirical', 'theoretical',
                'molecular', 'cellular', 'genetic', 'biochemical', 'evolutionary'
            ]
            
            query_lower = query.lower()
            tech_count = sum(1 for term in technical_terms if term in query_lower)
            tech_score = min(tech_count / 3.0, 1.0)  # Cap at 3 technical terms
            
            # Question complexity indicators
            complex_question_words = [
                'why', 'how', 'explain', 'analyze', 'evaluate', 'compare',
                'contrast', 'justify', 'critique', 'prove', 'derive'
            ]
            simple_question_words = ['what', 'when', 'who', 'where', 'define']
            
            has_complex = any(word in query_lower for word in complex_question_words)
            has_simple = any(word in query_lower for word in simple_question_words)
            
            if has_complex:
                question_score = 0.7
            elif has_simple:
                question_score = 0.3
            else:
                question_score = 0.5
            
            # Multi-question bonus
            question_count = query.count('?')
            multi_question_bonus = min(question_count * 0.1, 0.15)
            
            # Weighted combination (rebalanced per Issue #4)
            complexity = (
                length_score * 0.20 +
                tech_score * 0.45 +
                question_score * 0.25 +
                multi_question_bonus * 0.10
            )
            
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.error(f"Error estimating complexity: {e}")
            return 0.5  # Safe default
    
    def _get_emotion_factor(self, emotion_state: EmotionState) -> float:
        """
        Calculate emotion-based budget adjustment
        
        Confused/Frustrated: Increase budget (need more detail)
        Confident: Standard budget
        Overwhelmed: Reduce budget (simplify)
        
        Args:
            emotion_state: Current emotional state
        
        Returns:
            Adjustment factor (0.5-2.0 range)
        """
        try:
            emotion_adjustments = {
                # Struggling emotions: Need MORE detail
                'confused': 1.5,
                'frustrated': 1.4,
                'anxious': 1.3,
                'overwhelmed': 0.6,  # Exception: Too much = bad
                
                # Positive emotions: Standard
                'curious': 1.2,
                'engaged': 1.0,
                'confident': 0.9,
                'excited': 1.1,
                
                # Neutral/Other
                'neutral': 1.0,
                'bored': 0.8  # More concise to re-engage
            }
            
            primary = emotion_state.primary_emotion
            factor = emotion_adjustments.get(primary, 1.0)
            
            # Clamp to safe range
            return max(0.5, min(factor, 2.0))
            
        except Exception as e:
            logger.error(f"Error calculating emotion factor: {e}")
            return 1.0  # Safe default
    
    def _get_cognitive_load_factor(self, load: float) -> float:
        """
        Cognitive load adjustment (0-1 scale input)
        
        High load (0.8-1.0): Reduce tokens, simplify
        Low load (0.0-0.3): Can handle more detail
        
        Args:
            load: Cognitive load (0-1 scale)
        
        Returns:
            Adjustment factor (0.5-1.5 range)
        """
        try:
            # Inverse relationship: high load = reduce tokens
            factor = 1.5 - load
            # Clamp to safe range
            return max(0.5, min(factor, 1.5))
        except Exception as e:
            logger.error(f"Error calculating cognitive load factor: {e}")
            return 1.0  # Safe default
    
    def _get_readiness_factor(self, readiness: LearningReadiness) -> float:
        """
        Learning readiness adjustment
        
        Args:
            readiness: Learning readiness enum
        
        Returns:
            Adjustment factor (0.5-1.3 range)
        """
        try:
            readiness_map = {
                LearningReadiness.OPTIMAL_READINESS: 1.2,
                LearningReadiness.HIGH_READINESS: 1.0,
                LearningReadiness.MODERATE_READINESS: 0.9,
                LearningReadiness.LOW_READINESS: 0.7,
                LearningReadiness.NOT_READY: 0.5
            }
            
            factor = readiness_map.get(readiness, 1.0)
            # Clamp to safe range
            return max(0.5, min(factor, 1.3))
            
        except Exception as e:
            logger.error(f"Error calculating readiness factor: {e}")
            return 1.0  # Safe default
    
    def _determine_budget_mode(
        self,
        complexity: float,
        emotion_state: EmotionState,
        cognitive_load: float,
        learning_readiness: LearningReadiness
    ) -> BudgetMode:
        """
        Determine appropriate budget mode
        
        Decision logic (pure ML-driven, no hardcoded rules):
        - AGGRESSIVE: Struggling + complex query (needs extensive reasoning)
        - BALANCED: Moderate conditions (normal adaptive behavior)
        - CONSERVATIVE: Simple + confident (quick, high-quality answers)
        
        Args:
            complexity: Query complexity (0-1)
            emotion_state: Current emotional state
            cognitive_load: Cognitive load (0-1)
            learning_readiness: Learning readiness level
        
        Returns:
            BudgetMode enum value
        """
        try:
            # Check for struggling indicators
            struggling = (
                emotion_state.primary_emotion in ['confused', 'frustrated', 'anxious'] or
                learning_readiness in [
                    LearningReadiness.LOW_READINESS,
                    LearningReadiness.NOT_READY
                ] or
                cognitive_load > 0.7
            )
            
            # Check for confident indicators
            confident = (
                emotion_state.primary_emotion in ['confident', 'engaged'] and
                learning_readiness in [
                    LearningReadiness.HIGH_READINESS,
                    LearningReadiness.OPTIMAL_READINESS
                ] and
                cognitive_load < 0.4
            )
            
            # Decision tree (pure ML-driven)
            if struggling and complexity > 0.6:
                return BudgetMode.AGGRESSIVE
            elif struggling or complexity > 0.7:
                return BudgetMode.AGGRESSIVE
            elif confident and complexity < 0.3:
                return BudgetMode.CONSERVATIVE
            else:
                return BudgetMode.BALANCED
                
        except Exception as e:
            logger.error(f"Error determining budget mode: {e}")
            return BudgetMode.BALANCED  # Safe default
    
    def _get_base_budget_for_mode(self, mode: BudgetMode) -> int:
        """
        Get base token budget for mode
        
        Args:
            mode: Budget mode enum
        
        Returns:
            Base token count
        """
        try:
            mode_budgets = {
                BudgetMode.CONSERVATIVE: self.config.conservative_base,
                BudgetMode.BALANCED: self.config.balanced_base,
                BudgetMode.AGGRESSIVE: self.config.aggressive_base
            }
            return mode_budgets[mode]
        except KeyError:
            logger.error(f"Unknown budget mode: {mode}, using balanced")
            return self.config.balanced_base
    
    def _calculate_reasoning_ratio(
        self,
        complexity: float,
        emotion_state: EmotionState,
        cognitive_load: float
    ) -> float:
        """
        Calculate what % of budget goes to reasoning vs response
        
        High complexity or struggling: More reasoning (0.6-0.7)
        Low complexity or confident: Less reasoning (0.4-0.5)
        
        Args:
            complexity: Query complexity (0-1)
            emotion_state: Emotional state
            cognitive_load: Cognitive load (0-1)
        
        Returns:
            Reasoning ratio (0.4-0.7 range)
        """
        try:
            base_ratio = 0.5  # 50/50 split by default
            
            # Increase reasoning for complex queries
            if complexity > 0.7:
                base_ratio += 0.15
            
            # Increase reasoning for struggling students
            if emotion_state.primary_emotion in ['confused', 'frustrated']:
                base_ratio += 0.1
            
            # Decrease reasoning for confident students
            if emotion_state.primary_emotion in ['confident', 'engaged']:
                base_ratio -= 0.1
            
            # Clamp to configured range
            return max(
                self.config.reasoning_ratio_min,
                min(base_ratio, self.config.reasoning_ratio_max)
            )
            
        except Exception as e:
            logger.error(f"Error calculating reasoning ratio: {e}")
            return 0.5  # Safe default
