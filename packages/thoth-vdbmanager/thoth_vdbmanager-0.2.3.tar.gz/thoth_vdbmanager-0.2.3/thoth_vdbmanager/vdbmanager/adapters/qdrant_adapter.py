"""Qdrant adapter for Thoth Vector Database."""

import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

from .haystack_adapter import HaystackVectorStoreAdapter
from ..core.base import VectorStoreInterface

logger = logging.getLogger(__name__)


class QdrantAdapter(HaystackVectorStoreAdapter):
    """Qdrant implementation using Haystack integration."""
    
    _instances: Dict[str, "QdrantAdapter"] = {}
    
    def __new__(
        cls,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """Singleton pattern for Qdrant adapter."""
        instance_key = f"{collection}:{host}:{port}:{api_key}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]
            
        instance = super().__new__(cls)
        cls._instances[instance_key] = instance
        return instance
    
    def __init__(
        self,
        collection: str,
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
        **kwargs
    ):
        """Initialize Qdrant adapter.
        
        Args:
            collection: Collection name
            host: Qdrant host
            port: Qdrant port
            api_key: API key for authentication
            url: Full URL (overrides host/port)
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            **kwargs: Additional Qdrant parameters
        """
        # Prevent reinitialization
        if hasattr(self, '_initialized'):
            return
            
        # Parse URL if provided
        if url:
            parsed = urlparse(url)
            host = parsed.hostname or host
            port = parsed.port or port
            
        # Create Qdrant document store
        document_store = QdrantDocumentStore(
            index=collection,
            host=host,
            port=port,
            api_key=api_key,
            embedding_dim=embedding_dim,
            hnsw_config={
                "m": 16,
                "ef_construct": 100,
                **kwargs.get("hnsw_config", {})
            },
            **{k: v for k, v in kwargs.items() if k != "hnsw_config"}
        )
        
        super().__init__(
            document_store=document_store,
            collection_name=collection,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )
        
        self._initialized = True
        logger.info(f"Qdrant adapter initialized for collection: {collection}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get detailed Qdrant collection information."""
        info = super().get_collection_info()
        
        try:
            # Get additional Qdrant-specific info
            client = self.document_store._client
            collection_info = client.get_collection(self.collection_name)
            
            info.update({
                "backend": "qdrant",
                "points_count": collection_info.points_count,
                "vectors_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": str(collection_info.config.params.vectors.distance),
                },
                "hnsw_config": {
                    "m": collection_info.config.params.hnsw_config.m,
                    "ef_construct": collection_info.config.params.hnsw_config.ef_construct,
                }
            })
        except Exception as e:
            logger.error(f"Error getting Qdrant collection info: {e}")
            info["backend"] = "qdrant"
            
        return info
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "QdrantAdapter":
        """Create Qdrant adapter from configuration."""
        return cls(**config)
