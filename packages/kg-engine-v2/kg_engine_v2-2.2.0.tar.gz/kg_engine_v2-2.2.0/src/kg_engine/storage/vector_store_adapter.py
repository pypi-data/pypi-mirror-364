"""Adapter to maintain API compatibility between ChromaDB and Neo4j vector stores."""

from typing import List, Dict, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod

from ..models import GraphTriplet, SearchResult
from .neo4j_vector_store import Neo4jKnowledgeGraphVectorStore


class VectorStoreAdapter(ABC):
    """Abstract adapter for vector store operations."""
    
    @abstractmethod
    def add_triplet(self, triplet: GraphTriplet) -> str:
        """Add a single triplet to the vector store."""
        pass
    
    @abstractmethod
    def add_triplets(self, triplets: List[GraphTriplet]) -> List[str]:
        """Add multiple triplets in batch."""
        pass
    
    @abstractmethod
    def update_triplet(self, triplet: GraphTriplet) -> bool:
        """Update an existing triplet."""
        pass
    
    @abstractmethod
    def delete_triplet(self, vector_id: str) -> bool:
        """Delete a triplet from the vector store."""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 10, filter_obsolete: bool = True, 
              additional_filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Semantic search for triplets."""
        pass
    
    @abstractmethod
    def search_by_entity(self, entity: str, k: int = 10, filter_obsolete: bool = True) -> List[SearchResult]:
        """Search for triplets involving a specific entity."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        pass
    
    @abstractmethod
    def clear_collection(self) -> bool:
        """Clear all data from the collection."""
        pass



class Neo4jAdapter(VectorStoreAdapter):
    """Adapter for Neo4j vector store."""
    
    def __init__(self, neo4j_store: Neo4jKnowledgeGraphVectorStore):
        """Initialize with Neo4j vector store instance."""
        self.store = neo4j_store
    
    def add_triplet(self, triplet: GraphTriplet) -> str:
        """Add a single triplet to the vector store."""
        # Convert GraphTriplet to the format expected by Neo4jKnowledgeGraphVectorStore
        neo4j_triplet = self._convert_to_neo4j_triplet(triplet)
        ids = self.store.add_triplets([neo4j_triplet])
        return ids[0] if ids else None
    
    def add_triplets(self, triplets: List[GraphTriplet]) -> List[str]:
        """Add multiple triplets in batch."""
        neo4j_triplets = [self._convert_to_neo4j_triplet(t) for t in triplets]
        return self.store.add_triplets(neo4j_triplets)
    
    def update_triplet(self, triplet: GraphTriplet) -> bool:
        """Update an existing triplet."""
        # For Neo4j update, we use the same triplet as both old and new
        # The Neo4j store will find and update based on the triplet key
        neo4j_triplet = self._convert_to_neo4j_triplet(triplet)
        return self.store.update_triplet(neo4j_triplet, neo4j_triplet)
    
    def delete_triplet(self, vector_id: str) -> bool:
        """Delete a triplet from the vector store."""
        # For Neo4j, we need to construct a triplet object to delete
        # This is a limitation - we'd need to query first to get the triplet details
        # For now, return False as this operation needs redesign
        return False
    
    def search(self, query: str, k: int = 10, filter_obsolete: bool = True, 
              additional_filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Semantic search for triplets."""
        # Build filters
        filters = additional_filters or {}
        if filter_obsolete:
            filters["obsolete"] = False
        
        # Query Neo4j store
        results = self.store.query_similar(query, k, filters)
        
        # Convert results to SearchResult format
        search_results = []
        for graph_triplet, score in results:
            # neo4j_triplet is already a GraphTriplet, no conversion needed
            search_result = SearchResult(
                triplet=graph_triplet,
                score=score,
                source="neo4j_vector",
                explanation=f"Neo4j vector similarity: {score:.3f}"
            )
            search_results.append(search_result)
        
        return search_results
    
    def search_by_entity(self, entity: str, k: int = 10, filter_obsolete: bool = True) -> List[SearchResult]:
        """Search for triplets involving a specific entity."""
        results = self.store.search_entities([entity], k)
        
        # Convert results to SearchResult format
        search_results = []
        for graph_triplet, score in results:
            # Already a GraphTriplet, no conversion needed
            search_result = SearchResult(
                triplet=graph_triplet,
                score=score,
                source="neo4j_entity",
                explanation=f"Entity match for '{entity}'"
            )
            search_results.append(search_result)
        
        return search_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        neo4j_stats = self.store.get_stats()
        
        # Convert to format expected by existing code
        return {
            "total_triplets": neo4j_stats.get("triplet_count", 0),
            "active_triplets": neo4j_stats.get("triplet_count", 0),  # Neo4j doesn't separate by default
            "obsolete_triplets": 0,  # Would need separate query
            "collection_name": neo4j_stats.get("node_label", "Triplet"),
            "model_name": neo4j_stats.get("embedding_model", "unknown")
        }
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection."""
        return self.store.clear_all()
    
    def _convert_to_neo4j_triplet(self, graph_triplet: GraphTriplet):
        """Convert GraphTriplet to Neo4j triplet format."""
        from ..models import GraphTriplet as Neo4jGraphTriplet, GraphEdge, EdgeMetadata
        
        return Neo4jGraphTriplet(
            edge=GraphEdge(
                subject=graph_triplet.edge.subject,
                relationship=graph_triplet.edge.relationship,
                object=graph_triplet.edge.object,
                metadata=EdgeMetadata(
                    summary=graph_triplet.edge.metadata.summary,
                    confidence=graph_triplet.edge.metadata.confidence or 0.0,
                    status=graph_triplet.edge.metadata.status,
                    obsolete=graph_triplet.edge.metadata.obsolete,
                    created_at=graph_triplet.edge.metadata.created_at,
                    from_date=graph_triplet.edge.metadata.from_date,
                    to_date=graph_triplet.edge.metadata.to_date,
                    source=graph_triplet.edge.metadata.source or "migration"
                )
            )
        )
    
    def _convert_from_neo4j_triplet(self, neo4j_triplet):
        """Convert Neo4j triplet back to GraphTriplet format."""
        from ..models import GraphEdge, EdgeMetadata, GraphTriplet
        
        metadata = EdgeMetadata(
            summary=neo4j_triplet.summary,
            created_at=neo4j_triplet.created_at,
            from_date=neo4j_triplet.from_date,
            to_date=neo4j_triplet.to_date,
            obsolete=neo4j_triplet.obsolete,
            status=neo4j_triplet.status,
            confidence=neo4j_triplet.confidence,
            source=neo4j_triplet.source
        )
        
        edge = GraphEdge(
            subject=neo4j_triplet.subject,
            relationship=neo4j_triplet.relationship,
            object=neo4j_triplet.object,
            metadata=metadata,
            edge_id=f"{neo4j_triplet.subject}_{neo4j_triplet.relationship}_{neo4j_triplet.object}"
        )
        
        return GraphTriplet(
            edge=edge,
            vector_text=neo4j_triplet.to_vector_text() if hasattr(neo4j_triplet, 'to_vector_text') else None
        )