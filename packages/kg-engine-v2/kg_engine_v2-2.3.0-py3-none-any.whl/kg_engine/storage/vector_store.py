"""
Vector store implementation for Knowledge Graph Engine v2 using Neo4j GraphDB
"""
from typing import List, Dict, Any, Optional
from ..models import GraphTriplet, SearchResult
from .graph_db import GraphDB
from ..config import Neo4jConfig


class VectorStore:
    """Neo4j vector store for graph triplets with semantic search capabilities"""
    
    def __init__(
        self, 
        collection_name: str = "kg_triplets", 
        model_name: str = "all-MiniLM-L6-v2", 
        store_type: str = "neo4j",  # Keep for compatibility but always use neo4j
        neo4j_config: Optional[Neo4jConfig] = None,
        **kwargs  # Accept unused params for compatibility
    ):
        self.collection_name = collection_name
        self.model_name = model_name
        self.neo4j_config = neo4j_config or Neo4jConfig()
        
        # Use GraphDB for vector operations
        self._store = GraphDB(self.neo4j_config)
        
        # Get initial stats
        try:
            stats = self.get_stats()
            count = stats.get("total_triplets", 0)
            print(f"Vector store (neo4j) initialized with {count} existing triplets")
        except Exception as e:
            print(f"Vector store (neo4j) initialized (stats unavailable: {e})")
    
    def add_triplet(self, triplet: GraphTriplet) -> str:
        """Add a single triplet to the vector store"""
        ids = self.add_triplets([triplet])
        return ids[0] if ids else None
    
    def add_triplets(self, triplets: List[GraphTriplet]) -> List[str]:
        """Add multiple triplets in batch"""
        # GraphDB handles triplets through add_edge_data
        ids = []
        for triplet in triplets:
            # Extract graph data from triplet
            if triplet.edge.has_graph_data():
                subject, relationship, obj = triplet.edge.get_graph_data()
                from ..models import EdgeData
                edge_data = EdgeData(
                    subject=subject,
                    relationship=relationship,
                    object=obj,
                    metadata=triplet.edge.metadata,
                    edge_id=triplet.edge.edge_id
                )
                success = self._store.add_edge_data(edge_data)
                if success:
                    ids.append(triplet.edge.edge_id)
        return ids
    
    def update_triplet(self, triplet: GraphTriplet) -> bool:
        """Update an existing triplet"""
        try:
            return self._store.update_edge_metadata(triplet.edge.edge_id, triplet.edge.metadata)
        except Exception:
            return False
    
    def delete_triplet(self, vector_id: str) -> bool:
        """Delete a triplet from the vector store"""
        # This operation is not commonly used by the engine
        return False
    
    def search(self, query: str, k: int = 10, filter_obsolete: bool = True, 
               additional_filters: Dict[str, Any] = None) -> List[SearchResult]:
        """Semantic search for triplets"""
        # Use GraphDB's vector similarity search
        from sentence_transformers import SentenceTransformer
        
        # Get embedding model
        model = SentenceTransformer(self.model_name)
        query_vector = model.encode(query).tolist()
        
        # Use GraphDB's vector similarity search
        return self._store.vector_similarity_search_with_graph(
            vector=query_vector,
            k=k,
            filter_obsolete=filter_obsolete
        )
    
    def search_by_entity(self, entity: str, k: int = 10, filter_obsolete: bool = True) -> List[SearchResult]:
        """Search for triplets involving a specific entity"""
        # Use GraphDB's entity relationship exploration
        triplets = self._store.get_entity_relationships_optimized(
            entity=entity,
            filter_obsolete=filter_obsolete,
            max_depth=1,
            limit=k
        )
        
        # Convert to SearchResult format
        search_results = []
        for triplet in triplets:
            search_result = SearchResult(
                triplet=triplet,
                score=1.0,  # Entity matches have perfect score
                source="neo4j_entity",
                explanation=f"Entity match for '{entity}'"
            )
            search_results.append(search_result)
        
        return search_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        graph_stats = self._store.get_stats()
        
        # Convert to format expected by existing code
        # GraphDB returns total_edges, active_edges, obsolete_edges
        return {
            "total_triplets": graph_stats.get("total_edges", 0),
            "active_triplets": graph_stats.get("active_edges", 0),
            "obsolete_triplets": graph_stats.get("obsolete_edges", 0),
            "collection_name": self.collection_name,
            "model_name": self.model_name,
            "store_type": "neo4j"
        }
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection"""
        return self._store.clear_graph()
    
    def get_backend_store(self):
        """Get the underlying backend store instance.
        
        Returns:
            The GraphDB instance
        """
        return self._store