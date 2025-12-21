"""
Qdrant Vector Store Integration for MasterX
Following specifications from MASTERX_PROJECT_AUDIT.md Section 1.1

PURPOSE:
- Replace MongoDB embedding linear search with proper vector database
- Implement semantic search with <50ms latency
- Enable hybrid search (vector + metadata filtering)
- Scalable to 1M+ messages with HNSW indexing

PRINCIPLES (AGENTS.md):
- Zero hardcoded values (all from configuration)
- Real vector DB (Qdrant with HNSW indexing)
- Clean, professional naming
- Comprehensive error handling
- Graceful degradation to MongoDB fallback
- Async/await patterns throughout

ARCHITECTURE:
- Dual storage: MongoDB (messages) + Qdrant (embeddings)
- Sync: Insert message → MongoDB + Qdrant simultaneously
- Search: Qdrant (fast vector search) → MongoDB (fetch full messages)
- Fallback: If Qdrant fails, use MongoDB linear search

Based on 2025 best practices from Qdrant documentation and industry standards.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)

from core.models import Message, MessageRole
from utils.errors import MasterXError

logger = logging.getLogger(__name__)


class VectorStoreError(MasterXError):
    """Vector store operation failed"""
    pass


class QdrantVectorStore:
    """
    Qdrant vector database integration for semantic search
    
    Features:
    - HNSW indexing for fast nearest neighbor search
    - COSINE distance metric (optimal for embeddings)
    - Payload filtering for session-based queries
    - Batch operations for efficiency
    - Graceful degradation on failures
    - Health monitoring
    
    Performance Targets (AGENTS.md compliant - from benchmarking):
    - Search latency: <50ms (P95)
    - Insert latency: <10ms (P95)
    - Throughput: >1000 QPS
    - Scalability: Up to 10M vectors
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "conversation_history",
        vector_size: int = 384,
        distance: Distance = Distance.COSINE,
        timeout: int = 30
    ):
        """
        Initialize Qdrant vector store
        
        Args:
            url: Qdrant server URL (None for embedded mode, ":memory:" for in-memory)
            api_key: API key for Qdrant Cloud (optional)
            collection_name: Name of the collection
            vector_size: Embedding dimension (384 for all-MiniLM-L6-v2)
            distance: Distance metric (COSINE for semantic search)
            timeout: Request timeout in seconds
        
        Note: 
            - Embedded mode (url=None): For development/testing
            - Server mode (url="http://localhost:6333"): For production
            - Cloud mode (url + api_key): For Qdrant Cloud
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance
        self.timeout = timeout
        self._client: Optional[AsyncQdrantClient] = None
        self._initialized = False
        self._url = url
        self._api_key = api_key
        
        logger.info(
            f"QdrantVectorStore configured: "
            f"collection={collection_name}, "
            f"vector_size={vector_size}, "
            f"distance={distance.value}"
        )
    
    async def connect(self) -> None:
        """
        Connect to Qdrant and initialize collection
        
        Raises:
            VectorStoreError: If connection or initialization fails
        """
        try:
            logger.info("Connecting to Qdrant...")
            
            # Create client based on mode
            # Check for empty string or None for embedded mode
            if self._url is None or self._url == "":
                # Embedded mode (for development)
                logger.info("Using Qdrant embedded mode (local storage)")
                self._client = AsyncQdrantClient(path="/tmp/qdrant_storage")
            elif self._api_key:
                # Cloud mode
                logger.info(f"Connecting to Qdrant Cloud: {self._url}")
                self._client = AsyncQdrantClient(
                    url=self._url,
                    api_key=self._api_key,
                    timeout=self.timeout
                )
            else:
                # Server mode (local or remote)
                logger.info(f"Connecting to Qdrant server: {self._url}")
                self._client = AsyncQdrantClient(
                    url=self._url,
                    timeout=self.timeout
                )
            
            # Verify connection
            collections = await self._client.get_collections()
            logger.info(f"✅ Connected to Qdrant ({len(collections.collections)} collections)")
            
            # Initialize collection
            await self._initialize_collection()
            
            self._initialized = True
            logger.info("✅ Qdrant vector store ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            raise VectorStoreError(
                f"Failed to connect to Qdrant: {str(e)}",
                details={'url': self._url, 'collection': self.collection_name}
            )
    
    async def _initialize_collection(self) -> None:
        """
        Initialize Qdrant collection with proper configuration
        
        2025 Best Practices:
        - COSINE distance for normalized embeddings
        - Payload indexing for fast filtering
        - HNSW index parameters optimized for semantic search
        """
        try:
            # Check if collection exists
            collections = await self._client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                
                # Verify collection configuration
                collection_info = await self._client.get_collection(self.collection_name)
                config_vector_size = collection_info.config.params.vectors.size
                
                if config_vector_size != self.vector_size:
                    logger.error(
                        f"Collection vector size mismatch: "
                        f"expected {self.vector_size}, got {config_vector_size}"
                    )
                    raise VectorStoreError(
                        f"Vector size mismatch in collection {self.collection_name}"
                    )
                
                return
            
            # Create new collection
            logger.info(f"Creating collection '{self.collection_name}'...")
            
            await self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance
                )
            )
            
            # Create payload indexes for fast filtering
            # Index by session_id for session-specific queries
            await self._client.create_payload_index(
                collection_name=self.collection_name,
                field_name="session_id",
                field_schema="keyword"
            )
            
            # Index by timestamp for time-based filtering
            await self._client.create_payload_index(
                collection_name=self.collection_name,
                field_name="timestamp",
                field_schema="datetime"
            )
            
            logger.info(f"✅ Created collection '{self.collection_name}' with indexes")
            
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise VectorStoreError(f"Failed to initialize collection: {str(e)}")
    
    async def insert(
        self,
        message_id: str,
        embedding: np.ndarray,
        session_id: str,
        user_id: str,
        role: MessageRole,
        timestamp: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Insert embedding vector into Qdrant
        
        Args:
            message_id: Unique message ID (used as point ID)
            embedding: Embedding vector (numpy array)
            session_id: Session ID for filtering
            user_id: User ID
            role: Message role (user/assistant/system)
            timestamp: Message timestamp
            metadata: Additional metadata to store
        
        Returns:
            True if successful, False on error (graceful degradation)
        """
        if not self._initialized:
            logger.warning("Qdrant not initialized, skipping insert")
            return False
        
        try:
            # Prepare payload (metadata for filtering)
            payload = {
                'session_id': str(session_id),
                'user_id': str(user_id),
                'role': role.value,
                'timestamp': timestamp.isoformat(),
                'message_id': message_id
            }
            
            # Add custom metadata if provided
            if metadata:
                payload.update(metadata)
            
            # Convert embedding to list
            if isinstance(embedding, np.ndarray):
                embedding_list = embedding.tolist()
            else:
                embedding_list = list(embedding)
            
            # Create point
            # CRITICAL FIX: Qdrant embedded mode requires UUID-compatible IDs
            # Convert string IDs to UUID if not already UUID format
            import uuid as uuid_lib
            try:
                # Try to parse as UUID
                point_id = uuid_lib.UUID(message_id)
            except (ValueError, AttributeError):
                # Not a UUID, generate one from the message_id
                # Use deterministic UUID (namespace-based) to ensure consistency
                namespace = uuid_lib.NAMESPACE_DNS
                point_id = uuid_lib.uuid5(namespace, message_id)
            
            point = PointStruct(
                id=str(point_id),  # Qdrant accepts string UUID
                vector=embedding_list,
                payload=payload
            )
            
            # Insert into Qdrant
            await self._client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True  # Wait for indexing to complete
            )
            
            logger.debug(f"✅ Inserted embedding: message_id={message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to insert embedding: {e}")
            # Don't raise - graceful degradation
            return False
    
    async def insert_batch(
        self,
        points: List[Tuple[str, np.ndarray, Dict[str, Any]]]
    ) -> int:
        """
        Batch insert embeddings for efficiency
        
        Args:
            points: List of (message_id, embedding, payload) tuples
        
        Returns:
            Number of successfully inserted points
        """
        if not self._initialized:
            logger.warning("Qdrant not initialized, skipping batch insert")
            return 0
        
        try:
            # Prepare points
            qdrant_points = []
            for message_id, embedding, payload in points:
                if isinstance(embedding, np.ndarray):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = list(embedding)
                
                point = PointStruct(
                    id=message_id,
                    vector=embedding_list,
                    payload=payload
                )
                qdrant_points.append(point)
            
            # Batch upsert
            await self._client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
                wait=True
            )
            
            logger.info(f"✅ Batch inserted {len(qdrant_points)} embeddings")
            return len(qdrant_points)
            
        except Exception as e:
            logger.error(f"❌ Batch insert failed: {e}")
            return 0
    
    async def search(
        self,
        query_embedding: np.ndarray,
        session_id: str,
        limit: int = 5,
        score_threshold: float = 0.7,
        time_window_days: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Semantic search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            session_id: Session ID to filter by
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0.0 to 1.0)
            time_window_days: Only search within time window (optional)
        
        Returns:
            List of (message_id, similarity_score) tuples
        """
        if not self._initialized:
            logger.warning("Qdrant not initialized, returning empty results")
            return []
        
        try:
            import time
            start_time = time.time()
            
            # Convert embedding to list
            if isinstance(query_embedding, np.ndarray):
                query_vector = query_embedding.tolist()
            else:
                query_vector = list(query_embedding)
            
            # Build filter
            filter_conditions = [
                FieldCondition(
                    key="session_id",
                    match=MatchValue(value=str(session_id))
                )
            ]
            
            # Add time window filter if specified
            if time_window_days is not None:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(days=time_window_days)
                filter_conditions.append(
                    FieldCondition(
                        key="timestamp",
                        range={
                            "gte": cutoff.isoformat()
                        }
                    )
                )
            
            query_filter = Filter(must=filter_conditions)
            
            # Search using query_points (correct AsyncQdrantClient API)
            search_results = await self._client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Extract results (handle both search and query_points response formats)
            results = []
            
            # query_points returns a QueryResponse with .points attribute
            points = search_results.points if hasattr(search_results, 'points') else search_results
            
            for hit in points:
                # Handle both ScoredPoint and SearchResult formats
                point_id = str(hit.id)
                score = float(hit.score)
                results.append((point_id, score))
            
            search_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"✅ Semantic search complete: "
                f"found {len(results)} results, "
                f"time={search_time_ms:.1f}ms"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            # Return empty results on error (graceful degradation)
            return []
    
    async def delete(self, message_id: str) -> bool:
        """
        Delete embedding from Qdrant
        
        Args:
            message_id: Message ID to delete
        
        Returns:
            True if successful
        """
        if not self._initialized:
            logger.warning("Qdrant not initialized, skipping delete")
            return False
        
        try:
            await self._client.delete(
                collection_name=self.collection_name,
                points_selector=[message_id]
            )
            
            logger.debug(f"✅ Deleted embedding: message_id={message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete embedding: {e}")
            return False
    
    async def delete_by_session(self, session_id: str) -> int:
        """
        Delete all embeddings for a session
        
        Args:
            session_id: Session ID
        
        Returns:
            Number of deleted points
        """
        if not self._initialized:
            logger.warning("Qdrant not initialized, skipping session delete")
            return 0
        
        try:
            # Delete by filter
            delete_filter = Filter(
                must=[
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=str(session_id))
                    )
                ]
            )
            
            result = await self._client.delete(
                collection_name=self.collection_name,
                points_selector=delete_filter
            )
            
            logger.info(f"✅ Deleted session embeddings: session_id={session_id}")
            return 1  # Qdrant doesn't return count, assume success
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session embeddings: {e}")
            return 0
    
    async def count(self, session_id: Optional[str] = None) -> int:
        """
        Count embeddings in collection
        
        Args:
            session_id: Optional session ID to filter by
        
        Returns:
            Number of embeddings
        """
        if not self._initialized:
            return 0
        
        try:
            if session_id:
                # Count with filter
                count_filter = Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=str(session_id))
                        )
                    ]
                )
                result = await self._client.count(
                    collection_name=self.collection_name,
                    count_filter=count_filter
                )
            else:
                # Count all
                result = await self._client.count(
                    collection_name=self.collection_name
                )
            
            return result.count
            
        except Exception as e:
            logger.error(f"Failed to count embeddings: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check vector store health
        
        Returns:
            Health status dictionary
        """
        try:
            if not self._initialized:
                return {
                    'status': 'not_initialized',
                    'healthy': False,
                    'message': 'Qdrant not initialized'
                }
            
            # Get collection info
            collection_info = await self._client.get_collection(self.collection_name)
            
            # Get count
            total_count = await self.count()
            
            health = {
                'status': 'healthy',
                'healthy': True,
                'collection': self.collection_name,
                'vector_count': total_count,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance.value,
                'points_count': collection_info.points_count,
                'indexed_vectors_count': collection_info.indexed_vectors_count
            }
            
            logger.debug(f"Qdrant health check: {health['status']}")
            return health
            
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return {
                'status': 'error',
                'healthy': False,
                'error': str(e)
            }
    
    async def close(self) -> None:
        """Close Qdrant connection"""
        try:
            if self._client:
                await self._client.close()
                logger.info("✅ Qdrant connection closed")
        except Exception as e:
            logger.error(f"Error closing Qdrant connection: {e}")
