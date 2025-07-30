"""Factory for creating vector store instances."""

from typing import Any, Dict, Optional

from .adapters.qdrant_adapter import QdrantAdapter
from .adapters.weaviate_adapter import WeaviateAdapter
from .adapters.chroma_adapter import ChromaAdapter
from .adapters.pgvector_adapter import PgvectorAdapter
from .adapters.milvus_adapter import MilvusAdapter
from .adapters.pinecone_adapter import PineconeAdapter
from .core.base import VectorStoreInterface


class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    _adapters = {
        "qdrant": QdrantAdapter,
        "weaviate": WeaviateAdapter,
        "chroma": ChromaAdapter,
        "pgvector": PgvectorAdapter,
        "milvus": MilvusAdapter,
        "pinecone": PineconeAdapter,
    }
    
    @classmethod
    def create(
        cls,
        backend: str,
        collection: str,
        **kwargs
    ) -> VectorStoreInterface:
        """Create a vector store instance.
        
        Args:
            backend: Backend type (qdrant, weaviate, chroma, pgvector, milvus, pinecone)
            collection: Collection/table/index name
            **kwargs: Backend-specific parameters
            
        Returns:
            Vector store instance
            
        Raises:
            ValueError: If backend is not supported
        """
        if backend not in cls._adapters:
            raise ValueError(
                f"Unsupported backend: {backend}. "
                f"Supported backends: {list(cls._adapters.keys())}"
            )
            
        adapter_class = cls._adapters[backend]
        return adapter_class(collection=collection, **kwargs)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> VectorStoreInterface:
        """Create vector store from configuration.
        
        Args:
            config: Configuration dictionary with 'backend' and 'params'
            
        Returns:
            Vector store instance
        """
        backend = config.get("backend")
        if not backend:
            raise ValueError("Configuration must include 'backend' key")
            
        params = config.get("params", {})
        return cls.create(backend, **params)
    
    @classmethod
    def list_backends(cls) -> list[str]:
        """List available backends."""
        return list(cls._adapters.keys())
    
    @classmethod
    def get_backend_info(cls, backend: str) -> Dict[str, Any]:
        """Get information about a backend.
        
        Args:
            backend: Backend name
            
        Returns:
            Backend information
        """
        if backend not in cls._adapters:
            raise ValueError(f"Unsupported backend: {backend}")
            
        adapter_class = cls._adapters[backend]
        
        # Get basic info from adapter
        return {
            "name": backend,
            "class": adapter_class.__name__,
            "module": adapter_class.__module__,
        }
