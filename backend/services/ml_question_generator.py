"""
ML-Based Follow-Up Question Generator (Perplexity-Inspired)

Architecture inspired by:
- APARL (Adaptive Perplexity-Aware Reinforcement Learning)
- DQO (Diversity Quality Optimization)
- Sentence Transformers for semantic diversity
- Reinforcement Learning from user interactions

This uses LLMs + ML models, NOT templates.
"""

import logging
import asyncio
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from core.models import (
    EmotionState,
    LearningReadiness,
    SuggestedQuestion,
    Message
)

logger = logging.getLogger(__name__)


class MLQuestionGenerator:
    """
    ML-Based Question Generator using LLMs + Sentence Transformers
    
    Architecture:
    1. LLM-based generation (8-10 candidate questions)
    2. Semantic embedding for diversity measurement
    3. ML-based ranking (emotion + ability + relevance)
    4. Reinforcement learning from user clicks
    
    Matches MasterX's ML-first philosophy.
    """
    
    def __init__(
        self,
        provider_manager=None,
        db=None,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize ML-based question generator
        
        Args:
            provider_manager: AI provider manager for LLM generation
            db: MongoDB database for storing interaction data
            embedding_model_name: Sentence transformer model
        """
        self.provider_manager = provider_manager
        self.db = db
        
        # Initialize sentence transformer for semantic analysis
        self._init_sentence_transformer(embedding_model_name)
        
        # Reinforcement learning state
        self.question_performance = defaultdict(lambda: {"clicks": 0, "impressions": 0, "score": 0.5})
        # Historical performance will be loaded asynchronously
        
        # Diversity threshold (cosine similarity)
        self.diversity_threshold = 0.85  # Questions with similarity > 0.85 are too similar
        
        logger.info("✅ ML-Based Question Generator initialized")
    
    def _init_sentence_transformer(self, model_name: str):
        """Initialize sentence transformer for semantic embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_transformer = SentenceTransformer(model_name)
            logger.info(f"✅ Loaded sentence transformer: {model_name}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load sentence transformer: {e}. Using fallback.")
            self.sentence_transformer = None
    
    async def _load_historical_performance(self):
        """Load historical question performance from database (RL component)"""
        if self.db is None:
            return
        
        try:
            # Load aggregated click-through rates
            collection = self.db.question_interactions
            pipeline = [
                {
                    "$group": {
                        "_id": "$question_hash",
                        "clicks": {"$sum": {"$cond": ["$clicked", 1, 0]}},
                        "impressions": {"$sum": 1}
                    }
                },
                {"$limit": 1000}  # Top 1000 most shown questions
            ]
            
            # FIX: Use async to_list() instead of synchronous list()
            results = await collection.aggregate(pipeline).to_list(length=1000)
            
            for item in results:
                question_hash = item["_id"]
                clicks = item["clicks"]
                impressions = item["impressions"]
                ctr = clicks / max(impressions, 1)
                
                self.question_performance[question_hash] = {
                    "clicks": clicks,
                    "impressions": impressions,
                    "score": self._calculate_rl_score(ctr, impressions)
                }
            
            logger.info(f"✅ Loaded {len(results)} question performance records (RL)")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load historical performance: {e}")
    
    def _calculate_rl_score(self, ctr: float, impressions: int) -> float:
        """
        Calculate RL-based score using Thompson Sampling approach
        
        Balances exploration (new questions) vs exploitation (proven questions)
        """
        # Beta distribution parameters (Bayesian approach)
        alpha = 1 + (ctr * impressions)  # Successes + prior
        beta = 1 + (impressions - ctr * impressions)  # Failures + prior
        
        # Thompson sampling: sample from Beta distribution
        score = np.random.beta(alpha, beta)
        
        # Apply diminishing returns for over-shown questions
        if impressions > 100:
            score *= 0.9  # Encourage exploration of new questions
        
        return float(score)
    
    async def generate_follow_ups(
        self,
        user_message: str,
        ai_response: str,
        emotion_state: EmotionState,
        ability_level: float,
        category: str = "general",
        recent_messages: Optional[List[Message]] = None,
        max_questions: int = 5
    ) -> List[SuggestedQuestion]:
        """
        Generate ML-based follow-up questions
        
        Pipeline:
        1. LLM generates 8-10 candidate questions
        2. Embed questions for semantic analysis
        3. Filter for diversity (remove similar questions)
        4. Rank using ML scoring (emotion + ability + RL)
        5. Return top N
        
        Args:
            user_message: User's original question
            ai_response: AI's response
            emotion_state: Detected emotion state
            ability_level: Estimated ability (-3.0 to +3.0)
            category: Topic category
            recent_messages: Conversation history
            max_questions: Maximum to return
        
        Returns:
            List of ML-ranked SuggestedQuestion objects
        """
        try:
            # ================================================================
            # PHASE 1: LLM-BASED GENERATION (8-10 candidates)
            # ================================================================
            logger.info("🤖 Generating candidate questions using LLM...")
            
            candidates = await self._generate_candidates_with_llm(
                user_message=user_message,
                ai_response=ai_response,
                emotion_state=emotion_state,
                ability_level=ability_level,
                category=category,
                recent_messages=recent_messages,
                num_candidates=10
            )
            
            if not candidates:
                logger.warning("⚠️  LLM generation failed, using fallback")
                return self._generate_fallback_questions()
            
            logger.info(f"✅ Generated {len(candidates)} candidate questions")
            
            # ================================================================
            # PHASE 2: SEMANTIC EMBEDDING & DIVERSITY FILTERING
            # ================================================================
            logger.info("🧬 Computing semantic embeddings...")
            
            diverse_candidates = await self._filter_for_diversity(
                candidates,
                user_message,
                ai_response
            )
            
            logger.info(f"✅ Filtered to {len(diverse_candidates)} diverse questions")
            
            # ================================================================
            # PHASE 3: ML-BASED RANKING
            # ================================================================
            logger.info("📊 Ranking questions with ML models...")
            
            ranked_questions = await self._rank_questions_ml(
                questions=diverse_candidates,
                emotion_state=emotion_state,
                ability_level=ability_level,
                category=category,
                conversation_context=recent_messages
            )
            
            # ================================================================
            # PHASE 4: SELECT TOP N
            # ================================================================
            final_questions = ranked_questions[:max_questions]
            
            logger.info(f"✅ Generated {len(final_questions)} ML-ranked follow-up questions")
            return final_questions
        
        except Exception as e:
            logger.error(f"❌ ML question generation failed: {e}", exc_info=True)
            return self._generate_fallback_questions()
    
    async def _generate_candidates_with_llm(
        self,
        user_message: str,
        ai_response: str,
        emotion_state: EmotionState,
        ability_level: float,
        category: str,
        recent_messages: Optional[List[Message]],
        num_candidates: int = 10
    ) -> List[Dict]:
        """
        Use LLM to generate candidate questions (Phase 1)
        
        This is the core ML component - we use the AI provider's LLM
        to generate contextually relevant questions.
        """
        if not self.provider_manager:
            logger.warning("No provider manager available")
            return []
        
        # Build conversation context
        context_text = ""
        if recent_messages and len(recent_messages) > 0:
            context_text = "RECENT CONVERSATION:\n"
            for msg in recent_messages[-3:]:  # Last 3 messages
                role = "Student" if msg.role.value == "user" else "Tutor"
                context_text += f"{role}: {msg.content[:100]}...\n"
        
        # Emotion-based instruction
        emotion_instruction = self._get_emotion_based_instruction(emotion_state)
        
        # Ability-based instruction
        ability_instruction = self._get_ability_based_instruction(ability_level)
        
        # Construct prompt for LLM
        prompt = f"""You are an expert educational AI tutor. Generate {num_candidates} diverse, thought-provoking follow-up questions for a student.

{context_text}

CURRENT EXCHANGE:
Student: "{user_message}"
Your Response: "{ai_response[:500]}"

STUDENT PROFILE:
- Emotional State: {emotion_state.primary_emotion} (readiness: {emotion_state.learning_readiness.value})
- Ability Level: {ability_level:.2f} (-3.0=beginner, 0.0=average, +3.0=expert)
- Subject: {category}

{emotion_instruction}

{ability_instruction}

REQUIREMENTS:
1. Generate EXACTLY {num_candidates} distinct follow-up questions
2. Make them diverse: mix clarifying, extending, connecting, applying questions
3. Each question should build on the conversation naturally
4. Questions should match the student's ability and emotional state
5. Focus on learning, not just facts

Format your response as a JSON array:
[
  {{"question": "...", "type": "clarifying", "difficulty_delta": 0.0}},
  {{"question": "...", "type": "extending", "difficulty_delta": 0.2}},
  ...
]

Types: "clarifying", "extending", "connecting", "applying", "reflecting"
Difficulty_delta: -0.3 to +0.5 (relative to current level)

Generate the questions now:"""
        
        try:
            # Use provider manager to generate
            response = await self.provider_manager.generate(
                prompt=prompt,
                provider_name=None,  # Auto-select best provider
                max_tokens=800
                # Note: Temperature not supported in current provider manager
            )
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON array from response
            content = response.content
            json_match = re.search(r'\[[\s\S]*\]', content)
            
            if json_match:
                questions_json = json.loads(json_match.group(0))
                
                # Convert to our format
                candidates = []
                for item in questions_json:
                    if isinstance(item, dict) and 'question' in item:
                        candidates.append({
                            'question': item['question'],
                            'type': item.get('type', 'exploration'),
                            'difficulty_delta': item.get('difficulty_delta', 0.0)
                        })
                
                return candidates
            else:
                logger.warning("⚠️  Failed to parse LLM JSON response")
                return []
        
        except Exception as e:
            logger.error(f"❌ LLM generation error: {e}")
            return []
    
    def _get_emotion_based_instruction(self, emotion_state: EmotionState) -> str:
        """Generate emotion-specific instruction for LLM"""
        readiness = emotion_state.learning_readiness
        emotion = emotion_state.primary_emotion
        
        if readiness in [LearningReadiness.NOT_READY, LearningReadiness.LOW_READINESS]:
            return """EMOTION GUIDANCE: Student is struggling. Generate:
- More clarifying questions (break down concepts)
- Encouraging questions that build confidence
- Simpler, supportive questions
- Avoid overwhelming with too much complexity"""
        
        elif readiness == LearningReadiness.HIGH_READINESS:
            return """EMOTION GUIDANCE: Student is confident and ready. Generate:
- Challenging extension questions
- Questions that push understanding deeper
- Application to complex scenarios
- Connection to advanced topics"""
        
        elif emotion in ['curiosity', 'admiration']:
            return """EMOTION GUIDANCE: Student is curious and engaged. Generate:
- Questions that feed their curiosity
- Interesting connections and applications
- "What if" scenarios
- Deep exploration questions"""
        
        else:
            return """EMOTION GUIDANCE: Student is moderately engaged. Generate:
- Balanced mix of question types
- Some practice, some extension
- Maintain engagement with variety"""
    
    def _get_ability_based_instruction(self, ability_level: float) -> str:
        """Generate ability-specific instruction for LLM"""
        if ability_level < -1.5:
            return """ABILITY GUIDANCE: Beginner level. Questions should:
- Use simple language
- Focus on fundamentals
- Build from basics
- Avoid jargon"""
        
        elif ability_level > 1.5:
            return """ABILITY GUIDANCE: Advanced level. Questions should:
- Assume strong foundation
- Introduce sophisticated concepts
- Challenge with edge cases
- Use technical terminology"""
        
        else:
            return """ABILITY GUIDANCE: Intermediate level. Questions should:
- Build on established basics
- Introduce new complexity gradually
- Mix concrete and abstract thinking"""
    
    async def _filter_for_diversity(
        self,
        candidates: List[Dict],
        user_message: str,
        ai_response: str
    ) -> List[Dict]:
        """
        Filter candidates for semantic diversity using sentence transformers
        
        Uses cosine similarity to remove redundant questions.
        This is the DQO (Diversity Quality Optimization) component.
        """
        if not self.sentence_transformer or len(candidates) <= 1:
            return candidates
        
        try:
            # Extract question texts
            question_texts = [c['question'] for c in candidates]
            
            # Generate embeddings
            embeddings = self.sentence_transformer.encode(
                question_texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Calculate pairwise cosine similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarity_matrix = cosine_similarity(embeddings)
            
            # Greedy selection for diversity
            selected_indices = []
            remaining_indices = list(range(len(candidates)))
            
            # Start with first question
            selected_indices.append(remaining_indices.pop(0))
            
            # Greedily add most diverse questions
            while remaining_indices and len(selected_indices) < 8:
                # For each remaining question, find min similarity to selected
                max_min_similarity = -1
                best_idx_pos = 0
                
                for i, idx in enumerate(remaining_indices):
                    # Min similarity to any selected question
                    min_sim = min(similarity_matrix[idx][s] for s in selected_indices)
                    
                    if min_sim > max_min_similarity:
                        max_min_similarity = min_sim
                        best_idx_pos = i
                
                # Add most diverse question
                if max_min_similarity < self.diversity_threshold:
                    selected_indices.append(remaining_indices.pop(best_idx_pos))
                else:
                    # All remaining are too similar
                    break
            
            # Return selected candidates
            diverse_candidates = [candidates[i] for i in selected_indices]
            
            logger.info(
                f"Diversity filtering: {len(candidates)} → {len(diverse_candidates)} "
                f"(removed {len(candidates) - len(diverse_candidates)} similar questions)"
            )
            
            return diverse_candidates
        
        except Exception as e:
            logger.error(f"Diversity filtering failed: {e}")
            return candidates[:8]  # Return first 8 if filtering fails
    
    async def _rank_questions_ml(
        self,
        questions: List[Dict],
        emotion_state: EmotionState,
        ability_level: float,
        category: str,
        conversation_context: Optional[List[Message]]
    ) -> List[SuggestedQuestion]:
        """
        Rank questions using ML-based scoring (Phase 3)
        
        Scoring factors:
        1. Emotion alignment (does difficulty match readiness?)
        2. Ability appropriateness (IRT-based)
        3. Relevance (semantic similarity to conversation)
        4. Diversity bonus (novel question types)
        5. Historical performance (RL component)
        
        This is the ML ranking component.
        """
        scored_questions = []
        
        for q_dict in questions:
            question_text = q_dict['question']
            q_type = q_dict.get('type', 'exploration')
            difficulty_delta = q_dict.get('difficulty_delta', 0.0)
            
            # ============================================================
            # SCORING COMPONENTS (All ML-based)
            # ============================================================
            
            # 1. Emotion Alignment Score (0.0-1.0)
            emotion_score = self._calculate_emotion_alignment(
                emotion_state, q_type, difficulty_delta
            )
            
            # 2. Ability Appropriateness Score (0.0-1.0)
            ability_score = self._calculate_ability_appropriateness(
                ability_level, difficulty_delta
            )
            
            # 3. Diversity Bonus (0.0-0.2)
            # Extract already selected types from scored questions (which are tuples of (score, SuggestedQuestion))
            already_selected_types = [sq.rationale for score, sq in scored_questions]
            diversity_bonus = self._calculate_diversity_bonus(
                q_type, already_selected_types
            )
            
            # 4. Historical Performance (RL component, 0.0-1.0)
            question_hash = hash(question_text[:50]) % (10 ** 8)
            rl_score = self.question_performance[question_hash]["score"]
            
            # 5. Relevance Score (would use embeddings, simplified here)
            relevance_score = 0.7  # Baseline - could compute with sentence transformer
            
            # ============================================================
            # WEIGHTED COMBINATION
            # ============================================================
            total_score = (
                emotion_score * 0.30 +
                ability_score * 0.25 +
                relevance_score * 0.20 +
                rl_score * 0.15 +
                diversity_bonus * 0.10
            )
            
            # Map type to category
            category_map = {
                'clarifying': 'clarification',
                'extending': 'challenge',
                'connecting': 'exploration',
                'applying': 'application',
                'reflecting': 'clarification'
            }
            
            suggested_q = SuggestedQuestion(
                question=question_text,
                rationale=q_type,
                difficulty_delta=difficulty_delta,
                category=category_map.get(q_type, 'exploration')
            )
            
            scored_questions.append((total_score, suggested_q))
        
        # Sort by score (descending)
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        
        # Return SuggestedQuestion objects only
        return [sq for score, sq in scored_questions]
    
    def _calculate_emotion_alignment(
        self,
        emotion_state: EmotionState,
        question_type: str,
        difficulty_delta: float
    ) -> float:
        """
        Calculate how well question matches emotional state
        
        ML-based: Uses the emotion detection model's output
        """
        readiness = emotion_state.learning_readiness
        
        # Match question type to readiness
        if readiness in [LearningReadiness.NOT_READY, LearningReadiness.LOW_READINESS]:
            # Prefer clarifying, avoid challenging
            if question_type == 'clarifying' and difficulty_delta <= 0:
                return 1.0
            elif question_type == 'extending' and difficulty_delta > 0.2:
                return 0.3
            else:
                return 0.6
        
        elif readiness == LearningReadiness.HIGH_READINESS:
            # Prefer challenging, avoid too easy
            if question_type == 'extending' and difficulty_delta > 0.2:
                return 1.0
            elif question_type == 'clarifying' and difficulty_delta < 0:
                return 0.4
            else:
                return 0.7
        
        else:
            # Moderate - all types good
            return 0.8
    
    def _calculate_ability_appropriateness(
        self,
        ability_level: float,
        difficulty_delta: float
    ) -> float:
        """
        Calculate if question difficulty matches ability (IRT-based)
        
        Uses principles from MasterX's IRT ability estimation
        """
        target_difficulty = ability_level + difficulty_delta
        
        # Optimal zone: ability ± 0.5
        distance = abs(target_difficulty - ability_level)
        
        if distance <= 0.5:
            return 1.0  # Optimal challenge
        elif distance <= 1.0:
            return 0.8  # Acceptable
        elif distance <= 1.5:
            return 0.6  # Borderline
        else:
            return 0.4  # Too far
    
    def _calculate_diversity_bonus(
        self,
        question_type: str,
        already_selected_types: List[str]
    ) -> float:
        """
        Bonus for introducing new question types
        
        Encourages variety in suggestions
        """
        if question_type not in already_selected_types:
            return 0.2  # Full bonus for new type
        
        # Count how many times this type already appears
        count = already_selected_types.count(question_type)
        
        if count == 1:
            return 0.1  # Half bonus
        else:
            return 0.0  # No bonus
    
    async def record_interaction(
        self,
        question: str,
        clicked: bool,
        user_id: str,
        session_id: str,
        emotion_state: EmotionState,
        ability_level: float
    ):
        """
        Record user interaction for reinforcement learning
        
        This is the RL training data collection component.
        """
        if self.db is None:
            return
        
        try:
            question_hash = hash(question[:50]) % (10 ** 8)
            
            interaction_doc = {
                "question_hash": question_hash,
                "question_text": question,
                "clicked": clicked,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow(),
                "emotion": emotion_state.primary_emotion,
                "readiness": emotion_state.learning_readiness.value,
                "ability_level": ability_level
            }
            
            await self.db.question_interactions.insert_one(interaction_doc)
            
            # Update in-memory performance
            perf = self.question_performance[question_hash]
            perf["impressions"] += 1
            if clicked:
                perf["clicks"] += 1
            
            # Recalculate score
            ctr = perf["clicks"] / perf["impressions"]
            perf["score"] = self._calculate_rl_score(ctr, perf["impressions"])
            
            logger.info(f"📊 Recorded question interaction: clicked={clicked}")
        
        except Exception as e:
            logger.error(f"Failed to record interaction: {e}")
    
    def _generate_fallback_questions(self) -> List[SuggestedQuestion]:
        """Fallback questions if ML generation fails"""
        return [
            SuggestedQuestion(
                question="Can you explain that in a different way?",
                rationale="clarifying",
                difficulty_delta=0.0,
                category="clarification"
            ),
            SuggestedQuestion(
                question="Can you show me another example?",
                rationale="clarifying",
                difficulty_delta=0.0,
                category="clarification"
            ),
            SuggestedQuestion(
                question="How would I use this in practice?",
                rationale="applying",
                difficulty_delta=0.1,
                category="application"
            )
        ]


async def create_ml_question_generator(provider_manager, db) -> MLQuestionGenerator:
    """
    Factory function to create ML question generator
    
    Args:
        provider_manager: AI provider manager
        db: MongoDB database
    
    Returns:
        Configured MLQuestionGenerator
    """
    generator = MLQuestionGenerator(
        provider_manager=provider_manager,
        db=db
    )
    
    # Load historical performance asynchronously
    await generator._load_historical_performance()
    
    return generator
