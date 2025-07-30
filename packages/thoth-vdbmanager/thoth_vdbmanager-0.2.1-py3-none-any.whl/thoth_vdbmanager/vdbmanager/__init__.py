"""Thoth Vector Database Manager - Haystack-based implementation."""

from .core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    HintDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)
from .factory import VectorStoreFactory
from .compat.thoth_vector_store import ThothVectorStore, QdrantHaystackStore

# Import adapters for direct usage
from .adapters.qdrant_adapter import QdrantAdapter
from .adapters.weaviate_adapter import WeaviateAdapter
from .adapters.chroma_adapter import ChromaAdapter
from .adapters.pgvector_adapter import PgvectorAdapter
from .adapters.milvus_adapter import MilvusAdapter
from .adapters.pinecone_adapter import PineconeAdapter

__version__ = "2.0.0"
__all__ = [
    # Core classes
    "BaseThothDocument",
    "ColumnNameDocument",
    "HintDocument",
    "SqlDocument",
    "ThothType",
    "VectorStoreInterface",
    
    # Factory
    "VectorStoreFactory",
    
    # Adapters
    "QdrantAdapter",
    "WeaviateAdapter",
    "ChromaAdapter",
    "PgvectorAdapter",
    "MilvusAdapter",
    "PineconeAdapter",
    
    # Compatibility
    "ThothVectorStore",
    "QdrantHaystackStore",
]

# Backward compatibility aliases
ThothHaystackVectorStore = ThothVectorStore
