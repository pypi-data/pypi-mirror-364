"""Base Haystack adapter for Thoth Vector Database."""

import logging
from typing import Any, Dict, List, Optional, Type, cast
from uuid import uuid4

from haystack import Document as HaystackDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.document_stores.types import DocumentStore, DuplicatePolicy
from haystack import Pipeline

from ..core.base import (
    BaseThothDocument,
    ColumnNameDocument,
    HintDocument,
    SqlDocument,
    ThothType,
    VectorStoreInterface,
)

logger = logging.getLogger(__name__)


class HaystackVectorStoreAdapter(VectorStoreInterface):
    """Base adapter that uses Haystack DocumentStore as backend."""
    
    def __init__(
        self,
        document_store: DocumentStore,
        collection_name: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedding_dim: int = 384,
    ):
        """Initialize the Haystack adapter.
        
        Args:
            document_store: Haystack DocumentStore instance
            collection_name: Name of the collection/index
            embedding_model: Name of the sentence transformer model
            embedding_dim: Dimension of the embeddings
        """
        self.document_store = document_store
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        
        # Lazy initialization of embedders
        self._document_embedder: Optional[SentenceTransformersDocumentEmbedder] = None
        self._text_embedder: Optional[SentenceTransformersTextEmbedder] = None
        self._search_pipeline: Optional[Pipeline] = None
        
        logger.info(
            f"Initialized Haystack adapter for {collection_name} "
            f"with model {embedding_model}"
        )

    def _get_document_embedder(self) -> SentenceTransformersDocumentEmbedder:
        """Get or create document embedder."""
        if self._document_embedder is None:
            self._document_embedder = SentenceTransformersDocumentEmbedder(
                model=self.embedding_model
            )
            self._document_embedder.warm_up()
        return self._document_embedder

    def _get_text_embedder(self) -> SentenceTransformersTextEmbedder:
        """Get or create text embedder."""
        if self._text_embedder is None:
            self._text_embedder = SentenceTransformersTextEmbedder(
                model=self.embedding_model
            )
            self._text_embedder.warm_up()
        return self._text_embedder

    def _get_search_pipeline(self) -> Pipeline:
        """Get or create search pipeline."""
        if self._search_pipeline is None:
            try:
                # Try new retriever name first, fallback to old name
                try:
                    from haystack.components.retrievers import InMemoryEmbeddingRetriever as MemoryRetriever
                except ImportError:
                    from haystack.components.retrievers import MemoryRetriever

                self._search_pipeline = Pipeline()
                self._search_pipeline.add_component("embedder", self._get_text_embedder())
                self._search_pipeline.add_component(
                    "retriever",
                    MemoryRetriever(document_store=self.document_store, top_k=10)
                )
                self._search_pipeline.connect("embedder.embedding", "retriever.query_embedding")
            except ImportError as e:
                logger.error(f"Failed to import retriever: {e}")
                # Create a minimal pipeline without retriever for compatibility
                self._search_pipeline = Pipeline()
                self._search_pipeline.add_component("embedder", self._get_text_embedder())
        return self._search_pipeline

    def _convert_to_haystack_document(self, doc: BaseThothDocument) -> HaystackDocument:
        """Convert Thoth document to Haystack document."""
        if not doc.text:
            doc.text = self._enrich_content(doc)
            
        metadata = {
            "thoth_type": doc.thoth_type.value,
            "thoth_id": doc.id,
        }
        
        if isinstance(doc, ColumnNameDocument):
            metadata.update({
                "table_name": doc.table_name,
                "column_name": doc.column_name,
                "original_column_name": doc.original_column_name,
                "column_description": doc.column_description,
                "value_description": doc.value_description,
            })
        elif isinstance(doc, SqlDocument):
            metadata.update({
                "question": doc.question,
                "sql": doc.sql,
                "hint": doc.hint,
            })
        elif isinstance(doc, HintDocument):
            metadata.update({
                "hint": doc.hint,
            })
            
        return HaystackDocument(
            id=doc.id,
            content=doc.text,
            meta=metadata,
        )

    def _convert_from_haystack_document(self, haystack_doc: HaystackDocument) -> Optional[BaseThothDocument]:
        """Convert Haystack document to Thoth document."""
        if not haystack_doc.meta or "thoth_type" not in haystack_doc.meta:
            return None
            
        thoth_type_str = haystack_doc.meta["thoth_type"]
        try:
            thoth_type = ThothType(thoth_type_str)
        except ValueError:
            logger.warning(f"Invalid ThothType: {thoth_type_str}")
            return None
            
        doc_id = str(haystack_doc.meta.get("thoth_id", haystack_doc.id))
        doc_text = haystack_doc.content
        
        try:
            if thoth_type == ThothType.COLUMN_NAME:
                return ColumnNameDocument(
                    id=doc_id,
                    text=doc_text,
                    table_name=haystack_doc.meta.get("table_name", ""),
                    column_name=haystack_doc.meta.get("column_name", ""),
                    original_column_name=haystack_doc.meta.get("original_column_name", ""),
                    column_description=haystack_doc.meta.get("column_description", ""),
                    value_description=haystack_doc.meta.get("value_description", ""),
                )
            elif thoth_type == ThothType.SQL:
                return SqlDocument(
                    id=doc_id,
                    text=doc_text,
                    question=haystack_doc.meta.get("question", ""),
                    sql=haystack_doc.meta.get("sql", ""),
                    hint=haystack_doc.meta.get("hint", ""),
                )
            elif thoth_type == ThothType.HINT:
                return HintDocument(
                    id=doc_id,
                    text=doc_text,
                    hint=haystack_doc.meta.get("hint", haystack_doc.content),
                )
        except Exception as e:
            logger.error(f"Error converting document: {e}")
            return None
            
    def _enrich_content(self, doc: BaseThothDocument) -> str:
        """Enrich document content for embedding."""
        if isinstance(doc, ColumnNameDocument):
            return (
                f"Table: {doc.table_name}, Column: {doc.column_name} "
                f"(Original: {doc.original_column_name}). "
                f"Description: {doc.column_description}. "
                f"Value Info: {doc.value_description}"
            )
        elif isinstance(doc, SqlDocument):
            return f"{doc.question.lower()} {doc.hint.lower()}"
        elif isinstance(doc, HintDocument):
            return doc.hint
        else:
            return doc.text

    def _add_document_with_embedding(self, doc: BaseThothDocument) -> str:
        """Add document with embedding."""
        haystack_doc = self._convert_to_haystack_document(doc)
        
        # Generate embedding
        embedder = self._get_document_embedder()
        result = embedder.run(documents=[haystack_doc])
        embedded_docs = result["documents"]
        
        # Store document
        self.document_store.write_documents(
            embedded_docs, 
            policy=DuplicatePolicy.OVERWRITE
        )
        
        return embedded_docs[0].id

    def add_column_description(self, doc: ColumnNameDocument) -> str:
        """Add a column description document."""
        return self._add_document_with_embedding(doc)

    def add_sql(self, doc: SqlDocument) -> str:
        """Add an SQL document."""
        return self._add_document_with_embedding(doc)

    def add_hint(self, doc: HintDocument) -> str:
        """Add a hint document."""
        return self._add_document_with_embedding(doc)

    def search_similar(
        self,
        query: str,
        doc_type: ThothType,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> List[BaseThothDocument]:
        """Search for similar documents."""
        if not query:
            return []
            
        try:
            # Create filter for document type
            filters = {
                "field": "meta.thoth_type",
                "operator": "==",
                "value": doc_type.value
            }
            
            # Use search pipeline
            pipeline = self._get_search_pipeline()
            result = pipeline.run({
                "embedder": {"text": query},
                "retriever": {"top_k": top_k}
            })
            
            documents = result.get("retriever", {}).get("documents", [])
            
            # Convert and filter by score
            thoth_docs = []
            for doc in documents:
                if hasattr(doc, 'score') and doc.score is not None:
                    if doc.score >= score_threshold:
                        thoth_doc = self._convert_from_haystack_document(doc)
                        if thoth_doc:
                            thoth_docs.append(thoth_doc)
                            
            return thoth_docs
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[BaseThothDocument]:
        """Get a document by ID."""
        try:
            filters = {
                "operator": "OR",
                "conditions": [
                    {"field": "meta.thoth_id", "operator": "==", "value": doc_id},
                    {"field": "id", "operator": "==", "value": doc_id}
                ]
            }
            
            documents = self.document_store.filter_documents(filters=filters)
            if documents:
                return self._convert_from_haystack_document(documents[0])
                
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            
        return None

    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        try:
            self.document_store.delete_documents([doc_id])
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")

    def bulk_add_documents(self, documents: List[BaseThothDocument]) -> List[str]:
        """Add multiple documents in batch."""
        if not documents:
            return []
            
        haystack_docs = [self._convert_to_haystack_document(doc) for doc in documents]
        
        # Generate embeddings in batch
        embedder = self._get_document_embedder()
        result = embedder.run(documents=haystack_docs)
        embedded_docs = result["documents"]
        
        # Store all documents
        self.document_store.write_documents(
            embedded_docs,
            policy=DuplicatePolicy.OVERWRITE
        )
        
        return [doc.id for doc in embedded_docs]

    def _get_all_documents(self) -> List[BaseThothDocument]:
        """Get all documents."""
        try:
            haystack_docs = self.document_store.filter_documents()
            return [
                doc for doc in [
                    self._convert_from_haystack_document(h_doc)
                    for h_doc in haystack_docs
                ]
                if doc is not None
            ]
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            count = self.document_store.count_documents()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": self.embedding_model,
                "embedding_dim": self.embedding_dim,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                "collection_name": self.collection_name,
                "total_documents": 0,
                "embedding_model": self.embedding_model,
                "embedding_dim": self.embedding_dim,
            }
