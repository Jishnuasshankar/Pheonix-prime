"""
Context Management System for MasterX
Following specifications from 3.MASTERX_COMPREHENSIVE_PLAN.md Section 3

PURPOSE:
- Manage conversation history and context windows
- Implement memory systems (short-term, working, long-term)
- Context compression for token efficiency
- Semantic retrieval for relevant past interactions
- Token budget management

PRINCIPLES:
- No hardcoded values (all configurable)
- Real ML models (sentence-transformers for embeddings)
- Async/await patterns
- PEP8 compliant
- Clean naming conventions
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from sentence_transformers import SentenceTransformer
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.models import Message, MessageRole, EmotionState
from utils.errors import MasterXError

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Generate and manage text embeddings for semantic search
    Uses sentence-transformers for efficient embedding generation
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding engine
        
        Args:
            model_name: HuggingFace model for embeddings (default: all-MiniLM-L6-v2)
                       - Fast: 14ms per sentence
                       - Quality: Good for semantic search
                       - Size: 80MB
        """
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ Embedding model loaded (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise MasterXError(
                f"Failed to initialize embedding engine: {str(e)}",
                details={'model_name': model_name}
            )
    
    async def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector (numpy array)
        """
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self.model.encode,
                text
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise MasterXError(
                f"Failed to generate embedding: {str(e)}",
                details={'text_length': len(text)}
            )
    
    async def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
        
        Returns:
            Array of embeddings (shape: [n_texts, embedding_dim])
        """
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                texts
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise MasterXError(
                f"Failed to generate batch embeddings: {str(e)}",
                details={'batch_size': len(texts)}
            )
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Convert to 0-1 range
        return float((similarity + 1) / 2)


class TokenBudgetManager:
    """
    Manage token allocation for context windows
    Estimates tokens accurately using word-based approximation
    """
    
    def __init__(
        self,
        max_context_tokens: int = 8000,
        system_prompt_ratio: float = 0.15,
        context_ratio: float = 0.45,
        user_message_ratio: float = 0.10,
        response_ratio: float = 0.30
    ):
        """
        Initialize token budget manager
        
        Args:
            max_context_tokens: Maximum tokens for entire context
            system_prompt_ratio: Ratio reserved for system prompt
            context_ratio: Ratio reserved for conversation context
            user_message_ratio: Ratio reserved for current user message
            response_ratio: Ratio reserved for AI response
        """
        self.max_context_tokens = max_context_tokens
        self.system_prompt_ratio = system_prompt_ratio
        self.context_ratio = context_ratio
        self.user_message_ratio = user_message_ratio
        self.response_ratio = response_ratio
        
        # Calculate actual token budgets
        self.system_prompt_budget = int(max_context_tokens * system_prompt_ratio)
        self.context_budget = int(max_context_tokens * context_ratio)
        self.user_message_budget = int(max_context_tokens * user_message_ratio)
        self.response_budget = int(max_context_tokens * response_ratio)
        
        logger.info(
            f"Token budget initialized: "
            f"context={self.context_budget}, "
            f"system={self.system_prompt_budget}, "
            f"user={self.user_message_budget}, "
            f"response={self.response_budget}"
        )
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Uses word-based approximation (1 word ≈ 1.3 tokens)
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Word count approximation (industry standard: 1 word ≈ 1.3 tokens)
        words = len(text.split())
        tokens = int(words * 1.3)
        
        return tokens
    
    def fit_messages_to_budget(
        self,
        messages: List[Message],
        budget: int
    ) -> List[Message]:
        """
        Select messages that fit within token budget
        Prioritizes recent messages
        
        Args:
            messages: List of messages (sorted by timestamp)
            budget: Token budget
        
        Returns:
            Filtered list of messages that fit budget
        """
        if not messages:
            return []
        
        selected_messages = []
        total_tokens = 0
        
        # Start from most recent and work backwards
        for message in reversed(messages):
            message_tokens = self.estimate_tokens(message.content)
            
            if total_tokens + message_tokens <= budget:
                selected_messages.insert(0, message)
                total_tokens += message_tokens
            else:
                # Budget exceeded
                break
        
        logger.debug(
            f"Fitted {len(selected_messages)}/{len(messages)} messages "
            f"to budget ({total_tokens}/{budget} tokens)"
        )
        
        return selected_messages


class MemoryRetriever:
    """
    Semantic memory retrieval using vector embeddings
    Finds relevant past messages based on semantic similarity
    """
    
    def __init__(
        self, 
        embedding_engine: EmbeddingEngine, 
        db: AsyncIOMotorDatabase,
        vector_store: Optional["QdrantVectorStore"] = None
    ):
        """
        Initialize memory retriever
        
        Following MASTERX_PROJECT_AUDIT.md Section 1.1:
        - Uses Qdrant for fast semantic search when available
        - Falls back to MongoDB linear search if Qdrant unavailable
        
        Args:
            embedding_engine: Engine for generating embeddings
            db: MongoDB database instance
            vector_store: Qdrant vector store instance (None for MongoDB-only)
        """
        self.embedding_engine = embedding_engine
        self.db = db
        self.messages_collection = db.messages
        self.vector_store = vector_store
    
    async def find_relevant(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
        min_similarity: float = 0.6,
        time_window_days: int = 7
    ) -> List[Tuple[Message, float]]:
        """
        Find relevant messages from past conversations
        
        CRITICAL FIXES (Perplexity Enhancement Plan):
        - Ensure session_id type consistency
        - Proper error handling for embeddings
        - Enhanced logging for debugging
        - Graceful degradation on errors
        
        Args:
            query: Query text to search for
            session_id: Current session ID
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            time_window_days: Only search messages within this time window
        
        Returns:
            List of (Message, similarity_score) tuples
        """
        try:
            # CRITICAL: Ensure session_id is string
            session_id_str = str(session_id)
            
            logger.debug(f"🔎 Semantic search for session {session_id_str}: '{query[:50]}...'")
            
            # Generate query embedding
            query_embedding = await self.embedding_engine.embed_text(query)
            logger.debug(f"✅ Query embedding generated: dimension={len(query_embedding)}")
            
            # STRATEGY 1: Try Qdrant vector search first (fast, <50ms)
            # Following MASTERX_PROJECT_AUDIT.md Section 1.1
            if self.vector_store and self.vector_store._initialized:
                try:
                    logger.debug("🔵 Using Qdrant vector search (HNSW indexing)")
                    
                    # Calculate time window
                    cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
                    
                    # Search in Qdrant with filters
                    search_results = await self.vector_store.search(
                        query_embedding=query_embedding,
                        session_id=session_id_str,
                        limit=top_k,
                        score_threshold=min_similarity,
                        filter_params={
                            'timestamp': {'$gte': cutoff_date.isoformat()}
                        }
                    )
                    
                    if search_results:
                        # Fetch full message details from MongoDB
                        message_ids = [r['id'] for r in search_results]
                        cursor = self.messages_collection.find({
                            '_id': {'$in': message_ids},
                            'session_id': session_id_str
                        })
                        
                        messages_dict = {doc['_id']: doc for doc in await cursor.to_list(length=top_k)}
                        
                        # Build results with similarity scores
                        results = []
                        for result in search_results:
                            msg_doc = messages_dict.get(result['id'])
                            if msg_doc:
                                try:
                                    message = Message(
                                        id=msg_doc['_id'],
                                        session_id=msg_doc['session_id'],
                                        user_id=msg_doc['user_id'],
                                        role=MessageRole(msg_doc['role']),
                                        content=msg_doc['content'],
                                        timestamp=msg_doc['timestamp'],
                                        emotion_state=EmotionState(**msg_doc['emotion_state']) if msg_doc.get('emotion_state') else None,
                                        provider_used=msg_doc.get('provider_used'),
                                        response_time_ms=msg_doc.get('response_time_ms'),
                                        tokens_used=msg_doc.get('tokens_used'),
                                        cost=msg_doc.get('cost')
                                    )
                                    results.append((message, result['score']))
                                except Exception as e:
                                    logger.warning(f"⚠️  Failed to parse message: {e}")
                                    continue
                        
                        logger.debug(
                            f"✅ Qdrant search complete: found {len(results)} relevant messages "
                            f"(similarity >= {min_similarity})"
                        )
                        return results
                    
                except Exception as e:
                    logger.warning(f"⚠️  Qdrant search failed, falling back to MongoDB: {e}")
                    # Fall through to MongoDB strategy
            
            # STRATEGY 2: Fallback to MongoDB linear search (slower, O(n))
            logger.debug("📦 Using MongoDB linear search (fallback)")
            
            # Get recent messages from database (with embeddings)
            cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
            
            cursor = self.messages_collection.find({
                'session_id': session_id_str,  # CRITICAL: Use string type
                'timestamp': {'$gte': cutoff_date},
                'embedding': {'$exists': True, '$ne': None}
            }).sort('timestamp', -1).limit(100)  # Limit search space
            
            messages = await cursor.to_list(length=100)
            
            if not messages:
                logger.debug(f"No messages with embeddings found for session {session_id_str}")
                return []
            
            logger.debug(f"📊 Found {len(messages)} messages with embeddings to search")
            
            # Calculate similarities
            results = []
            
            for msg_doc in messages:
                if 'embedding' not in msg_doc or not msg_doc['embedding']:
                    continue
                
                try:
                    msg_embedding = np.array(msg_doc['embedding'])
                    similarity = self.embedding_engine.cosine_similarity(
                        query_embedding,
                        msg_embedding
                    )
                    
                    if similarity >= min_similarity:
                        # Convert document to Message object
                        message = Message(
                            id=msg_doc['_id'],
                            session_id=msg_doc['session_id'],
                            user_id=msg_doc['user_id'],
                            role=MessageRole(msg_doc['role']),
                            content=msg_doc['content'],
                            timestamp=msg_doc['timestamp'],
                            emotion_state=EmotionState(**msg_doc['emotion_state']) if msg_doc.get('emotion_state') else None,
                            provider_used=msg_doc.get('provider_used'),
                            response_time_ms=msg_doc.get('response_time_ms'),
                            tokens_used=msg_doc.get('tokens_used'),
                            cost=msg_doc.get('cost')
                        )
                        results.append((message, similarity))
                except Exception as e:
                    logger.warning(f"⚠️  Failed to process message for similarity: {e}")
                    continue
            
            # Sort by similarity (descending) and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            results = results[:top_k]
            
            logger.debug(
                f"✅ MongoDB search complete: found {len(results)} relevant messages "
                f"(similarity >= {min_similarity})"
            )
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []


class ContextManager:
    """
    Main context management system
    
    Features:
    - Maintain conversation history
    - Smart context window management
    - Memory systems (short-term, long-term)
    - Context compression
    - Semantic retrieval
    - Token budget management
    """
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        max_context_tokens: int = 8000,
        short_term_memory_size: int = 20,
        embedding_model: str = "all-MiniLM-L6-v2",
        vector_store: Optional["QdrantVectorStore"] = None
    ):
        """
        Initialize context manager
        
        Following MASTERX_PROJECT_AUDIT.md Section 1.1:
        - Uses Qdrant vector store for semantic search (if available)
        - Falls back to MongoDB linear search if Qdrant unavailable
        - Dual storage: MongoDB (messages) + Qdrant (embeddings)
        
        Args:
            db: MongoDB database instance
            max_context_tokens: Maximum tokens for context window
            short_term_memory_size: Number of recent messages to keep in memory
            embedding_model: Model for generating embeddings
            vector_store: Qdrant vector store instance (None for MongoDB-only)
        """
        self.db = db
        self.messages_collection = db.messages
        self.sessions_collection = db.sessions
        
        # Vector store for semantic search
        self.vector_store = vector_store
        
        # Initialize components
        self.embedding_engine = EmbeddingEngine(model_name=embedding_model)
        self.token_manager = TokenBudgetManager(max_context_tokens=max_context_tokens)
        self.memory_retriever = MemoryRetriever(self.embedding_engine, db)
        
        # Configuration
        self.short_term_memory_size = short_term_memory_size
        
        # Log initialization
        vector_mode = "Qdrant (HNSW)" if vector_store else "MongoDB (linear)"
        logger.info(
            f"✅ ContextManager initialized "
            f"(max_tokens={max_context_tokens}, "
            f"short_term={short_term_memory_size}, "
            f"semantic_search={vector_mode})"
        )
    
    async def add_message(
        self,
        session_id: str,
        message: Message,
        generate_embedding: bool = True
    ) -> str:
        """
        Add message to context and database
        
        CRITICAL FIXES (Perplexity Enhancement Plan):
        - Ensure embedding is generated and stored properly
        - Verify MongoDB insert is awaited
        - Add comprehensive logging for debugging
        - Type consistency (session_id as string)
        - Don't fail entire request if embedding fails
        
        Args:
            session_id: Session ID
            message: Message to add
            generate_embedding: Whether to generate embedding for semantic search
        
        Returns:
            Message ID
        """
        try:
            # CRITICAL: Ensure session_id is string for consistency
            session_id_str = str(session_id)
            
            # DEBUG: Log what we're storing
            logger.info(f"📝 Storing message for session {session_id_str} (role: {message.role.value})")
            
            # Generate embedding if requested
            embedding = None
            if generate_embedding:
                try:
                    embedding_vector = await self.embedding_engine.embed_text(
                        message.content
                    )
                    # CRITICAL: Convert numpy array to list for MongoDB
                    embedding = embedding_vector.tolist()
                    
                    # DEBUG: Verify embedding generated
                    logger.info(f"✅ Embedding generated: dimension={len(embedding)}")
                except Exception as e:
                    logger.error(f"❌ Failed to generate embedding: {e}")
                    # Don't fail the whole request, but log prominently
                    embedding = None
            
            # Prepare message document
            message_doc = {
                '_id': message.id,
                'session_id': session_id_str,  # CRITICAL: Use string type
                'user_id': message.user_id,
                'role': message.role.value,
                'content': message.content,
                'timestamp': message.timestamp,
                'embedding': embedding,  # CRITICAL: Store embedding
                'emotion_state': message.emotion_state.model_dump() if message.emotion_state else None,
                'provider_used': message.provider_used,
                'response_time_ms': message.response_time_ms,
                'tokens_used': message.tokens_used,
                'cost': message.cost,
                'quality_rating': message.quality_rating
            }
            
            # CRITICAL: Insert into MongoDB (must await)
            result = await self.messages_collection.insert_one(message_doc)
            
            # DEBUG: Verify insertion
            logger.info(f"✅ Message stored in MongoDB: id={result.inserted_id}, has_embedding={embedding is not None}")
            
            # DUAL STORAGE: Insert into Qdrant vector store if available
            # Following MASTERX_PROJECT_AUDIT.md Section 1.1
            if self.vector_store and embedding is not None:
                try:
                    success = await self.vector_store.insert(
                        message_id=message.id,
                        embedding=embedding_vector,  # Use numpy array, not list
                        session_id=session_id_str,
                        user_id=message.user_id,
                        role=message.role,
                        timestamp=message.timestamp,
                        metadata={
                            'provider_used': message.provider_used,
                            'tokens_used': message.tokens_used,
                            'cost': message.cost
                        }
                    )
                    
                    if success:
                        logger.info(f"✅ Message also stored in Qdrant vector store")
                    else:
                        logger.warning(f"⚠️  Qdrant insert failed, using MongoDB only")
                        
                except Exception as e:
                    logger.warning(f"⚠️  Qdrant insert error (graceful degradation): {e}")
                    # Continue with MongoDB-only storage
            
            return message.id
        
        except Exception as e:
            logger.error(f"❌ Failed to store message: {e}")
            # Don't fail the whole request if context storage fails
            # This allows the chat to continue even if context system has issues
            logger.warning("⚠️  Context storage failed, but continuing request")
            return message.id  # Return ID anyway to not break flow
    
    async def get_context(
        self,
        session_id: str,
        include_semantic: bool = True,
        semantic_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conversation context for session
        
        CRITICAL FIXES (Perplexity Enhancement Plan):
        - Verify messages exist before semantic search
        - Handle empty results gracefully
        - Add extensive logging for debugging
        - Type consistency (session_id as string)
        - Don't fail on errors, return empty context
        
        Args:
            session_id: Session ID
            include_semantic: Include semantically relevant past messages
            semantic_query: Query for semantic search (if None, uses recent messages)
        
        Returns:
            Context dictionary with:
            - recent_messages: Recent conversation history
            - relevant_messages: Semantically relevant past messages
            - total_tokens: Estimated token count
            - compressed: Whether context was compressed
        """
        try:
            import time
            start_time = time.time()
            
            # CRITICAL: Convert session_id to string for consistency
            session_id_str = str(session_id)
            
            logger.info(f"🔍 Retrieving context for session: {session_id_str}")
            
            # STEP 1: Check if messages exist (DEBUG)
            message_count = await self.messages_collection.count_documents({
                'session_id': session_id_str
            })
            logger.info(f"📊 Found {message_count} total messages in session")
            
            if message_count == 0:
                logger.warning(f"⚠️  No messages found for session {session_id_str}")
                return {
                    'recent_messages': [],
                    'relevant_messages': [],
                    'total_tokens': 0,
                    'compressed': False,
                    'compression_ratio': 1.0
                }
            
            # STEP 2: Check if embeddings exist (DEBUG)
            embedded_count = await self.messages_collection.count_documents({
                'session_id': session_id_str,
                'embedding': {'$exists': True, '$ne': None}
            })
            logger.info(f"📊 Found {embedded_count} messages with embeddings")
            
            if embedded_count == 0:
                logger.warning(f"⚠️  No embeddings found! Messages stored without embeddings!")
            
            # STEP 3: Get recent messages (short-term memory)
            cursor = self.messages_collection.find({
                'session_id': session_id_str
            }).sort('timestamp', -1).limit(self.short_term_memory_size)
            
            recent_docs = await cursor.to_list(length=self.short_term_memory_size)
            logger.info(f"📥 Retrieved {len(recent_docs)} recent messages from DB")
            
            # Convert to Message objects
            recent_messages = []
            for doc in reversed(recent_docs):  # Reverse to chronological order
                try:
                    message = Message(
                        id=doc['_id'],
                        session_id=doc['session_id'],
                        user_id=doc['user_id'],
                        role=MessageRole(doc['role']),
                        content=doc['content'],
                        timestamp=doc['timestamp'],
                        emotion_state=EmotionState(**doc['emotion_state']) if doc.get('emotion_state') else None,
                        provider_used=doc.get('provider_used'),
                        response_time_ms=doc.get('response_time_ms'),
                        tokens_used=doc.get('tokens_used'),
                        cost=doc.get('cost')
                    )
                    recent_messages.append(message)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to parse message: {e}")
                    continue
            
            logger.info(f"✅ Parsed {len(recent_messages)} recent messages")
            
            # Fit to token budget
            fitted_messages = self.token_manager.fit_messages_to_budget(
                recent_messages,
                self.token_manager.context_budget
            )
            
            logger.info(f"📏 Fitted {len(fitted_messages)} messages to token budget")
            
            # STEP 4: Get semantically relevant messages if requested
            relevant_messages = []
            if include_semantic and semantic_query and embedded_count > 0:
                try:
                    logger.info(f"🔎 Performing semantic search...")
                    relevant_with_scores = await self.memory_retriever.find_relevant(
                        query=semantic_query,
                        session_id=session_id_str,
                        top_k=3,
                        min_similarity=0.7
                    )
                    relevant_messages = [msg for msg, score in relevant_with_scores]
                    logger.info(f"✅ Found {len(relevant_messages)} relevant messages")
                except Exception as e:
                    logger.error(f"❌ Semantic search failed: {e}")
                    relevant_messages = []
            
            # Calculate total tokens
            total_tokens = sum(
                self.token_manager.estimate_tokens(msg.content)
                for msg in fitted_messages
            )
            
            # STEP 5: Assemble context
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            context = {
                'recent_messages': fitted_messages,
                'relevant_messages': relevant_messages,
                'total_tokens': total_tokens,
                'compressed': len(fitted_messages) < len(recent_messages),
                'compression_ratio': len(fitted_messages) / len(recent_messages) if recent_messages else 1.0
            }
            
            logger.info(
                f"✅ Context retrieved successfully: "
                f"recent={len(fitted_messages)}, "
                f"relevant={len(relevant_messages)}, "
                f"tokens={total_tokens}, "
                f"time={retrieval_time_ms:.1f}ms"
            )
            
            return context
        
        except Exception as e:
            logger.error(f"❌ Context retrieval failed: {e}")
            # Return empty context instead of failing
            logger.warning("⚠️  Returning empty context due to error")
            return {
                'recent_messages': [],
                'relevant_messages': [],
                'total_tokens': 0,
                'compressed': False,
                'compression_ratio': 1.0
            }
    
    async def compress_context(
        self,
        session_id: str,
        compression_ratio: float = 0.5
    ) -> int:
        """
        Compress old context by removing less important messages
        
        Strategy:
        - Keep recent messages (high importance)
        - Keep messages with strong emotions (high importance)
        - Remove neutral, older messages (low importance)
        
        Args:
            session_id: Session ID
            compression_ratio: Target ratio of messages to keep (0.5 = keep 50%)
        
        Returns:
            Number of messages removed
        """
        try:
            # Get all messages
            cursor = self.messages_collection.find({
                'session_id': session_id
            }).sort('timestamp', 1)  # Oldest first
            
            all_messages = await cursor.to_list(length=1000)
            
            if len(all_messages) <= self.short_term_memory_size:
                # Not enough messages to compress
                return 0
            
            # Calculate target count
            target_count = int(len(all_messages) * compression_ratio)
            target_count = max(target_count, self.short_term_memory_size)
            
            # Score messages by importance
            scored_messages = []
            for msg in all_messages:
                # Base score: recency (0.0 to 1.0)
                recency_score = all_messages.index(msg) / len(all_messages)
                
                # Emotion score: high arousal = important
                emotion_score = 0.0
                if msg.get('emotion_state'):
                    emotion = msg['emotion_state']
                    emotion_score = emotion.get('arousal', 0.0)
                
                # Combined importance score
                importance = (recency_score * 0.6) + (emotion_score * 0.4)
                
                scored_messages.append((msg, importance))
            
            # Sort by importance (descending)
            scored_messages.sort(key=lambda x: x[1], reverse=True)
            
            # Keep top N messages
            messages_to_keep = set(msg['_id'] for msg, _ in scored_messages[:target_count])
            
            # Delete less important messages
            result = await self.messages_collection.delete_many({
                'session_id': session_id,
                '_id': {'$nin': list(messages_to_keep)}
            })
            
            removed_count = result.deleted_count
            
            logger.info(
                f"Context compressed for session {session_id}: "
                f"removed {removed_count} messages "
                f"({len(all_messages)} -> {target_count})"
            )
            
            return removed_count
        
        except Exception as e:
            logger.error(f"Error compressing context: {e}")
            return 0
    
    async def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for session context
        
        Args:
            session_id: Session ID
        
        Returns:
            Summary dictionary with statistics
        """
        try:
            # Count messages
            total_messages = await self.messages_collection.count_documents({
                'session_id': session_id
            })
            
            # Get session info
            session = await self.sessions_collection.find_one({'_id': session_id})
            
            summary = {
                'session_id': session_id,
                'total_messages': total_messages,
                'short_term_capacity': self.short_term_memory_size,
                'context_budget_tokens': self.token_manager.context_budget,
                'session_started': session['started_at'] if session else None,
                'current_topic': session.get('current_topic') if session else None
            }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {}
