"""
MasterX Deep Thinking - Reasoning Module
Implements visible thinking, MCTS, dynamic budgets

Following AGENTS.md principles:
- Zero hardcoded values
- ML-driven decisions
- Type hints throughout
- PEP8 compliant
"""

from .dual_process import (
    DualProcessEngine,
    ThinkingMode,
    ThinkingDecision
)

from .reasoning_chain import (
    ReasoningChain,
    ReasoningStep,
    ReasoningStrategy
)

from .budget_allocator import (
    DynamicBudgetAllocator,
    TokenBudget,
    BudgetConfig,
    BudgetMode
)

from .mcts_engine import (
    MCTSReasoningEngine,
    MCTSNode,
    ReasoningPath
)

from .metacognitive_controller import (
    MetacognitiveController
)

from .streaming_engine import (
    StreamingReasoningEngine
)

__all__ = [
    # Dual Process
    'DualProcessEngine',
    'ThinkingMode',
    'ThinkingDecision',
    
    # Reasoning Chain
    'ReasoningChain',
    'ReasoningStep',
    'ReasoningStrategy',
    
    # Budget
    'DynamicBudgetAllocator',
    'TokenBudget',
    'BudgetConfig',
    'BudgetMode',
    
    # MCTS
    'MCTSReasoningEngine',
    'MCTSNode',
    'ReasoningPath',
    
    # Metacognitive
    'MetacognitiveController',
    
    # Streaming
    'StreamingReasoningEngine'
]

__version__ = "1.0.0"
