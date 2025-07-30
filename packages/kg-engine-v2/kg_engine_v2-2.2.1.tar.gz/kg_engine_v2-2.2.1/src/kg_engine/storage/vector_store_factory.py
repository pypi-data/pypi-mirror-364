"""Factory for creating vector store instances with configurable backends."""

import os
from typing import Optional, Union, Dict, Any
from enum import Enum

from ..config import Neo4jConfig
from .neo4j_vector_store import Neo4jKnowledgeGraphVectorStore


class VectorStoreType(Enum):
    """Supported vector store backends."""
    NEO4J = "neo4j"


class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    @staticmethod
    def create_vector_store(
        store_type: Union[VectorStoreType, str] = None,
        collection_name: str = "kg_triplets",
        model_name: str = "all-MiniLM-L6-v2",
        use_memory: bool = False,
        neo4j_config: Optional[Neo4jConfig] = None,
        **kwargs
    ):
        """Create a vector store instance based on configuration.
        
        Args:
            store_type: Type of vector store to create
            collection_name: Name of the collection/index
            model_name: Embedding model name
            use_memory: Use in-memory storage (ChromaDB only)
            neo4j_config: Neo4j configuration
            **kwargs: Additional configuration options
            
        Returns:
            Vector store instance
        """
        # Determine store type from environment if not specified
        if store_type is None:
            store_type_str = os.getenv("VECTOR_STORE_TYPE", "neo4j").lower()
            store_type = VectorStoreType(store_type_str)
        elif isinstance(store_type, str):
            store_type = VectorStoreType(store_type.lower())
        
        if store_type == VectorStoreType.NEO4J:
            return VectorStoreFactory._create_neo4j_store(
                neo4j_config or Neo4jConfig(),
                model_name,
                collection_name,
                **kwargs
            )
        
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")
    
    @staticmethod
    def _create_neo4j_store(
        neo4j_config: Neo4jConfig,
        model_name: str,
        index_name: str,
        **kwargs
    ):
        """Create Neo4j vector store instance."""
        # Use a consistent index name regardless of collection name
        return Neo4jKnowledgeGraphVectorStore(
            config=neo4j_config,
            embedding_model=model_name,
            index_name="triplet_embedding_index",
            node_label="Triplet",
            **kwargs
        )
    
    @staticmethod
    def get_supported_types() -> list[VectorStoreType]:
        """Get list of supported vector store types.
        
        Returns:
            List of supported vector store types
        """
        return list(VectorStoreType)
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration for vector stores.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "store_type": os.getenv("VECTOR_STORE_TYPE", "neo4j"),
            "collection_name": "kg_triplets",
            "model_name": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        }