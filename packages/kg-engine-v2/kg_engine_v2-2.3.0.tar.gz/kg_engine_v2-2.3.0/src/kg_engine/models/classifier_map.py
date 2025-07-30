"""
ClassifierMap - Manages edge classifier categories from Neo4j metadata
"""
from typing import Dict, List, Optional, Set
import logging
from ..storage.graph_db import GraphDB

logger = logging.getLogger(__name__)


class ClassifierMap:
    """
    Manages classifier categories for edge standardization.
    
    Builds and maintains a map of categories to edge types based on 
    the 'category' field in edge metadata stored in Neo4j.
    
    Structure: Dict[category, List[edge_types]]
    Example: {"location": ["LIVES_IN", "STAY_IN"], "business": ["WORKS_AT", "HIRING"]}
    """
    
    def __init__(self, graph_db: GraphDB):
        self.graph_db = graph_db
        self.classifier_map: Dict[str, List[str]] = {}
        self._load_from_neo4j()
    
    def _load_from_neo4j(self) -> None:
        """
        Load classifier map from existing edge metadata in Neo4j.
        Builds map from relationships that have category field populated.
        """
        try:
            query = """
            MATCH ()-[r]->() 
            WHERE r.category IS NOT NULL AND r.category <> ''
            RETURN DISTINCT type(r) as edge_type, r.category as category
            ORDER BY category, edge_type
            """
            
            with self.graph_db.driver.session(database=self.graph_db.config.database) as session:
                results = session.run(query)
                
                # Build classifier map
                for record in results:
                    edge_type = record.get("edge_type")
                    category = record.get("category")
                    
                    if edge_type and category:
                        if category not in self.classifier_map:
                            self.classifier_map[category] = []
                        
                        if edge_type not in self.classifier_map[category]:
                            self.classifier_map[category].append(edge_type)
            
            logger.info(f"Loaded classifier map with {len(self.classifier_map)} categories")
            logger.debug(f"Classifier map: {self.classifier_map}")
            
        except Exception as e:
            logger.error(f"Failed to load classifier map from Neo4j: {e}")
            self.classifier_map = {}
    
    def get_edges_by_classifier(self, category: str) -> List[str]:
        """
        Get all edge types for a given category.
        
        Args:
            category: The classifier category (e.g., 'location', 'business')
            
        Returns:
            List of edge type names for the category
        """
        return self.classifier_map.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available category names."""
        return list(self.classifier_map.keys())
    
    def get_category_for_edge(self, edge_type: str) -> Optional[str]:
        """
        Find which category an edge type belongs to.
        
        Args:
            edge_type: The relationship type (e.g., 'LIVES_IN')
            
        Returns:
            Category name if found, None otherwise
        """
        for category, edges in self.classifier_map.items():
            if edge_type in edges:
                return category
        return None
    
    def has_category(self, category: str) -> bool:
        """Check if a category exists in the map."""
        return category in self.classifier_map
    
    def has_edge_in_category(self, category: str, edge_type: str) -> bool:
        """Check if an edge type exists in a specific category."""
        return edge_type in self.classifier_map.get(category, [])
    
    def get_or_create_edge(self, category: str, edge_name: str) -> str:
        """
        Add edge to category, creating category if needed.
        This updates the in-memory map but doesn't persist to Neo4j.
        The category will be persisted when the edge is actually created in Neo4j.
        
        Args:
            category: The classifier category
            edge_name: The edge type name
            
        Returns:
            The edge name (for consistency)
        """
        # Normalize edge name to uppercase convention
        edge_name = edge_name.upper()
        
        # Create category if it doesn't exist
        if category not in self.classifier_map:
            self.classifier_map[category] = []
            logger.debug(f"Created new category: {category}")
        
        # Add edge if not already present
        if edge_name not in self.classifier_map[category]:
            self.classifier_map[category].append(edge_name)
            logger.debug(f"Added edge '{edge_name}' to category '{category}'")
        
        return edge_name
    
    def find_similar_edges(self, category: str, target_edge: str) -> List[str]:
        """
        Find edges in a category that might be similar to the target edge.
        Uses simple string similarity for now.
        
        Args:
            category: The category to search in
            target_edge: The edge to find similar matches for
            
        Returns:
            List of similar edge names, sorted by similarity
        """
        if category not in self.classifier_map:
            return []
        
        edges = self.classifier_map[category]
        target_lower = target_edge.lower()
        
        # Simple similarity scoring
        similarities = []
        for edge in edges:
            edge_lower = edge.lower()
            
            # Exact match
            if edge_lower == target_lower:
                similarities.append((edge, 1.0))
            # Substring match
            elif target_lower in edge_lower or edge_lower in target_lower:
                similarities.append((edge, 0.8))
            # Common words
            else:
                target_words = set(target_lower.split('_'))
                edge_words = set(edge_lower.split('_'))
                common = len(target_words & edge_words)
                total = len(target_words | edge_words)
                if common > 0:
                    score = common / total
                    if score >= 0.3:  # Minimum threshold
                        similarities.append((edge, score))
        
        # Sort by similarity score (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [edge for edge, _ in similarities]
    
    def get_best_edge_for_category(self, category: str, proposed_edge: str, 
                                   similarity_threshold: float = 0.7) -> Optional[str]:
        """
        Find the best existing edge in a category for a proposed edge name.
        
        Args:
            category: The category to search in
            proposed_edge: The proposed edge name
            similarity_threshold: Minimum similarity to consider a match
            
        Returns:
            Best matching edge name if found, None otherwise
        """
        similar_edges = self.find_similar_edges(category, proposed_edge)
        
        if similar_edges:
            # For now, use simple scoring. Could be enhanced with ML similarity
            target_lower = proposed_edge.lower()
            best_edge = similar_edges[0]
            best_edge_lower = best_edge.lower()
            
            # Calculate simple similarity score
            if best_edge_lower == target_lower:
                return best_edge
            elif target_lower in best_edge_lower or best_edge_lower in target_lower:
                return best_edge
            
        return None
    
    def refresh(self) -> None:
        """Reload classifier map from Neo4j."""
        self._load_from_neo4j()
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the classifier map."""
        total_edges = sum(len(edges) for edges in self.classifier_map.values())
        return {
            "total_categories": len(self.classifier_map),
            "total_edges": total_edges,
            "average_edges_per_category": total_edges / len(self.classifier_map) if self.classifier_map else 0
        }
    
    def __str__(self) -> str:
        """String representation of the classifier map."""
        lines = [f"ClassifierMap ({len(self.classifier_map)} categories):"]
        for category, edges in self.classifier_map.items():
            lines.append(f"  {category}: {edges}")
        return "\n".join(lines)