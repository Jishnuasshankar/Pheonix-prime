"""
Advanced Deep Thinking Test Suite
Additional comprehensive tests for system stability and edge cases

Test Categories:
1. Advanced Error Handling
2. Concurrent Operations
3. Budget Enforcement
4. Complex Reasoning Chains
5. Integration Scenarios
6. Performance Under Load

Follows AGENTS.md strict requirements:
- No placeholders
- Full error handling
- Structured logging validation
- Type safety checks
"""

import pytest
import asyncio
import time
from datetime import datetime
from typing import Dict, List
import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.reasoning import (
    DualProcessEngine,
    ThinkingMode,
    ThinkingDecision,
    ReasoningChain,
    ReasoningStep,
    ReasoningStrategy,
    DynamicBudgetAllocator,
    TokenBudget,
    BudgetConfig,
    BudgetMode,
    MCTSReasoningEngine,
    MCTSNode,
    ReasoningPath,
    MetacognitiveController
)
from core.models import EmotionState, LearningReadiness


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def dual_process_engine():
    """Initialize dual process engine"""
    return DualProcessEngine(db=None)


@pytest.fixture
def budget_allocator():
    """Initialize budget allocator"""
    return DynamicBudgetAllocator()


@pytest.fixture
def emotion_extreme_anxiety():
    """Extreme anxiety state (edge case)"""
    return EmotionState(
        primary_emotion="anxious",
        secondary_emotions=["overwhelmed", "panicked"],
        emotional_intensity=1.0,
        valence=-1.0,
        arousal=1.0,
        dominance=0.0,
        learning_readiness=LearningReadiness.NOT_READY,
        cognitive_load=1.0,
        flow_state="anxiety"
    )


@pytest.fixture
def emotion_peak_flow():
    """Peak flow state (edge case)"""
    return EmotionState(
        primary_emotion="focused",
        secondary_emotions=["engaged", "motivated"],
        emotional_intensity=0.9,
        valence=1.0,
        arousal=0.8,
        dominance=1.0,
        learning_readiness=LearningReadiness.OPTIMAL_READINESS,
        cognitive_load=0.1,
        flow_state="flow"
    )


# ============================================================================
# 1. ADVANCED ERROR HANDLING TESTS
# ============================================================================

class TestAdvancedErrorHandling:
    """Test robust error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_null_emotion_state_handling(self, dual_process_engine):
        """Test handling of None emotion state"""
        query = "What is machine learning?"
        
        # Should handle gracefully with default values
        decision = await dual_process_engine.select_thinking_mode(
            query=query,
            emotion_state=None,  # None input
            cognitive_load=0.5,
            learning_readiness=LearningReadiness.MODERATE_READINESS
        )
        
        assert decision is not None
        assert decision.mode in [ThinkingMode.SYSTEM1, ThinkingMode.HYBRID, ThinkingMode.SYSTEM2]
        assert 0.0 <= decision.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_extreme_cognitive_load_values(self, dual_process_engine, emotion_peak_flow):
        """Test handling of out-of-range cognitive load"""
        query = "Simple question"
        
        # Test values outside normal range - should raise ValueError
        for load in [-0.5, 1.5, 10.0]:
            with pytest.raises(ValueError, match="Cognitive load must be 0-1"):
                await dual_process_engine.select_thinking_mode(
                    query=query,
                    emotion_state=emotion_peak_flow,
                    cognitive_load=load,
                    learning_readiness=LearningReadiness.OPTIMAL_READINESS
                )
    
    @pytest.mark.asyncio
    async def test_malformed_query_characters(self, dual_process_engine, emotion_peak_flow):
        """Test handling of special characters and unicode"""
        queries = [
            "What is 2+2? 🤔",
            "Explain ∑(n=1 to ∞) 1/n²",
            "How does λ calculus work?",
            "Test with\nnewlines\tand\ttabs",
            "Test with <html> & special chars",
        ]
        
        for query in queries:
            decision = await dual_process_engine.select_thinking_mode(
                query=query,
                emotion_state=emotion_peak_flow,
                cognitive_load=0.3,
                learning_readiness=LearningReadiness.OPTIMAL_READINESS
            )
            
            assert decision is not None
            assert 0.0 <= decision.complexity_score <= 1.0
    
    def test_budget_allocator_extreme_inputs(self, budget_allocator):
        """Test budget allocator with extreme edge cases"""
        extreme_cases = [
            # (complexity, emotion_intensity, cognitive_load, expected_valid)
            (0.0, 0.0, 0.0, True),  # All minimum
            (1.0, 1.0, 1.0, True),  # All maximum
            (-0.5, 0.5, 0.5, True),  # Negative complexity
            (0.5, -0.5, 0.5, True),  # Negative emotion
            (2.0, 0.5, 2.0, True),  # Values over 1.0
        ]
        
        for complexity, emotion, load, should_be_valid in extreme_cases:
            try:
                # Create mock emotion state
                emotion_state = EmotionState(
                    primary_emotion="neutral",
                    secondary_emotions=[],
                    emotional_intensity=max(0.0, min(1.0, emotion)),
                    valence=0.0,
                    arousal=0.5,
                    dominance=0.5,
                    learning_readiness=LearningReadiness.MODERATE_READINESS,
                    cognitive_load=max(0.0, min(1.0, load)),
                    flow_state="not_in_flow"
                )
                
                budget = budget_allocator.allocate_budget(
                    emotion_state=emotion_state,
                    cognitive_load=max(0.0, min(1.0, load)),
                    complexity=max(0.0, min(1.0, complexity)),
                    learning_readiness=LearningReadiness.MODERATE_READINESS
                )
                
                assert budget is not None
                assert budget.total_tokens > 0
                assert budget.reasoning_tokens >= 0
                assert budget.response_tokens > 0
                
            except Exception as e:
                if should_be_valid:
                    pytest.fail(f"Should handle case ({complexity}, {emotion}, {load}): {e}")


# ============================================================================
# 2. CONCURRENT OPERATIONS TESTS
# ============================================================================

class TestConcurrentOperations:
    """Test thread safety and concurrent processing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_thinking_mode_selection(self, dual_process_engine, emotion_peak_flow):
        """Test multiple simultaneous thinking mode selections"""
        queries = [
            "What is water?",
            "Explain quantum mechanics",
            "How does photosynthesis work?",
            "Prove Fermat's Last Theorem",
            "What is the capital of France?",
        ] * 4  # 20 total queries
        
        # Run all selections concurrently
        tasks = [
            dual_process_engine.select_thinking_mode(
                query=query,
                emotion_state=emotion_peak_flow,
                cognitive_load=0.3,
                learning_readiness=LearningReadiness.OPTIMAL_READINESS
            )
            for query in queries
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # Verify all completed successfully
        assert len(results) == 20
        successful = [r for r in results if isinstance(r, ThinkingDecision)]
        assert len(successful) == 20
        
        # Should complete reasonably fast (not serialized)
        assert elapsed < 2.0  # 20 operations in under 2 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_budget_allocation(self, budget_allocator):
        """Test concurrent budget allocations"""
        emotion_state = EmotionState(
            primary_emotion="focused",
            secondary_emotions=[],
            emotional_intensity=0.7,
            valence=0.5,
            arousal=0.6,
            dominance=0.7,
            learning_readiness=LearningReadiness.OPTIMAL_READINESS,
            cognitive_load=0.4,
            flow_state="flow"
        )
        
        # Run 50 concurrent allocations
        def allocate_with_index(idx):
            return budget_allocator.allocate_budget(
                emotion_state=emotion_state,
                cognitive_load=0.4,
                complexity=idx / 100.0,
                learning_readiness=LearningReadiness.OPTIMAL_READINESS
            )
        
        tasks = [
            asyncio.create_task(asyncio.to_thread(allocate_with_index, i))
            for i in range(50)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        successful = [r for r in results if isinstance(r, TokenBudget)]
        assert len(successful) == 50


# ============================================================================
# 3. BUDGET ENFORCEMENT TESTS
# ============================================================================

class TestBudgetEnforcement:
    """Test strict budget enforcement and limits"""
    
    def test_budget_never_exceeds_provider_limits(self, budget_allocator):
        """Ensure budgets never exceed provider token limits"""
        config = BudgetConfig(provider_max_tokens=4096)
        allocator = DynamicBudgetAllocator(config=config)
        
        # Test with extreme complexity
        emotion_state = EmotionState(
            primary_emotion="confused",
            secondary_emotions=["overwhelmed"],
            emotional_intensity=1.0,
            valence=-1.0,
            arousal=1.0,
            dominance=0.0,
            learning_readiness=LearningReadiness.NOT_READY,
            cognitive_load=1.0,
            flow_state="anxiety"
        )
        
        budget = allocator.allocate_budget(
            emotion_state=emotion_state,
            cognitive_load=1.0,
            complexity=1.0,
            learning_readiness=LearningReadiness.NOT_READY
        )
        
        # Should respect provider limits even with extreme inputs
        assert budget.total_tokens <= config.provider_max_tokens
        assert budget.total_tokens <= config.provider_max_tokens * config.safety_margin
    
    def test_reasoning_response_split_consistency(self, budget_allocator):
        """Ensure reasoning + response always equals total"""
        emotion_state = EmotionState(
            primary_emotion="neutral",
            secondary_emotions=[],
            emotional_intensity=0.5,
            valence=0.0,
            arousal=0.5,
            dominance=0.5,
            learning_readiness=LearningReadiness.MODERATE_READINESS,
            cognitive_load=0.5,
            flow_state="not_in_flow"
        )
        
        # Test across complexity spectrum
        for complexity in [0.1, 0.3, 0.5, 0.7, 0.9]:
            budget = budget_allocator.allocate_budget(
                emotion_state=emotion_state,
                cognitive_load=0.5,
                complexity=complexity,
                learning_readiness=LearningReadiness.MODERATE_READINESS
            )
            
            # Strict equality check
            assert budget.reasoning_tokens + budget.response_tokens == budget.total_tokens
            
            # Reasoning should be meaningful portion
            assert budget.reasoning_tokens > 0
            assert budget.response_tokens > 0
    
    def test_budget_mode_boundaries(self, budget_allocator):
        """Test budget mode selection boundaries"""
        emotion_struggling = EmotionState(
            primary_emotion="confused",
            secondary_emotions=["frustrated"],
            emotional_intensity=0.8,
            valence=-0.6,
            arousal=0.7,
            dominance=0.2,
            learning_readiness=LearningReadiness.LOW_READINESS,
            cognitive_load=0.9,
            flow_state="anxiety"
        )
        
        emotion_confident = EmotionState(
            primary_emotion="confident",
            secondary_emotions=["engaged"],
            emotional_intensity=0.8,
            valence=0.8,
            arousal=0.6,
            dominance=0.9,
            learning_readiness=LearningReadiness.OPTIMAL_READINESS,
            cognitive_load=0.2,
            flow_state="flow"
        )
        
        # Struggling student should get AGGRESSIVE budget
        budget_struggling = budget_allocator.allocate_budget(
            emotion_state=emotion_struggling,
            cognitive_load=0.9,
            complexity=0.8,
            learning_readiness=LearningReadiness.LOW_READINESS
        )
        
        # Confident student with simple query should get CONSERVATIVE
        budget_confident = budget_allocator.allocate_budget(
            emotion_state=emotion_confident,
            cognitive_load=0.2,
            complexity=0.2,
            learning_readiness=LearningReadiness.OPTIMAL_READINESS
        )
        
        assert budget_struggling.mode == BudgetMode.AGGRESSIVE
        assert budget_confident.mode == BudgetMode.CONSERVATIVE
        assert budget_struggling.total_tokens > budget_confident.total_tokens


# ============================================================================
# 4. COMPLEX REASONING CHAIN TESTS
# ============================================================================

class TestComplexReasoningChains:
    """Test complex multi-step reasoning scenarios"""
    
    def test_deep_reasoning_chain_construction(self):
        """Test building deep reasoning chains with multiple strategies"""
        chain = ReasoningChain(
            query="Prove that the square root of 2 is irrational",
            total_time_ms=5000.0,
            total_tokens=3500
        )
        
        # Add 20 reasoning steps with various strategies
        # Use strategies that exist in the enum
        strategies = [
            ReasoningStrategy.DEDUCTIVE,
            ReasoningStrategy.INDUCTIVE,
            ReasoningStrategy.ANALOGICAL,
            ReasoningStrategy.ABDUCTIVE,
            ReasoningStrategy.CAUSAL
        ]
        
        for i in range(20):
            step = ReasoningStep(
                step_number=i + 1,
                strategy=strategies[i % len(strategies)],
                content=f"Reasoning step {i + 1} using {strategies[i % len(strategies)].value}",
                confidence=0.7 + (i * 0.01),  # Increasing confidence
                processing_time_ms=200 + (i * 20)
            )
            chain.add_step(step)
        
        chain.conclusion = "Therefore, √2 is irrational."
        chain.completed_at = datetime.utcnow()
        
        assert chain.conclusion is not None
        assert len(chain.steps) == 20
        
        # Check average confidence increases
        total_conf = sum(s.confidence for s in chain.steps)
        avg_conf = total_conf / len(chain.steps)
        assert 0.7 < avg_conf < 0.9
        
        # Verify strategy distribution
        dist = chain.get_strategy_distribution()
        assert len(dist) == 5  # All 5 strategies used
        assert all(count == 4 for count in dist.values())  # Each used 4 times
    
    def test_reasoning_chain_serialization_with_complex_data(self):
        """Test serialization with unicode, special chars, etc."""
        chain = ReasoningChain(
            query="Test with unicode: 🔬 and math: ∫∑∏",
            processing_time_ms=1000.0,
            token_budget_allocated=500
        )
        
        step = ReasoningStep(
            step_number=1,
            strategy=ReasoningStrategy.DEDUCTIVE,
            content="Analysis with special characters: <>&\"'\n\t",
            confidence=0.8,
            processing_time_ms=200
        )
        chain.add_step(step)
        chain.conclusion = "Test conclusion with λ"
        chain.completed_at = datetime.utcnow()
        
        # Should serialize without errors using Pydantic model_dump
        serialized = chain.model_dump()
        
        assert serialized is not None
        assert 'query' in serialized
        assert 'steps' in serialized
        assert len(serialized['steps']) == 1


# ============================================================================
# 5. REAL-WORLD INTEGRATION SCENARIOS
# ============================================================================

class TestRealWorldIntegration:
    """Test realistic end-to-end scenarios"""
    
    @pytest.mark.asyncio
    async def test_student_progression_scenario(self, dual_process_engine):
        """Simulate student progressing from confused to confident"""
        query = "Explain derivatives in calculus"
        
        # Stage 1: Confused student (should get System 2)
        emotion_confused = EmotionState(
            primary_emotion="confused",
            secondary_emotions=["frustrated"],
            emotional_intensity=0.7,
            valence=-0.5,
            arousal=0.6,
            dominance=0.3,
            learning_readiness=LearningReadiness.LOW_READINESS,
            cognitive_load=0.8,
            flow_state="anxiety"
        )
        
        decision1 = await dual_process_engine.select_thinking_mode(
            query=query,
            emotion_state=emotion_confused,
            cognitive_load=0.8,
            learning_readiness=LearningReadiness.LOW_READINESS
        )
        
        # Stage 2: Understanding (should get Hybrid)
        emotion_learning = EmotionState(
            primary_emotion="curious",
            secondary_emotions=["engaged"],
            emotional_intensity=0.6,
            valence=0.3,
            arousal=0.5,
            dominance=0.5,
            learning_readiness=LearningReadiness.MODERATE_READINESS,
            cognitive_load=0.5,
            flow_state="not_in_flow"
        )
        
        decision2 = await dual_process_engine.select_thinking_mode(
            query=query,
            emotion_state=emotion_learning,
            cognitive_load=0.5,
            learning_readiness=LearningReadiness.MODERATE_READINESS
        )
        
        # Stage 3: Confident (could get System 1 or Hybrid for same query)
        emotion_confident = EmotionState(
            primary_emotion="confident",
            secondary_emotions=["motivated"],
            emotional_intensity=0.8,
            valence=0.8,
            arousal=0.6,
            dominance=0.8,
            learning_readiness=LearningReadiness.OPTIMAL_READINESS,
            cognitive_load=0.2,
            flow_state="flow"
        )
        
        decision3 = await dual_process_engine.select_thinking_mode(
            query=query,
            emotion_state=emotion_confident,
            cognitive_load=0.2,
            learning_readiness=LearningReadiness.OPTIMAL_READINESS
        )
        
        # Verify progression: System2 → Hybrid → (System1 or Hybrid)
        assert decision1.mode == ThinkingMode.SYSTEM2
        assert decision2.mode == ThinkingMode.HYBRID
        assert decision3.mode in [ThinkingMode.SYSTEM1, ThinkingMode.HYBRID]
        
        # Token allocation should decrease as confidence increases
        assert decision1.estimated_tokens > decision2.estimated_tokens
        assert decision2.estimated_tokens >= decision3.estimated_tokens
    
    @pytest.mark.asyncio
    async def test_rapid_fire_questions_scenario(self, dual_process_engine, emotion_peak_flow):
        """Simulate rapid Q&A session (latency critical)"""
        questions = [
            "What is 5*7?",
            "What is the capital of Germany?",
            "How many days in a week?",
            "What is H2O?",
            "Who wrote Romeo and Juliet?"
        ]
        
        start_time = time.time()
        
        decisions = []
        for query in questions:
            decision = await dual_process_engine.select_thinking_mode(
                query=query,
                emotion_state=emotion_peak_flow,
                cognitive_load=0.2,
                learning_readiness=LearningReadiness.OPTIMAL_READINESS
            )
            decisions.append(decision)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # All should be System 1 (simple factual questions)
        assert all(d.mode == ThinkingMode.SYSTEM1 for d in decisions)
        
        # Total latency should be minimal (under 50ms total for 5 queries)
        assert elapsed_ms < 50.0


# ============================================================================
# 6. PERFORMANCE UNDER LOAD TESTS
# ============================================================================

class TestPerformanceUnderLoad:
    """Test system performance under stress"""
    
    @pytest.mark.asyncio
    async def test_high_volume_processing(self, dual_process_engine):
        """Test processing 100 queries rapidly"""
        emotion_state = EmotionState(
            primary_emotion="neutral",
            secondary_emotions=[],
            emotional_intensity=0.5,
            valence=0.0,
            arousal=0.5,
            dominance=0.5,
            learning_readiness=LearningReadiness.MODERATE_READINESS,
            cognitive_load=0.5,
            flow_state="not_in_flow"
        )
        
        queries = [f"Test query number {i}" for i in range(100)]
        
        start_time = time.time()
        
        tasks = [
            dual_process_engine.select_thinking_mode(
                query=query,
                emotion_state=emotion_state,
                cognitive_load=0.5,
                learning_readiness=LearningReadiness.MODERATE_READINESS
            )
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # All should complete successfully
        successful = [r for r in results if isinstance(r, ThinkingDecision)]
        assert len(successful) == 100
        
        # Should maintain reasonable throughput
        avg_time_per_query = elapsed / 100
        assert avg_time_per_query < 0.05  # Under 50ms average per query
        
        logging.info(f"✅ Processed 100 queries in {elapsed:.2f}s ({avg_time_per_query*1000:.1f}ms avg)")
    
    def test_memory_efficiency_large_chains(self):
        """Test memory usage doesn't explode with large chains"""
        chains = []
        
        # Create 50 chains with 50 steps each
        for chain_idx in range(50):
            chain = ReasoningChain(
                query=f"Chain {chain_idx}",
                total_time_ms=5000.0,
                total_tokens=2500
            )
            
            for step_idx in range(50):
                step = ReasoningStep(
                    step_number=step_idx + 1,
                    strategy=ReasoningStrategy.DEDUCTIVE,
                    content=f"Step {step_idx + 1} content" * 10,  # Some content
                    confidence=0.8,
                    tokens_used=50,
                    time_ms=100
                )
                chain.add_step(step)
            
            chain.mark_complete(conclusion="Conclusion")
            chains.append(chain)
        
        # Should complete without memory errors
        assert len(chains) == 50
        total_steps = sum(len(c.steps) for c in chains)
        assert total_steps == 2500  # 50 chains * 50 steps
        
        logging.info(f"✅ Created {total_steps} reasoning steps across {len(chains)} chains")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
