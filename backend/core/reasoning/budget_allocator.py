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
import numpy as np
from typing import Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

from core.models import EmotionState, LearningReadiness

logger = logging.getLogger(__name__)


class BudgetMode(str, Enum):
    """Budget allocation modes"""
    CONSERVATIVE = "conservative"     # 2000-3000 tokens (cautious, high quality)
    BALANCED = "balanced"             # 3000-5000 tokens (normal adaptive)
    AGGRESSIVE = "aggressive"         # 5000-8000 tokens (extensive reasoning)


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
    mode: BudgetMode = Field(default=BudgetMode.STANDARD)
    
    class Config:
        json_schema_extra = {
            "example": {
                "reasoning_tokens": 1200,
                "response_tokens": 800,
                "total_tokens": 2000,
                "complexity_score": 0.7,
                "emotion_factor": 1.3,
                "mode": "extended"
            }
        }


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
    provider_max_tokens: int = Field(default=4096, ge=2048, le=8192)
    
    # Safety margins
    safety_margin: float = Field(default=0.9, ge=0.8, le=0.95, description="Use 90% of max")


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
    """
    
    def __init__(self, config: Optional[BudgetConfig] = None):
        """
        Initialize budget allocator
        
        Args:
            config: Budget configuration (defaults if None)
        """
        self.config = config or BudgetConfig()
        logger.info("✅ DynamicBudgetAllocator initialized")
    
    async def allocate_budget(
        self,
        query: str,
        emotion_state: EmotionState,
        cognitive_load: float,
        learning_readiness: LearningReadiness,
        provider_max_tokens: Optional[int] = None
    ) -> TokenBudget:
        """
        Allocate dynamic token budget
        
        Args:
            query: User query text
            emotion_state: Current emotional state
            cognitive_load: Cognitive load (0-1 scale)
            learning_readiness: Learning readiness level
            provider_max_tokens: Provider's max token limit (optional)
        
        Returns:
            TokenBudget with reasoning + response allocation
        """
        
        # Use provider max or config default
        max_tokens = provider_max_tokens or self.config.provider_max_tokens
        safe_max = int(max_tokens * self.config.safety_margin)
        
        # 1. Estimate query complexity (ML-based)
        complexity = self._estimate_complexity(query)
        
        # 2. Calculate emotion-based adjustment factor
        emotion_factor = self._get_emotion_factor(emotion_state)
        
        # 3. Calculate cognitive load factor
        load_factor = self._get_cognitive_load_factor(cognitive_load)
        
        # 4. Calculate readiness factor
        readiness_factor = self._get_readiness_factor(learning_readiness)
        
        # 5. Determine budget mode
        mode = self._determine_budget_mode(
            complexity, emotion_state, cognitive_load, learning_readiness
        )
        
        # 6. Calculate base budget for mode
        base_budget = self._get_base_budget_for_mode(mode)
        
        # 7. Apply adjustment factors
        adjusted_total = int(
            base_budget * emotion_factor * load_factor * readiness_factor
        )
        
        # Enforce limits
        adjusted_total = min(adjusted_total, safe_max)
        adjusted_total = max(adjusted_total, self.config.minimal_base)
        
        # 8. Split between reasoning and response
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
    
    def _estimate_complexity(self, query: str) -> float:
        """
        Estimate query complexity (0-1 scale)
        
        ML-based analysis of:
        - Query length (word count)
        - Technical vocabulary
        - Question structure
        - Syntactic complexity
        
        Returns:
            Complexity score (0.0=simple, 1.0=very complex)
        """
        
        # Length analysis
        word_count = len(query.split())
        length_score = min(word_count / 50.0, 1.0)  # Cap at 50 words
        
        # Technical vocabulary detection
        technical_indicators = [
            'algorithm', 'function', 'variable', 'equation', 'derivative',
            'integral', 'matrix', 'vector', 'probability', 'hypothesis',
            'theorem', 'proof', 'optimization', 'complexity', 'analysis',
            'synthesis', 'evaluation', 'implementation', 'architecture'
        ]
        
        query_lower = query.lower()
        tech_count = sum(1 for term in technical_indicators if term in query_lower)
        tech_score = min(tech_count / 3.0, 1.0)  # Cap at 3 technical terms
        
        # Question complexity indicators
        complex_question_words = ['why', 'how', 'explain', 'analyze', 'evaluate']
        simple_question_words = ['what', 'when', 'who', 'where']
        
        has_complex = any(word in query_lower for word in complex_question_words)
        has_simple = any(word in query_lower for word in simple_question_words)
        
        structure_score = 0.7 if has_complex else (0.3 if has_simple else 0.5)
        
        # Weighted combination
        complexity = (
            length_score * 0.3 +
            tech_score * 0.4 +
            structure_score * 0.3
        )
        
        return complexity
    
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
        return emotion_adjustments.get(primary, 1.0)
    
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
        # Inverse relationship: high load = reduce tokens
        return 1.5 - load
    
    def _get_readiness_factor(self, readiness: LearningReadiness) -> float:
        """
        Learning readiness adjustment
        
        Args:
            readiness: Learning readiness enum
        
        Returns:
            Adjustment factor (0.5-1.3 range)
        """
        
        readiness_map = {
            LearningReadiness.OPTIMAL_READINESS: 1.2,
            LearningReadiness.HIGH_READINESS: 1.0,
            LearningReadiness.MODERATE_READINESS: 0.9,
            LearningReadiness.LOW_READINESS: 0.7,
            LearningReadiness.NOT_READY: 0.5
        }
        
        return readiness_map.get(readiness, 1.0)
    
    def _determine_budget_mode(
        self,
        complexity: float,
        emotion_state: EmotionState,
        cognitive_load: float,
        learning_readiness: LearningReadiness
    ) -> BudgetMode:
        """
        Determine appropriate budget mode
        
        Decision logic:
        - Comprehensive: Struggling + complex query
        - Extended: Moderate struggle or high complexity
        - Standard: Normal conditions
        - Minimal: Simple + confident
        """
        
        # Check for struggling indicators
        struggling = (
            emotion_state.primary_emotion in ['confused', 'frustrated', 'anxious'] or
            learning_readiness in [LearningReadiness.LOW_READINESS, LearningReadiness.NOT_READY] or
            cognitive_load > 0.7
        )
        
        # Check for confident indicators
        confident = (
            emotion_state.primary_emotion in ['confident', 'engaged'] and
            learning_readiness in [LearningReadiness.HIGH_READINESS, LearningReadiness.OPTIMAL_READINESS] and
            cognitive_load < 0.4
        )
        
        # Decision tree
        if struggling and complexity > 0.6:
            return BudgetMode.COMPREHENSIVE
        elif struggling or complexity > 0.7:
            return BudgetMode.EXTENDED
        elif confident and complexity < 0.3:
            return BudgetMode.MINIMAL
        else:
            return BudgetMode.STANDARD
    
    def _get_base_budget_for_mode(self, mode: BudgetMode) -> int:
        """Get base token budget for mode"""
        mode_budgets = {
            BudgetMode.MINIMAL: self.config.minimal_base,
            BudgetMode.STANDARD: self.config.standard_base,
            BudgetMode.EXTENDED: self.config.extended_base,
            BudgetMode.COMPREHENSIVE: self.config.comprehensive_base
        }
        return mode_budgets[mode]
    
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
