"""
Optimized Knowledge Graph Engine v2 - Streamlined Implementation
"""
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

from ..models import (
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet,
    SearchResult, QueryResponse, RelationshipStatus, EdgeData, SearchType
)
from ..models.classifier_map import ClassifierMap
from ..llm import LLMInterface
from ..storage import VectorStore, GraphDB
from ..config import Neo4jConfig
from ..utils.date_parser import parse_date

DEFAULT_MODEL = "gpt-4o"


class KnowledgeGraphEngineV2:
    """
    Optimized Knowledge Graph Engine with:
    - LLM-powered entity/relationship extraction
    - Optimized Neo4j operations
    - Advanced conflict detection and temporal analysis
    - Vector search with graph integration
    """

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL,
                 base_url: str = None, vector_collection: str = "kg_v2",
                 neo4j_config: Neo4jConfig = None, bearer_token: str = None):
        """
        Initialize the optimized engine
        
        Args:
            api_key: API key for LLM operations (use "ollama" for local Ollama)
            model: Model name (e.g., "llama3.2:3b", "phi3:mini", "gpt-4")
            base_url: Custom base URL (e.g., "http://localhost:11434/v1" for Ollama)
            vector_collection: Name for the vector store collection
            neo4j_config: Neo4j configuration
        """
        self.graph_db = GraphDB(neo4j_config)
        self.vector_store = VectorStore(
            collection_name=vector_collection,
            store_type="neo4j",
            neo4j_config=neo4j_config
        )
        
        # Create embedder for classifier detection
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(self.vector_store.model_name)
        except Exception as e:
            logger.warning(f"Failed to initialize embedder: {e}")
            self.embedder = None
        
        self.classifier_map = ClassifierMap(self.graph_db)
        self.llm = LLMInterface(api_key=api_key, model=model, base_url=base_url, bearer_token=bearer_token, classifier_map=self.classifier_map, embedder=self.embedder)

        # Ensure performance indexes are created once during initialization
        self.graph_db._ensure_performance_indexes()

        print("🚀 Knowledge Graph Engine v2")
        print(f"   - Vector store: {vector_collection} (Neo4j)")
        provider = "Ollama" if api_key == "ollama" else "OpenAI"
        print(f"   - LLM interface: {model} via {base_url or provider}")

    def process_input(self, items: List[InputItem]) -> Dict[str, Any]:
        """
        Process input items using optimized graph operations
        
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
            "errors": [],
            "edge_results": []
        }

        for item in items:
            try:
                # Extract entities and relationships using LLM with classifier
                extracted_info = self.llm.extract_entities_relationships_with_classifier(item.description)
                if not extracted_info:
                    self._add_error(results, f"No relationships extracted from: {item.description}", item.description)
                    continue

                # Process each extracted relationship
                for info in extracted_info:
                    # Parse dates from extracted info (dates are extracted by LLM)
                    from_date = parse_date(info.from_date) if info.from_date else None
                    to_date = parse_date(info.to_date) if info.to_date else None
                    
                    edge_result = self._process_relationship(info, item, from_date, to_date)
                    
                    # Only add to results if it's not a duplicate (completely skip duplicates)
                    if edge_result.get("action") != "duplicate":
                        edge_result["input_description"] = item.description
                        edge_result["extracted_info"] = {
                            "subject": info.subject,
                            "relationship": info.relationship,
                            "object": info.object,
                            "summary": info.summary,
                            "confidence": info.confidence,
                            "is_negation": info.is_negation,
                            "from_date": info.from_date,
                            "to_date": info.to_date,
                            "category": info.category
                        }
                        
                        results["edge_results"].append(edge_result)
                        self._update_counters(results, edge_result)
                    else:
                        # Just count the duplicate but don't add to results
                        results["duplicates_ignored"] += 1

                results["processed_items"] += 1

            except Exception as e:
                self._add_error(results, f"Error processing item '{item.description}': {str(e)}", item.description)

        results["processing_time_ms"] = (time.time() - start_time) * 1000
        return results

    def _process_relationship(self, extracted_info, input_item: InputItem,
                              from_date: Optional[datetime], to_date: Optional[datetime]) -> Dict[str, Any]:
        """Process a single extracted relationship using optimized operations"""
        try:
            # Create edge metadata with category from classifier
            metadata = EdgeMetadata(
                summary=extracted_info.summary,
                from_date=from_date,
                to_date=to_date,
                confidence=extracted_info.confidence,
                source=input_item.metadata.get("source", "user_input"),
                user_id=input_item.metadata.get("user_id"),
                category=extracted_info.category,
                additional_metadata={k: v for k, v in input_item.metadata.items() 
                                   if k not in ["source", "user_id"]}
            )

            # Handle negations
            if extracted_info.is_negation:
                metadata.obsolete = True
                metadata.status = RelationshipStatus.OBSOLETE
                if not to_date:
                    metadata.to_date = datetime.now()

            # Create edge data
            edge_data = EdgeData(
                subject=extracted_info.subject,
                relationship=extracted_info.relationship,
                object=extracted_info.object,
                metadata=metadata
            )

            # Check for exact duplicates using optimized method
            duplicates = self.graph_db.find_duplicate_edges(edge_data)
            if duplicates and not extracted_info.is_negation:
                return {"action": "duplicate", "message": f"Duplicate ignored: {extracted_info.summary}"}

            # Handle explicit negations using optimized conflict detection
            if extracted_info.is_negation:
                return self._handle_negation(extracted_info, edge_data, to_date)
            else:
                return self._add_new_edge(edge_data)

        except Exception as e:
            return {"action": "error", "message": str(e)}

    def _handle_negation(self, extracted_info, edge_data: EdgeData, to_date: Optional[datetime]) -> Dict[str, Any]:
        """Handle negations using optimized conflict detection"""
        try:
            # Use optimized conflict detection to find relationships to obsolete
            conflicts = self.graph_db.detect_relationship_conflicts_optimized(
                entity_name=extracted_info.subject,
                relationship_type=extracted_info.relationship,
                confidence_threshold=0.3
            )

            obsoleted_count = 0
            obsoleted_relationships = []

            for conflict in conflicts:
                if extracted_info.object.lower() in conflict["conflicting_objects"]:
                    # Obsolete the matching edge
                    edge = conflict["higher_confidence_edge"]
                    edge.metadata.obsolete = True
                    edge.metadata.status = RelationshipStatus.OBSOLETE
                    edge.metadata.to_date = to_date or datetime.now()

                    self.graph_db.update_edge_metadata(edge.edge_id, edge.metadata)
                    
                    # Update vector store
                    triplet = GraphTriplet(edge=edge)
                    self.vector_store.update_triplet(triplet)

                    obsoleted_count += 1
                    subject = edge.get_subject_safe() or "Unknown"
                    relationship = edge.get_relationship_safe() or "Unknown"
                    obj = edge.get_object_safe() or "Unknown"
                    obsoleted_relationships.append(f"{subject} {relationship} {obj}")

            if obsoleted_count > 0:
                return {
                    "action": "obsoleted",
                    "count": obsoleted_count,
                    "obsoleted_relationships": obsoleted_relationships,
                    "message": f"Obsoleted {obsoleted_count} similar relationship(s)"
                }
            else:
                return {"action": "error", "message": f"No existing relationship found to obsolete: {extracted_info.summary}"}

        except Exception as e:
            return {"action": "error", "message": f"Error handling negation: {str(e)}"}

    def _add_new_edge(self, edge_data: EdgeData) -> Dict[str, Any]:
        """Add new edge using optimized graph operations (single call to avoid duplicates)"""
        try:
            # Only call graph_db.add_edge_data once - the vector store will be updated through Neo4j
            success = self.graph_db.add_edge_data(edge_data)
            if success:
                return {"action": "created"}
            else:
                return {"action": "error", "message": "Failed to add edge to graph"}
        except Exception as e:
            return {"action": "error", "message": str(e)}

    def search(self, query: str, search_type: SearchType = SearchType.BOTH, k: int = 10) -> QueryResponse:
        """
        Search using optimized graph and vector operations
        
        Args:
            query: Natural language query
            search_type: "direct", "semantic", or "both"
            k: Number of results to return
            
        Returns:
            QueryResponse with results and generated answer
        """

        print(f"Search type: {search_type} {query}")
        start_time = time.time()

        try:
            all_results = []

            # Optimized direct graph search
            if search_type in [SearchType.DIRECT, SearchType.BOTH]:
                print('Parsing query DIRECT...')
                parsed_query = self.llm.parse_query(query, self.graph_db.get_relationships())
                print(f"Parsed query: {parsed_query}")
                graph_results = self._optimized_graph_search(parsed_query, k)
                all_results.extend(graph_results)

            # Optimized semantic vector search  
            if search_type in [SearchType.SEMANTIC, SearchType.BOTH]:
                print('Parsing query SEMANTIC...')
                vector_results = self._optimized_semantic_search(query, k)
                all_results.extend(vector_results)

            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.score, reverse=True)
            final_results = unique_results[:k]

            # Generate answer using LLM
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

    def _optimized_graph_search(self, parsed_query, k: int) -> List[SearchResult]:
        """Direct graph search using optimized entity exploration"""
        results = []

        try:
            # Search by entities using optimized method
            for entity in parsed_query.entities:
                triplets = self.graph_db.get_entity_relationships_optimized(
                    entity=entity,
                    filter_obsolete=True,
                    max_depth=1,
                    limit=k
                )

                for triplet in triplets:
                    # Score based on relationship match (use safe accessor)
                    relationship = triplet.edge.get_relationship_safe()
                    score = 1.0 if parsed_query.relationships and relationship and relationship in parsed_query.relationships else 0.8
                    
                    result = SearchResult(
                        triplet=triplet,
                        score=score,
                        source="graph",
                        explanation=f"Optimized graph match for entity '{entity}'"
                    )
                    results.append(result)

            # Use path finding for multi-entity queries
            if len(parsed_query.entities) >= 2:
                for i, start_entity in enumerate(parsed_query.entities):
                    for end_entity in parsed_query.entities[i+1:]:
                        paths = self.graph_db.find_relationship_paths(
                            start_entity=start_entity,
                            end_entity=end_entity,
                            max_hops=3,
                            limit=5
                        )
                        
                        for path_info in paths:
                            # Create SearchResult from path
                            # This is simplified - in practice you'd convert path to triplets
                            score = path_info["path_confidence"]
                            # Add path results to results (implementation details omitted for brevity)

        except Exception as e:
            print(f"Error in optimized graph search: {e}")

        return results

    def _optimized_semantic_search(self, query: str, k: int) -> List[SearchResult]:
        """Semantic search using optimized vector operations with graph integration"""
        try:
            # Use the vector store's search method directly (it handles embedding internally)
            return self.vector_store.search(query, k=k, filter_obsolete=True)
        except Exception as e:
            print(f"Error in optimized semantic search: {e}")
            return []

    def get_node_relations(self, node_name: str, max_depth: int = 1, 
                          filter_obsolete: bool = True, source: Optional[str] = None) -> List[SearchResult]:
        """
        Get all relations for a node using optimized entity exploration
        
        Args:
            node_name: Name of the node to search relations for
            max_depth: Maximum relationship depth to explore
            filter_obsolete: Whether to filter out obsolete relationships
            source: Optional filter by source metadata
            
        Returns:
            List of SearchResult objects containing all relations
        """
        try:
            triplets = self.graph_db.get_entity_relationships_optimized(
                entity=node_name,
                filter_obsolete=filter_obsolete,
                max_depth=max_depth,
                limit=50
            )

            results = []
            for triplet in triplets:
                # Apply source filter if provided
                if source and hasattr(triplet.edge.metadata, 'source'):
                    if triplet.edge.metadata.source != source:
                        continue

                result = SearchResult(
                    triplet=triplet,
                    score=1.0,
                    source="graph",
                    explanation=f"Optimized relation for node '{node_name}'"
                )
                results.append(result)
            
            return results

        except Exception as e:
            print(f"Error getting node relations: {e}")
            return []

    def analyze_conflicts(self, entity_name: Optional[str] = None, 
                         relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze relationship conflicts using optimized detection"""
        try:
            return self.graph_db.detect_relationship_conflicts_optimized(
                entity_name=entity_name,
                relationship_type=relationship_type,
                confidence_threshold=0.5
            )
        except Exception as e:
            print(f"Error analyzing conflicts: {e}")
            return []

    def analyze_temporal_relationships(self, entity_name: str, 
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze temporal relationships using optimized queries"""
        try:
            return self.graph_db.analyze_entity_temporal_relationships(
                entity_name=entity_name,
                start_date=start_date,
                end_date=end_date,
                show_evolution=True
            )
        except Exception as e:
            print(f"Error analyzing temporal relationships: {e}")
            return []

    def find_paths(self, start_entity: str, end_entity: str, max_hops: int = 4) -> List[Dict[str, Any]]:
        """Find paths between entities using optimized algorithms"""
        try:
            return self.graph_db.find_relationship_paths(
                start_entity=start_entity,
                end_entity=end_entity,
                max_hops=max_hops,
                limit=10
            )
        except Exception as e:
            print(f"Error finding paths: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics including optimization stats"""
        try:
            return {
                "graph_stats": self.graph_db.get_stats(),
                "vector_stats": self.vector_store.get_stats(),
                "optimization_stats": self.graph_db.get_optimization_stats(),
                "relationships": self.graph_db.get_relationships(),
                "entities": len(self.graph_db.get_entities())
            }
        except Exception as e:
            return {"error": str(e)}

    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the entire knowledge graph"""
        return {
            "graph_data": self.graph_db.export_to_dict(),
            "vector_stats": self.vector_store.get_stats(),
            "optimization_stats": self.graph_db.get_optimization_stats(),
            "export_timestamp": datetime.now().isoformat(),
            "version": "2.0-optimized"
        }

    def clear_all_data(self) -> bool:
        """Clear all data from both graph and vector stores"""
        try:
            graph_cleared = self.graph_db.clear_graph()
            vector_cleared = self.vector_store.clear_collection()
            return graph_cleared and vector_cleared
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False

    # Helper methods
    def _add_error(self, results: Dict[str, Any], error_msg: str, description: str):
        """Add error to results"""
        results["errors"].append(error_msg)
        results["edge_results"].append({
            "action": "error",
            "message": error_msg,
            "input_description": description
        })

    def _update_counters(self, results: Dict[str, Any], edge_result: Dict[str, Any]):
        """Update result counters based on edge result"""
        action = edge_result.get("action", "unknown")
        if action == "created":
            results["new_edges"] += 1
        elif action == "updated":
            results["updated_edges"] += 1
        elif action == "obsoleted":
            results["obsoleted_edges"] += edge_result.get("count", 1)
        elif action == "duplicate":
            results["duplicates_ignored"] += 1
        elif action == "error":
            # Only append the error message if it's not already in the errors list
            error_msg = edge_result.get("message", "Unknown error")
            if error_msg not in results["errors"]:
                results["errors"].append(error_msg)

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results keeping highest scoring"""
        if not results:
            return []
        
        unique_results = []
        seen_relationships = []
        
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        
        for result in sorted_results:
            edge = result.triplet.edge
            # Use safe accessors to handle edges that might not have graph data populated
            subject = edge.get_subject_safe() or "unknown"
            relationship = edge.get_relationship_safe() or "unknown"
            obj = edge.get_object_safe() or "unknown"
            
            relationship_key = (
                subject.lower().strip(),
                relationship.upper(),
                obj.lower().strip()
            )
            
            if relationship_key not in seen_relationships:
                seen_relationships.append(relationship_key)
                unique_results.append(result)
        
        return unique_results

    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Calculate overall confidence in results"""
        if not results:
            return 0.0

        weights = [0.5, 0.3, 0.2]
        total_score = 0.0

        for i, result in enumerate(results[:3]):
            weight = weights[i] if i < len(weights) else 0.1
            total_score += result.score * weight

        return min(total_score, 1.0)
    
    def get_classifier_stats(self) -> Dict[str, Any]:
        """Get statistics about the classifier system."""
        stats = self.classifier_map.get_stats()
        stats["classifier_map"] = dict(self.classifier_map.classifier_map)
        return stats
    
    def refresh_classifier_map(self) -> None:
        """Refresh the classifier map from Neo4j (useful after manual data changes)."""
        self.classifier_map.refresh()
        # Update the LLM interface's classifier detector
        if self.llm.classifier_detector:
            self.llm.classifier_detector.classifier_map = self.classifier_map
    
    def get_edges_by_category(self, category: str) -> List[str]:
        """Get all edge types for a given category."""
        return self.classifier_map.get_edges_by_classifier(category)
    
    def get_all_categories(self) -> List[str]:
        """Get all available classifier categories."""
        return self.classifier_map.get_all_categories()