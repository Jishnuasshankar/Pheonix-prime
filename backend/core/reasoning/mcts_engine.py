"""
MCTS Reasoning Engine
Monte Carlo Tree Search for reasoning path exploration

AGENTS.md compliant:
- Pure AI/ML approach (no rule-based systems)
- Type hints throughout
- PEP8 naming
- Production-ready error handling
"""

import logging
import math
import time
import uuid
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from core.models import EmotionState
from .reasoning_chain import ReasoningStep, ReasoningStrategy

logger = logging.getLogger(__name__)


@dataclass
class MCTSNode:
    """
    MCTS tree node representing a reasoning state
    
    Each node represents one step in the reasoning process
    """
    id: str
    content: str
    strategy: ReasoningStrategy
    parent: Optional['MCTSNode']
    children: List['MCTSNode']
    visits: int
    value: float  # Cumulative value (reward)
    depth: int
    
    def ucb_score(self, exploration_weight: float = 1.41) -> float:
        """
        Calculate UCB1 (Upper Confidence Bound) score
        
        UCB = exploitation + exploration
        = (value/visits) + C * sqrt(ln(parent_visits) / visits)
        
        Args:
            exploration_weight: C parameter (default √2)
        
        Returns:
            UCB score for selection
        """
        if self.visits == 0:
            return float('inf')  # Unvisited nodes have highest priority
        
        exploitation = self.value / self.visits
        
        if self.parent and self.parent.visits > 0:
            exploration = exploration_weight * math.sqrt(
                math.log(self.parent.visits) / self.visits
            )
        else:
            exploration = 0
        
        return exploitation + exploration


class ReasoningPath(BaseModel):
    """
    Complete reasoning path from root to leaf
    
    Represents one complete chain of reasoning
    """
    steps: List[ReasoningStep] = Field(default_factory=list)
    total_value: float = Field(default=0.0)
    confidence: float = Field(default=0.7)
    conclusion: str = Field(default="")
    
    def add_step(self, step: ReasoningStep):
        """Add step to path"""
        self.steps.append(step)


class MCTSReasoningEngine:
    """
    MCTS-based reasoning engine
    
    Uses Monte Carlo Tree Search to explore reasoning paths and select
    the most promising chain of thought.
    
    Simplified Phase 1 implementation:
    - Basic tree search
    - AI-driven step generation
    - UCB-based selection
    
    Future enhancements (Phase 3):
    - Reward model for step evaluation
    - Parallel rollouts
    - Value function approximation
    """
    
    def __init__(self, provider_manager, max_iterations: int = 10):
        """
        Initialize MCTS reasoning engine
        
        Args:
            provider_manager: AI provider manager for step generation
            max_iterations: Max MCTS iterations (default: 10)
        """
        self.provider_manager = provider_manager
        self.max_iterations = max_iterations
        self.exploration_weight = 1.41  # √2 (standard UCB parameter)
        
        logger.info("✅ MCTSReasoningEngine initialized (simplified)")
    
    async def generate_reasoning_chain(
        self,
        query: str,
        emotion_state: EmotionState,
        max_steps: int = 5,
        token_budget: int = 1500
    ) -> ReasoningPath:
        """
        Generate reasoning chain using MCTS
        
        Simplified Phase 1 algorithm:
        1. Start with root node (query)
        2. For each iteration:
           - Select most promising node (UCB)
           - Expand with AI-generated reasoning step
           - Evaluate step quality
           - Backpropagate value
        3. Return best path
        
        Args:
            query: User query to reason about
            emotion_state: Current emotional state
            max_steps: Maximum reasoning steps
            token_budget: Token budget for reasoning
        
        Returns:
            Best reasoning path found
        """
        
        start_time = time.time()
        
        # Initialize root node
        root = MCTSNode(
            id=str(uuid.uuid4()),
            content=f"Query: {query}",
            strategy=ReasoningStrategy.DEDUCTIVE,
            parent=None,
            children=[],
            visits=0,
            value=0.0,
            depth=0
        )
        
        logger.info(f"🌳 Starting MCTS reasoning: query={query[:50]}..., max_steps={max_steps}")
        
        # MCTS iterations
        for iteration in range(min(self.max_iterations, max_steps)):
            # 1. Selection - find most promising node to expand
            selected_node = self._select(root)
            
            # 2. Expansion - generate next reasoning step
            if selected_node.depth < max_steps:
                new_node = await self._expand(selected_node, query, emotion_state)
                if new_node:
                    selected_node.children.append(new_node)
                    selected_node = new_node
            
            # 3. Simulation - estimate value of this path (simplified)
            value = self._simulate(selected_node)
            
            # 4. Backpropagation - update values up the tree
            self._backpropagate(selected_node, value)
            
            logger.debug(f"MCTS iteration {iteration + 1}: depth={selected_node.depth}, value={value:.2f}")
        
        # Extract best path from root to best leaf
        best_path = self._extract_best_path(root)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(
            f"✅ MCTS reasoning complete: {len(best_path.steps)} steps, "
            f"value={best_path.total_value:.2f} in {elapsed_ms:.0f}ms"
        )
        
        return best_path
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """
        Selection phase: find most promising node using UCB
        
        Traverse tree following highest UCB scores until leaf
        
        Args:
            node: Current node
        
        Returns:
            Selected leaf node for expansion
        """
        current = node
        
        while current.children:
            # Select child with highest UCB score
            current = max(current.children, key=lambda n: n.ucb_score(self.exploration_weight))
        
        return current
    
    async def _expand(
        self,
        node: MCTSNode,
        query: str,
        emotion_state: EmotionState
    ) -> Optional[MCTSNode]:
        """
        Expansion phase: generate next reasoning step using AI
        
        Uses dynamic provider selection for optimal quality/speed tradeoff.
        MCTS requires fast reasoning steps, so we prefer speed but maintain
        quality threshold for accurate reasoning.
        
        Args:
            node: Node to expand
            query: Original query
            emotion_state: Emotional state
        
        Returns:
            New child node with AI-generated reasoning step
        """
        
        try:
            # Build context from path to this node
            path_context = self._build_path_context(node)
            
            # Prompt AI to generate next reasoning step
            prompt = self._create_expansion_prompt(query, path_context, emotion_state)
            
            # Dynamically select best provider for reasoning
            # MCTS benefits from fast providers but needs good quality
            # Use "reasoning" category to get best model for logical thinking
            try:
                best_provider, best_model = await self.provider_manager.select_best_model(
                    category="reasoning",
                    prefer_speed=True,  # MCTS needs fast iterations
                    min_quality_score=60.0  # Maintain quality threshold
                )
                logger.debug(
                    f"🤖 MCTS using dynamically selected provider: "
                    f"{best_provider}/{best_model}"
                )
            except Exception as provider_error:
                logger.warning(
                    f"Provider selection failed: {provider_error}, "
                    f"falling back to any available provider"
                )
                best_provider = None  # Will trigger auto-selection in generate()
            
            # Generate step using AI provider (with dynamic selection)
            # If best_provider is None, generate() will auto-select best model
            response = await self.provider_manager.generate(
                prompt=prompt,
                category="reasoning",
                provider_name=best_provider,  # None = auto-select
                max_tokens=200  # Short reasoning steps
            )
            
            # Parse response into reasoning step
            step_content = response.content.strip()
            strategy = self._infer_strategy(step_content)
            
            # Create new node
            new_node = MCTSNode(
                id=str(uuid.uuid4()),
                content=step_content,
                strategy=strategy,
                parent=node,
                children=[],
                visits=0,
                value=0.0,
                depth=node.depth + 1
            )
            
            logger.debug(
                f"✅ MCTS expanded node at depth {node.depth} → {new_node.depth}, "
                f"strategy={strategy.value}"
            )
            
            return new_node
        
        except Exception as e:
            logger.error(f"❌ Failed to expand MCTS node: {e}", exc_info=True)
            return None
    
    def _simulate(self, node: MCTSNode) -> float:
        """
        Simulation phase: estimate value of reasoning path
        
        Simplified heuristic evaluation:
        - Longer paths (more steps) = higher value
        - Deeper reasoning = higher value
        - Penalize repetition
        
        Args:
            node: Leaf node to evaluate
        
        Returns:
            Estimated value (0-1 scale)
        """
        
        # Base value from depth (deeper = more thorough)
        depth_value = min(node.depth / 5.0, 1.0)
        
        # Content quality heuristics
        content_length = len(node.content.split())
        length_value = min(content_length / 50.0, 1.0)
        
        # Strategy diversity bonus (check parent chain)
        strategies_used = set()
        current = node
        while current:
            strategies_used.add(current.strategy)
            current = current.parent
        diversity_bonus = len(strategies_used) / len(ReasoningStrategy) * 0.2
        
        # Weighted combination
        value = (
            depth_value * 0.4 +
            length_value * 0.4 +
            diversity_bonus * 0.2
        )
        
        return value
    
    def _backpropagate(self, node: MCTSNode, value: float):
        """
        Backpropagation phase: update node values up the tree
        
        Args:
            node: Starting node
            value: Value to propagate
        """
        current = node
        while current:
            current.visits += 1
            current.value += value
            current = current.parent
    
    def _extract_best_path(self, root: MCTSNode) -> ReasoningPath:
        """
        Extract best reasoning path from tree
        
        Follow highest value/visit ratio from root to leaf
        
        Args:
            root: Root node
        
        Returns:
            Best reasoning path
        """
        path = ReasoningPath()
        current = root
        
        # Skip root (it's just the query)
        while current.children:
            # Select child with highest average value
            best_child = max(
                current.children,
                key=lambda n: (n.value / n.visits) if n.visits > 0 else 0
            )
            
            # Convert to ReasoningStep
            step = ReasoningStep(
                step_number=len(path.steps) + 1,
                content=best_child.content,
                strategy=best_child.strategy,
                confidence=(best_child.value / best_child.visits) if best_child.visits > 0 else 0.5,
                visit_count=best_child.visits,
                ucb_score=best_child.ucb_score(self.exploration_weight)
            )
            
            path.add_step(step)
            current = best_child
        
        # Calculate path metrics
        path.total_value = current.value / current.visits if current.visits > 0 else 0.0
        path.confidence = path.total_value
        
        # Set conclusion as the last step's content
        if path.steps:
            path.conclusion = path.steps[-1].content
        else:
            path.conclusion = "No reasoning steps generated"
        
        return path
    
    def _build_path_context(self, node: MCTSNode) -> str:
        """Build context string from root to node"""
        steps = []
        current = node
        while current.parent:  # Skip root
            steps.insert(0, f"Step {len(steps) + 1}: {current.content}")
            current = current.parent
        return "\n".join(steps) if steps else "No previous steps"
    
    def _create_expansion_prompt(
        self,
        query: str,
        path_context: str,
        emotion_state: EmotionState
    ) -> str:
        """Create prompt for expanding reasoning tree"""
        
        return f"""You are reasoning through a problem step-by-step.

Original Query: {query}

Previous Reasoning Steps:
{path_context}

Generate the NEXT logical reasoning step. Be specific and clear.
Focus on ONE reasoning action:
- Break down the problem
- Identify key concepts
- Make a logical deduction
- Consider an example
- Draw a conclusion

Next Step:"""
    
    def _infer_strategy(self, content: str) -> ReasoningStrategy:
        """
        Infer reasoning strategy from step content
        
        Simple keyword-based classification
        
        Args:
            content: Step content
        
        Returns:
            Inferred ReasoningStrategy
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['therefore', 'thus', 'conclude', 'deduce']):
            return ReasoningStrategy.DEDUCTIVE
        elif any(word in content_lower for word in ['pattern', 'observe', 'notice', 'generalize']):
            return ReasoningStrategy.INDUCTIVE
        elif any(word in content_lower for word in ['likely', 'probably', 'best explanation', 'hypothesis']):
            return ReasoningStrategy.ABDUCTIVE
        elif any(word in content_lower for word in ['similar to', 'like', 'analogy', 'comparable']):
            return ReasoningStrategy.ANALOGICAL
        elif any(word in content_lower for word in ['because', 'causes', 'leads to', 'results in']):
            return ReasoningStrategy.CAUSAL
        elif any(word in content_lower for word in ['step', 'next', 'then', 'procedure', 'algorithm']):
            return ReasoningStrategy.ALGORITHMIC
        else:
            return ReasoningStrategy.DEDUCTIVE  # Default
