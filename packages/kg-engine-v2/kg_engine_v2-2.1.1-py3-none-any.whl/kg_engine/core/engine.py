"""
Main Knowledge Graph Engine v2
"""
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import (
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet, 
    SearchResult, QueryResponse, RelationshipStatus
)
from ..llm import LLMInterface
from ..storage import VectorStore
from ..config import Neo4jConfig
from ..storage import GraphDB
from ..utils import DateParser

DEFAULT_MODEL = "gpt-4.1-nano"  # Default model for OpenAI

class KnowledgeGraphEngineV2:
    """
    Advanced Knowledge Graph Engine with:
    - LLM-powered entity/relationship extraction
    - Vector search capabilities
    - Temporal relationship tracking
    - Smart duplicate detection and conflict resolution
    """
    
    def __init__(self, api_key: str = "ollama", model: str = DEFAULT_MODEL,
                 base_url: str = None, vector_collection: str = "kg_v2", 
                 use_memory_store: bool = False, vector_store_type: str = None,
                 neo4j_config: Neo4jConfig = None):
        """
        Initialize the engine with all components
        
        Args:
            api_key: API key for LLM operations (use "ollama" for local Ollama)
            model: Model name (e.g., "llama3.2:3b", "phi3:mini", "gpt-4")
            base_url: Custom base URL (e.g., "http://localhost:11434/v1" for Ollama)
            vector_collection: Name for the vector store collection
            use_memory_store: Use in-memory vector store instead of persistent
            vector_store_type: Type of vector store (only "neo4j" supported)
            neo4j_config: Neo4j configuration (required if vector_store_type is "neo4j")
        """
        self.llm = LLMInterface(api_key=api_key, model=model, base_url=base_url)
        self.vector_store = VectorStore(
            collection_name=vector_collection, 
            use_memory=use_memory_store,
            store_type=vector_store_type,
            neo4j_config=neo4j_config
        )
        self.graph_db = GraphDB(neo4j_config)
        self.date_parser = DateParser()
        
        print("🚀 Knowledge Graph Engine v2 initialized")
        print(f"   - Vector store: {vector_collection} ({self.vector_store.get_store_type().value})")
        print(f"   - Graph database: Neo4j (persistent)")
        provider = "Ollama" if api_key == "ollama" or base_url else "OpenAI"
        print(f"   - LLM interface: {model} via {provider}")
    
    def process_input(self, items: List[InputItem]) -> Dict[str, Any]:
        """
        Process input items and update the knowledge graph
        
        Args:
            items: List of InputItem objects to process
            
        Returns:
            Dictionary with processing results and statistics
        """
        start_time = time.time()
        results = {
            "processed_items": 0,
            "new_edges": 0,
            "updated_edges": 0,
            "obsoleted_edges": 0,
            "duplicates_ignored": 0,
            "errors": []
        }
        
        for item in items:
            try:
                # Extract entities and relationships using LLM
                extracted_info = self.llm.extract_entities_relationships(item.description)
                
                if not extracted_info:
                    results["errors"].append(f"No relationships extracted from: {item.description}")
                    continue
                
                # Parse dates
                from_date = self.date_parser.parse_date(item.from_date)
                to_date = self.date_parser.parse_date(item.to_date)
                
                # Process each extracted relationship
                for info in extracted_info:
                    edge_result = self._process_relationship(info, item, from_date, to_date)
                    
                    # Update results
                    if edge_result["action"] == "created":
                        results["new_edges"] += 1
                    elif edge_result["action"] == "updated":
                        results["updated_edges"] += 1
                    elif edge_result["action"] == "obsoleted":
                        # Use the count from the edge_result if available
                        if "count" in edge_result:
                            results["obsoleted_edges"] += edge_result["count"]
                        else:
                            results["obsoleted_edges"] += 1
                    elif edge_result["action"] == "duplicate":
                        results["duplicates_ignored"] += 1
                    elif edge_result["action"] == "error":
                        results["errors"].append(edge_result["message"])
                
                results["processed_items"] += 1
                
            except Exception as e:
                results["errors"].append(f"Error processing item '{item.description}': {str(e)}")
        
        processing_time = time.time() - start_time
        results["processing_time_ms"] = processing_time * 1000
        
        return results
    
    def _process_relationship(self, extracted_info, input_item: InputItem, 
                             from_date: Optional[datetime], to_date: Optional[datetime]) -> Dict[str, Any]:
        """Process a single extracted relationship"""
        
        try:
            # Create edge metadata
            metadata = EdgeMetadata(
                summary=extracted_info.summary,
                from_date=from_date,
                to_date=to_date,
                confidence=extracted_info.confidence,
                source=input_item.metadata.get("source", "user_input"),
                user_id=input_item.metadata.get("user_id"),  # Extract user_id from metadata
                additional_metadata={k: v for k, v in input_item.metadata.items() if k not in ["source", "user_id"]}
            )
            
            # Handle negations (obsoleting existing relationships)
            if extracted_info.is_negation:
                metadata.obsolete = True
                metadata.status = RelationshipStatus.OBSOLETE
                if not to_date:
                    metadata.to_date = datetime.now()
            
            # Create edge
            edge = GraphEdge(
                subject=extracted_info.subject,
                relationship=extracted_info.relationship,
                object=extracted_info.object,
                metadata=metadata
            )
            
            # Check for duplicates
            duplicates = self.graph_db.find_duplicate_edges(edge)
            if duplicates and not extracted_info.is_negation:
                return {"action": "duplicate", "message": f"Duplicate ignored: {extracted_info.summary}"}
            
            # Use semantic search to find potential conflicts
            # Search for relationships involving the same subject
            conflict_search_query = f"{extracted_info.subject} {extracted_info.relationship}"
            conflict_search_response = self.search(conflict_search_query, search_type="semantic", k=10)
            unique_conflict_results = conflict_search_response.results
            
            conflicts_to_obsolete = []
            
            # Filter for actual conflicts: same subject, similar relationship, different object
            for result in unique_conflict_results:
                conflict_edge = result.triplet.edge
                
                # Check if this is a conflict:
                # - Same subject (normalized)
                # - Different object
                # - Not already obsolete
                # - High semantic similarity (captured by being in top results)
                subject_match = self.graph_db._normalize_entity_name(conflict_edge.subject) == \
                               self.graph_db._normalize_entity_name(extracted_info.subject)
                
                different_object = self.graph_db._normalize_entity_name(conflict_edge.object) != \
                                  self.graph_db._normalize_entity_name(extracted_info.object)
                
                if subject_match and different_object and not conflict_edge.metadata.obsolete:
                    # This is a potential conflict - verify it's semantically similar enough
                    # Lower threshold for location-based relationships since they're clearly conflicts
                    location_relationships = ["LIVES_IN", "RESIDES_IN", "LOCATED_IN", "BASED_IN", "MOVED_TO"]
                    if (extracted_info.relationship in location_relationships and 
                        conflict_edge.relationship in location_relationships):
                        # Location conflicts are always conflicts regardless of score
                        conflicts_to_obsolete.append(conflict_edge)
                    elif result.score > 0.6:  # General threshold for semantic similarity
                        conflicts_to_obsolete.append(conflict_edge)
            
            # Handle conflicts by obsoleting old edges
            for conflict in conflicts_to_obsolete:
                if not extracted_info.is_negation:  # Only obsolete if new edge isn't a negation
                    conflict.metadata.obsolete = True
                    conflict.metadata.status = RelationshipStatus.OBSOLETE
                    conflict.metadata.to_date = from_date or datetime.now()
                    
                    # Update in both stores
                    self.graph_db.update_edge(conflict)
                    
                    # Update in vector store
                    conflict_triplet = GraphTriplet(edge=conflict, vector_id=conflict.edge_id)
                    self.vector_store.update_triplet(conflict_triplet)
            
            # Add/update the new edge
            if extracted_info.is_negation:
                # Use semantic search to find similar relationships to obsolete
                # Construct multiple search queries to capture different phrasings
                search_queries = [
                    f"{extracted_info.subject} {extracted_info.relationship} {extracted_info.object}",
                    f"{extracted_info.subject} {extracted_info.object}",  # Without specific relationship
                    extracted_info.summary  # The natural language summary
                ]
                
                # Use semantic search to find similar relationships
                # We need to search without filtering obsolete edges for this specific case
                all_search_results = []
                for query in search_queries:
                    results = self.vector_store.search(query, k=5, filter_obsolete=False)
                    all_search_results.extend(results)
                
                # Deduplicate results
                seen_edges = set()
                search_results = []
                for result in all_search_results:
                    if result.triplet.edge.edge_id not in seen_edges:
                        seen_edges.add(result.triplet.edge.edge_id)
                        search_results.append(result)
                
                
                obsoleted_count = 0
                obsoleted_relationships = []
                
                # Filter results to find relevant matches based on entity similarity
                for result in search_results:
                    edge = result.triplet.edge
                    
                    # Check if this is a relevant match:
                    # - Same subject (normalized)
                    # - Similar/related relationship (captured by semantic search)
                    # - Same or similar object
                    subject_match = self.graph_db._normalize_entity_name(edge.subject) == \
                                   self.graph_db._normalize_entity_name(extracted_info.subject)
                    
                    object_match = self.graph_db._normalize_entity_name(edge.object) == \
                                  self.graph_db._normalize_entity_name(extracted_info.object)
                    
                    # If subject matches and object matches (or similar), and it's not already obsolete
                    # For object matching, we can be more flexible with locations/organizations
                    object_similarity = self.graph_db._normalize_entity_name(edge.object) == \
                                       self.graph_db._normalize_entity_name(extracted_info.object) or \
                                       (extracted_info.object.lower() in edge.object.lower()) or \
                                       (edge.object.lower() in extracted_info.object.lower())
                    
                    
                    if subject_match and object_similarity and not edge.metadata.obsolete:
                        # Mark as obsolete
                        edge.metadata.obsolete = True
                        edge.metadata.status = RelationshipStatus.OBSOLETE
                        edge.metadata.to_date = to_date or datetime.now()
                        
                        self.graph_db.update_edge(edge)
                        self.vector_store.update_triplet(result.triplet)
                        
                        obsoleted_count += 1
                        obsoleted_relationships.append(f"{edge.subject} {edge.relationship} {edge.object}")
                
                if obsoleted_count > 0:
                    return {
                        "action": "obsoleted", 
                        "count": obsoleted_count,
                        "obsoleted_relationships": obsoleted_relationships,
                        "message": f"Obsoleted {obsoleted_count} similar relationship(s)",
                        "search_info": f"Searched for: {search_queries}, found {len(search_results)} candidates"
                    }
                else:
                    return {"action": "error", "message": f"No existing relationship found to obsolete: {extracted_info.summary}"}
            
            else:
                # Add new edge to both stores
                self.graph_db.add_edge(edge)
                
                triplet = GraphTriplet(edge=edge)
                self.vector_store.add_triplet(triplet)
                
                if conflicts_to_obsolete:
                    return {"action": "updated", "conflicts_resolved": len(conflicts_to_obsolete)}
                else:
                    return {"action": "created"}
            
        except Exception as e:
            return {"action": "error", "message": str(e)}
    
    def search(self, query: str, search_type: str = "both", k: int = 10) -> QueryResponse:
        """
        Search the knowledge graph using natural language
        
        Args:
            query: Natural language query
            search_type: "direct", "semantic", or "both"
            k: Number of results to return
            
        Returns:
            QueryResponse with results and generated answer
        """
        start_time = time.time()
        
        try:
            # Parse the query using LLM
            parsed_query = self.llm.parse_query(query, self.graph_db.get_relationships())
            
            all_results = []
            
            # Direct graph search
            if search_type in ["direct", "both"]:
                graph_results = self._graph_search(parsed_query, k)
                all_results.extend(graph_results)
            
            # Semantic vector search  
            if search_type in ["semantic", "both"]:
                vector_results = self._semantic_search(query, k)
                all_results.extend(vector_results)
            
            # Remove duplicates and sort by score
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.score, reverse=True)
            
            # Limit results
            final_results = unique_results[:k]
            
            # Generate natural language answer
            answer = None
            if final_results:
                result_summaries = [r.triplet.edge.metadata.summary for r in final_results[:5]]
                answer = self.llm.generate_answer(query, result_summaries)
            
            query_time = time.time() - start_time
            
            return QueryResponse(
                results=final_results,
                total_found=len(unique_results),
                query_time_ms=query_time * 1000,
                answer=answer,
                confidence=self._calculate_confidence(final_results)
            )
            
        except Exception as e:
            query_time = time.time() - start_time
            return QueryResponse(
                results=[],
                total_found=0,
                query_time_ms=query_time * 1000,
                answer=f"Error processing query: {str(e)}",
                confidence=0.0
            )
    
    def _graph_search(self, parsed_query, k: int) -> List[SearchResult]:
        """Direct graph database search"""
        results = []
        
        try:
            # Search by entities
            for entity in parsed_query.entities:
                triplets = self.graph_db.get_entity_relationships(entity, filter_obsolete=True)
                
                for triplet in triplets[:k]:
                    # Score based on relationship match
                    score = 1.0
                    if parsed_query.relationships:
                        if triplet.edge.relationship in parsed_query.relationships:
                            score = 1.0
                        else:
                            score = 0.7
                    
                    result = SearchResult(
                        triplet=triplet,
                        score=score,
                        source="graph",
                        explanation=f"Direct graph match for entity '{entity}'"
                    )
                    results.append(result)
            
            # Search by relationships
            for relationship in parsed_query.relationships:
                triplets = self.graph_db.find_edges(relationship=relationship, filter_obsolete=True)
                
                for triplet in triplets[:k]:
                    # Higher score if entity also matches
                    score = 0.8
                    if parsed_query.entities:
                        for entity in parsed_query.entities:
                            if (entity.lower() in triplet.edge.subject.lower() or 
                                entity.lower() in triplet.edge.object.lower()):
                                score = 1.0
                                break
                    
                    result = SearchResult(
                        triplet=triplet,
                        score=score,
                        source="graph",
                        explanation=f"Direct graph match for relationship '{relationship}'"
                    )
                    results.append(result)
        
        except Exception as e:
            print(f"Error in graph search: {e}")
        
        return results
    
    def _semantic_search(self, query: str, k: int) -> List[SearchResult]:
        """Semantic vector search"""
        try:
            return self.vector_store.search(query, k=k, filter_obsolete=True)
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on edge ID"""
        seen_edge_ids = set()
        unique_results = []
        
        for result in results:
            edge_id = result.triplet.edge.edge_id
            if edge_id not in seen_edge_ids:
                seen_edge_ids.add(edge_id)
                unique_results.append(result)
        
        return unique_results
    
    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Calculate overall confidence in the results"""
        if not results:
            return 0.0
        
        # Average of top 3 scores, weighted by position
        weights = [0.5, 0.3, 0.2]
        total_score = 0.0
        
        for i, result in enumerate(results[:3]):
            weight = weights[i] if i < len(weights) else 0.1
            total_score += result.score * weight
        
        return min(total_score, 1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        return {
            "graph_stats": self.graph_db.get_stats(),
            "vector_stats": self.vector_store.get_stats(),
            "relationships": self.graph_db.get_relationships(),
            "entities": len(self.graph_db.get_entities())
        }
    
    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the entire knowledge graph"""
        return {
            "graph_data": self.graph_db.export_to_dict(),
            "vector_stats": self.vector_store.get_stats(),
            "export_timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }
    
    def import_knowledge_graph(self, data: Dict[str, Any]) -> bool:
        """Import knowledge graph data"""
        try:
            if "graph_data" in data:
                self.graph_db.import_from_dict(data["graph_data"])
                
                # Rebuild vector store from graph data
                self.vector_store.clear_collection()
                
                # Get all edges from Neo4j graph
                triplets = self.graph_db.find_edges(filter_obsolete=False)  # Get all edges including obsolete
                
                if triplets:
                    self.vector_store.add_triplets(triplets)
                
                return True
            else:
                return False
        except Exception as e:
            print(f"Error importing knowledge graph: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """Clear all data from both graph and vector stores"""
        try:
            graph_cleared = self.graph_db.clear_graph()
            vector_cleared = self.vector_store.clear_collection()
            return graph_cleared and vector_cleared
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False