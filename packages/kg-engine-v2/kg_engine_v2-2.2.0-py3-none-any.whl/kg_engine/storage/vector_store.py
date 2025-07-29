"""
Vector store implementation for Knowledge Graph Engine v2 with configurable backends
"""
import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from sentence_transformers import SentenceTransformer
from ..models import GraphTriplet, SearchResult
from .vector_store_factory import VectorStoreFactory, VectorStoreType
from .vector_store_adapter import VectorStoreAdapter, Neo4jAdapter
from ..config import Neo4jConfig


class VectorStore:
    """Vector store for graph triplets with semantic search capabilities"""
    
    def __init__(
        self, 
        collection_name: str = "kg_triplets", 
        model_name: str = "all-MiniLM-L6-v2", 
        use_memory: bool = False,
        store_type: Union[str, VectorStoreType] = None,
        neo4j_config: Optional[Neo4jConfig] = None
    ):
        self.collection_name = collection_name
        self.model_name = model_name
        self.use_memory = use_memory
        self.neo4j_config = neo4j_config
        
        # Determine store type from environment or parameter
        if store_type is None:
            store_type = os.getenv("VECTOR_STORE_TYPE", "neo4j")
        
        if isinstance(store_type, str):
            store_type = VectorStoreType(store_type.lower())
        
        self.store_type = store_type
        
        # Create the appropriate vector store implementation
        self._backend_store = VectorStoreFactory.create_vector_store(
            store_type=store_type,
            collection_name=collection_name,
            model_name=model_name,
            use_memory=use_memory,
            neo4j_config=neo4j_config
        )
        
        # Create adapter for unified API (Neo4j only)
        self._adapter = Neo4jAdapter(self._backend_store)
        
        # Get initial stats
        try:
            stats = self._adapter.get_stats()
            count = stats.get("total_triplets", 0)
            print(f"Vector store ({store_type.value}) initialized with {count} existing triplets")
        except Exception as e:
            print(f"Vector store ({store_type.value}) initialized (stats unavailable: {e})")
    
    def _create_clean_metadata(self, edge) -> dict:
        """Create metadata dict with None values properly handled"""
        metadata = {
            "subject": edge.subject or "",
            "relationship": edge.relationship or "",
            "object": edge.object or "",
            "summary": edge.metadata.summary or "",
            "obsolete": bool(edge.metadata.obsolete),
            "status": edge.metadata.status.value if edge.metadata.status else "active",
            "confidence": float(edge.metadata.confidence) if edge.metadata.confidence is not None else 1.0,
            "created_at": edge.metadata.created_at.isoformat() if edge.metadata.created_at else "",
        }
        
        # Handle optional date fields
        if edge.metadata.from_date:
            metadata["from_date"] = edge.metadata.from_date.isoformat()
        else:
            metadata["from_date"] = ""
            
        if edge.metadata.to_date:
            metadata["to_date"] = edge.metadata.to_date.isoformat()
        else:
            metadata["to_date"] = ""
            
        if edge.metadata.source:
            metadata["source"] = str(edge.metadata.source)
        else:
            metadata["source"] = ""
        
        return metadata
    
    def add_triplet(self, triplet: GraphTriplet) -> str:
        """Add a single triplet to the vector store"""
        return self._adapter.add_triplet(triplet)
    
    def add_triplets(self, triplets: List[GraphTriplet]) -> List[str]:
        """Add multiple triplets in batch"""
        return self._adapter.add_triplets(triplets)
    
    def update_triplet(self, triplet: GraphTriplet) -> bool:
        """Update an existing triplet"""
        return self._adapter.update_triplet(triplet)
    
    def delete_triplet(self, vector_id: str) -> bool:
        """Delete a triplet from the vector store"""
        return self._adapter.delete_triplet(vector_id)
    
    def search(self, query: str, k: int = 10, filter_obsolete: bool = True, 
               additional_filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Semantic search for triplets"""
        return self._adapter.search(query, k, filter_obsolete, additional_filters)
    
    def search_by_entity(self, entity: str, k: int = 10, filter_obsolete: bool = True) -> List[SearchResult]:
        """Search for triplets involving a specific entity"""
        return self._adapter.search_by_entity(entity, k, filter_obsolete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        stats = self._adapter.get_stats()
        stats["store_type"] = self.store_type.value
        return stats
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection"""
        return self._adapter.clear_collection()
    
    def get_backend_store(self):
        """Get the underlying backend store instance.
        
        Returns:
            The backend store instance (Neo4j)
        """
        return self._backend_store
    
    def get_store_type(self) -> VectorStoreType:
        """Get the current vector store type.
        
        Returns:
            The vector store type enum
        """
        return self.store_type