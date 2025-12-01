"""
Reasoning Chain Data Structures
Represents step-by-step thinking process

AGENTS.MD compliant:
- Pydantic V2 models with ConfigDict
- Type hints
- Zero hardcoded values
- Clean naming
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ReasoningStrategy(str, Enum):
    """Types of reasoning strategies"""
    DEDUCTIVE = "deductive"      # General → specific (logical derivation)
    INDUCTIVE = "inductive"      # Specific → general (pattern recognition)
    ABDUCTIVE = "abductive"      # Best explanation (inference to best hypothesis)
    ANALOGICAL = "analogical"    # By analogy (similar cases)
    CAUSAL = "causal"            # Cause-effect (why questions)
    ALGORITHMIC = "algorithmic"  # Step-by-step procedure (how questions)


class ReasoningStep(BaseModel):
    """
    Single step in reasoning chain
    
    Represents one thought or reasoning action in the thinking process
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = Field(..., ge=1, description="Step number in chain (1-indexed)")
    content: str = Field(..., min_length=1, description="Reasoning content/thought")
    strategy: ReasoningStrategy = Field(default=ReasoningStrategy.DEDUCTIVE)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Confidence in this step")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = Field(None, description="Time to generate this step")
    
    # MCTS metadata (if from MCTS)
    parent_step_id: Optional[str] = None
    ucb_score: Optional[float] = None
    visit_count: Optional[int] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "step_number": 1,
                "content": "First, I need to understand what the equation is asking...",
                "strategy": "deductive",
                "confidence": 0.85
            }
        }
    )


class ReasoningChain(BaseModel):
    """
    Complete reasoning chain from query to response
    
    Contains all thinking steps with metadata for transparency
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str = Field(..., description="Original user query")
    steps: List[ReasoningStep] = Field(default_factory=list, description="Reasoning steps")
    
    # Final result
    conclusion: Optional[str] = Field(None, description="Final conclusion/answer")
    
    # Metadata
    thinking_mode: str = Field(default="system2", description="system1, system2, or hybrid")
    total_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    processing_time_ms: float = Field(default=0.0, ge=0.0)
    token_budget_used: Optional[int] = None
    token_budget_allocated: Optional[int] = None
    
    # Context
    emotion_state: Optional[Dict[str, Any]] = Field(None, description="Emotion at reasoning start")
    complexity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def add_step(self, step: ReasoningStep):
        """Add reasoning step to chain"""
        step.step_number = len(self.steps) + 1
        self.steps.append(step)
    
    def get_strategy_distribution(self) -> Dict[str, int]:
        """Get count of each reasoning strategy used"""
        distribution = {}
        for step in self.steps:
            strategy = step.strategy.value
            distribution[strategy] = distribution.get(strategy, 0) + 1
        return distribution
    
    def get_average_confidence(self) -> float:
        """Calculate average confidence across all steps"""
        if not self.steps:
            return 0.0
        return sum(step.confidence for step in self.steps) / len(self.steps)
    
    def mark_complete(self, conclusion: str):
        """Mark reasoning chain as complete"""
        self.conclusion = conclusion
        self.completed_at = datetime.utcnow()
        self.total_confidence = self.get_average_confidence()
        
        if self.started_at:
            elapsed = (self.completed_at - self.started_at).total_seconds() * 1000
            self.processing_time_ms = elapsed
    
    def to_dict_for_frontend(self) -> Dict[str, Any]:
        """
        Convert to frontend-friendly format
        
        Returns:
            Dictionary optimized for frontend display
        """
        return {
            'id': self.id,
            'query': self.query,
            'thinking_mode': self.thinking_mode,
            'steps': [
                {
                    'step_number': step.step_number,
                    'content': step.content,
                    'strategy': step.strategy.value,
                    'confidence': step.confidence,
                    'timestamp': step.timestamp.isoformat()
                }
                for step in self.steps
            ],
            'conclusion': self.conclusion,
            'total_confidence': self.total_confidence,
            'processing_time_ms': self.processing_time_ms,
            'complexity_score': self.complexity_score,
            'strategy_distribution': self.get_strategy_distribution()
        }
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "query": "Explain how photosynthesis works",
                "thinking_mode": "system2",
                "steps": [
                    {
                        "step_number": 1,
                        "content": "First, identify the key components...",
                        "strategy": "algorithmic",
                        "confidence": 0.9
                    }
                ],
                "complexity_score": 0.6
            }
        }
    )
