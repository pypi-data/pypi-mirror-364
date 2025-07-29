"""Graph-native query optimization for Neo4j knowledge graphs."""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..config import Neo4jConfig
from ..models import GraphTriplet, SearchResult

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of graph queries."""
    ENTITY_EXPLORATION = "entity_exploration"
    RELATIONSHIP_DISCOVERY = "relationship_discovery"
    PATH_FINDING = "path_finding"
    PATTERN_MATCHING = "pattern_matching"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    CONFLICT_DETECTION = "conflict_detection"


@dataclass
class OptimizedQuery:
    """Optimized Cypher query with metadata."""
    cypher: str
    parameters: Dict[str, Any]
    description: str
    estimated_complexity: str
    indexes_used: List[str]


class GraphQueryOptimizer:
    """Optimizer for graph-native queries in Neo4j."""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize graph query optimizer.
        
        Args:
            config: Neo4j configuration
        """
        self.config = config or Neo4jConfig()
        self.query_cache: Dict[str, OptimizedQuery] = {}
    
    def optimize_entity_exploration(
        self,
        entity_name: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None,
        include_obsolete: bool = False
    ) -> OptimizedQuery:
        """Create optimized query for exploring entity relationships.
        
        Args:
            entity_name: Name of the entity to explore
            max_depth: Maximum relationship depth to explore
            relationship_types: Specific relationship types to include
            include_obsolete: Whether to include obsolete relationships
            
        Returns:
            Optimized Cypher query
        """
        cache_key = f"entity_exploration_{entity_name}_{max_depth}_{relationship_types}_{include_obsolete}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Build relationship type filter
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_filter = f":{rel_types}"
        
        # Build obsolete filter
        obsolete_filter = "WHERE r.obsolete = false" if not include_obsolete else ""
        
        if max_depth == 1:
            # Single-hop optimization
            cypher = f"""
            MATCH (start:Entity {{name: $entity_name}})
            MATCH (start)-[r{rel_filter}]-(connected:Entity)
            {obsolete_filter}
            RETURN start, r, connected, 
                   r.confidence as confidence,
                   r.relationship as relationship_type
            ORDER BY r.confidence DESC
            LIMIT $limit
            """
            complexity = "O(degree)"
        else:
            # Multi-hop with path optimization
            cypher = f"""
            MATCH (start:Entity {{name: $entity_name}})
            MATCH path = (start)-[*1..{max_depth}]-(connected:Entity)
            WHERE ALL(r IN relationships(path) WHERE {'' if include_obsolete else 'r.obsolete = false AND'} 
                      {'true' if not relationship_types else f'type(r) IN {relationship_types}'})
            WITH start, connected, path, 
                 reduce(conf = 1.0, r IN relationships(path) | conf * r.confidence) as path_confidence
            RETURN start, connected, path, path_confidence,
                   length(path) as path_length
            ORDER BY path_confidence DESC, path_length ASC
            LIMIT $limit
            """
            complexity = f"O(degree^{max_depth})"
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters={"entity_name": entity_name, "limit": 50},
            description=f"Explore {entity_name} relationships up to depth {max_depth}",
            estimated_complexity=complexity,
            indexes_used=["entity_name_idx", "relates_to_obsolete_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def optimize_relationship_discovery(
        self,
        subject_pattern: str,
        object_pattern: str,
        relationship_hint: Optional[str] = None,
        confidence_threshold: float = 0.7
    ) -> OptimizedQuery:
        """Create optimized query for discovering relationships between entities.
        
        Args:
            subject_pattern: Pattern to match subject entities
            object_pattern: Pattern to match object entities
            relationship_hint: Hint for relationship type
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            Optimized Cypher query
        """
        cache_key = f"rel_discovery_{subject_pattern}_{object_pattern}_{relationship_hint}_{confidence_threshold}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Build relationship filter
        rel_filter = ""
        if relationship_hint:
            rel_filter = f"AND t.relationship CONTAINS $relationship_hint"
        
        cypher = f"""
        // Find relationships matching patterns
        MATCH (t:Triplet)
        WHERE t.subject CONTAINS $subject_pattern
          AND t.object CONTAINS $object_pattern
          AND t.confidence >= $confidence_threshold
          AND t.obsolete = false
          {rel_filter}
        
        // Get entity nodes for richer context
        MATCH (subject:Entity {{name: t.subject}})
        MATCH (object:Entity {{name: t.object}})
        
        RETURN t, subject, object,
               t.confidence as confidence,
               t.relationship as relationship_type,
               t.summary as summary
        ORDER BY t.confidence DESC
        LIMIT $limit
        """
        
        parameters = {
            "subject_pattern": subject_pattern,
            "object_pattern": object_pattern,
            "confidence_threshold": confidence_threshold,
            "limit": 25
        }
        
        if relationship_hint:
            parameters["relationship_hint"] = relationship_hint
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters=parameters,
            description=f"Discover relationships between '{subject_pattern}' and '{object_pattern}'",
            estimated_complexity="O(log n)",
            indexes_used=["triplet_subject_idx", "triplet_object_idx", "triplet_confidence_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def optimize_path_finding(
        self,
        start_entity: str,
        end_entity: str,
        max_hops: int = 4,
        avoid_obsolete: bool = True
    ) -> OptimizedQuery:
        """Create optimized query for finding paths between entities.
        
        Args:
            start_entity: Starting entity name
            end_entity: Target entity name
            max_hops: Maximum number of hops
            avoid_obsolete: Whether to avoid obsolete relationships
            
        Returns:
            Optimized Cypher query
        """
        cache_key = f"path_finding_{start_entity}_{end_entity}_{max_hops}_{avoid_obsolete}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        obsolete_condition = "r.obsolete = false AND" if avoid_obsolete else ""
        
        cypher = f"""
        // Find shortest paths between entities
        MATCH (start:Entity {{name: $start_entity}})
        MATCH (end:Entity {{name: $end_entity}})
        
        // Use shortestPath for optimal performance
        MATCH path = shortestPath((start)-[*1..{max_hops}]-(end))
        WHERE ALL(r IN relationships(path) WHERE {obsolete_condition} r.confidence >= 0.5)
        
        WITH path, 
             reduce(conf = 1.0, r IN relationships(path) | conf * r.confidence) as path_confidence,
             [r IN relationships(path) | r.relationship] as relationship_chain
        
        RETURN path, path_confidence, relationship_chain,
               length(path) as path_length,
               nodes(path) as entities_in_path
        ORDER BY path_length ASC, path_confidence DESC
        LIMIT $limit
        """
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters={
                "start_entity": start_entity,
                "end_entity": end_entity,
                "limit": 10
            },
            description=f"Find paths from '{start_entity}' to '{end_entity}'",
            estimated_complexity=f"O(degree^{max_hops})",
            indexes_used=["entity_name_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def optimize_pattern_matching(
        self,
        pattern_description: str,
        entity_types: Optional[Dict[str, str]] = None
    ) -> OptimizedQuery:
        """Create optimized query for complex pattern matching.
        
        Args:
            pattern_description: Natural language description of pattern
            entity_types: Entity type constraints
            
        Returns:
            Optimized Cypher query
        """
        # This is a simplified pattern matcher - in practice, you'd use NLP
        # to parse the pattern description into graph patterns
        
        cache_key = f"pattern_matching_{pattern_description}_{entity_types}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Example patterns based on common queries
        if "works for" in pattern_description.lower():
            cypher = """
            MATCH (person:Entity)-[r:RELATES_TO {relationship: 'works_for'}]->(company:Entity)
            WHERE r.obsolete = false
            RETURN person, company, r,
                   r.confidence as confidence
            ORDER BY r.confidence DESC
            LIMIT $limit
            """
            description = "Find employment relationships"
        
        elif "connected to" in pattern_description.lower():
            cypher = """
            MATCH (a:Entity)-[r1:RELATES_TO]-(intermediate:Entity)-[r2:RELATES_TO]-(b:Entity)
            WHERE r1.obsolete = false AND r2.obsolete = false
              AND id(a) < id(b)  // Avoid duplicate paths
            RETURN a, intermediate, b, 
                   [r1.relationship, r2.relationship] as connection_path,
                   (r1.confidence * r2.confidence) as path_confidence
            ORDER BY path_confidence DESC
            LIMIT $limit
            """
            description = "Find entities connected through intermediates"
        
        else:
            # Generic pattern - search triplets by description
            cypher = """
            MATCH (t:Triplet)
            WHERE t.summary CONTAINS $pattern_description
              AND t.obsolete = false
            MATCH (subject:Entity {name: t.subject})
            MATCH (object:Entity {name: t.object})
            RETURN t, subject, object,
                   t.confidence as confidence
            ORDER BY t.confidence DESC
            LIMIT $limit
            """
            description = f"Pattern match: {pattern_description}"
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters={"pattern_description": pattern_description, "limit": 20},
            description=description,
            estimated_complexity="O(n log n)",
            indexes_used=["triplet_obsolete_idx", "triplet_confidence_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def optimize_temporal_analysis(
        self,
        entity_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        show_evolution: bool = True
    ) -> OptimizedQuery:
        """Create optimized query for temporal relationship analysis.
        
        Args:
            entity_name: Entity to analyze
            start_date: Start date for analysis (ISO format)
            end_date: End date for analysis (ISO format)
            show_evolution: Whether to show relationship evolution
            
        Returns:
            Optimized Cypher query
        """
        cache_key = f"temporal_analysis_{entity_name}_{start_date}_{end_date}_{show_evolution}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        date_filter = ""
        if start_date:
            date_filter += "AND (t.from_date IS NULL OR t.from_date >= datetime($start_date))"
        if end_date:
            date_filter += "AND (t.to_date IS NULL OR t.to_date <= datetime($end_date))"
        
        if show_evolution:
            cypher = f"""
            // Show relationship evolution over time
            MATCH (t:Triplet)
            WHERE (t.subject = $entity_name OR t.object = $entity_name)
              {date_filter}
            
            WITH t,
                 CASE 
                   WHEN t.obsolete = true THEN 'ended'
                   WHEN t.to_date IS NOT NULL AND t.to_date < datetime() THEN 'expired'
                   ELSE 'active'
                 END as status,
                 coalesce(t.from_date, t.created_at) as start_time
            
            RETURN t, status, start_time,
                   t.relationship as relationship_type,
                   CASE WHEN t.subject = $entity_name THEN t.object ELSE t.subject END as connected_entity
            ORDER BY start_time DESC
            LIMIT $limit
            """
        else:
            cypher = f"""
            // Show active relationships in time period
            MATCH (t:Triplet)
            WHERE (t.subject = $entity_name OR t.object = $entity_name)
              AND t.obsolete = false
              {date_filter}
            
            RETURN t,
                   t.relationship as relationship_type,
                   CASE WHEN t.subject = $entity_name THEN t.object ELSE t.subject END as connected_entity,
                   t.confidence as confidence
            ORDER BY t.confidence DESC
            LIMIT $limit
            """
        
        parameters = {"entity_name": entity_name, "limit": 30}
        if start_date:
            parameters["start_date"] = start_date
        if end_date:
            parameters["end_date"] = end_date
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters=parameters,
            description=f"Temporal analysis for {entity_name}",
            estimated_complexity="O(log n)",
            indexes_used=["triplet_subject_idx", "triplet_object_idx", "triplet_created_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def optimize_conflict_detection(
        self,
        entity_name: Optional[str] = None,
        relationship_type: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> OptimizedQuery:
        """Create optimized query for detecting relationship conflicts.
        
        Args:
            entity_name: Specific entity to check for conflicts
            relationship_type: Specific relationship type to check
            confidence_threshold: Minimum confidence for considering conflicts
            
        Returns:
            Optimized Cypher query
        """
        cache_key = f"conflict_detection_{entity_name}_{relationship_type}_{confidence_threshold}"
        
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        entity_filter = ""
        if entity_name:
            entity_filter = "AND (t1.subject = $entity_name OR t2.subject = $entity_name)"
        
        rel_filter = ""
        if relationship_type:
            rel_filter = "AND t1.relationship = $relationship_type AND t2.relationship = $relationship_type"
        
        cypher = f"""
        // Find conflicting relationships
        MATCH (t1:Triplet), (t2:Triplet)
        WHERE t1.subject = t2.subject
          AND t1.relationship = t2.relationship
          AND t1.object <> t2.object
          AND t1.obsolete = false
          AND t2.obsolete = false
          AND t1.confidence >= $confidence_threshold
          AND t2.confidence >= $confidence_threshold
          AND id(t1) < id(t2)  // Avoid duplicates
          {entity_filter}
          {rel_filter}
        
        WITH t1, t2,
             abs(t1.confidence - t2.confidence) as confidence_diff,
             CASE 
               WHEN t1.confidence > t2.confidence THEN t1
               ELSE t2
             END as higher_confidence,
             CASE 
               WHEN t1.confidence < t2.confidence THEN t1
               ELSE t2  
             END as lower_confidence
        
        RETURN t1, t2, confidence_diff, higher_confidence, lower_confidence,
               t1.subject as conflicted_entity,
               t1.relationship as conflicted_relationship,
               [t1.object, t2.object] as conflicting_objects
        ORDER BY confidence_diff ASC  // Show most similar confidence first
        LIMIT $limit
        """
        
        parameters = {"confidence_threshold": confidence_threshold, "limit": 15}
        if entity_name:
            parameters["entity_name"] = entity_name
        if relationship_type:
            parameters["relationship_type"] = relationship_type
        
        optimized_query = OptimizedQuery(
            cypher=cypher,
            parameters=parameters,
            description="Detect relationship conflicts",
            estimated_complexity="O(n²) - use with constraints",
            indexes_used=["triplet_subject_idx", "triplet_relationship_idx", "triplet_confidence_idx"]
        )
        
        self.query_cache[cache_key] = optimized_query
        return optimized_query
    
    def execute_optimized_query(
        self,
        optimized_query: OptimizedQuery,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute an optimized query and return results.
        
        Args:
            optimized_query: The optimized query to execute
            additional_params: Additional parameters to merge
            
        Returns:
            List of result records
        """
        driver = self.config.get_driver()
        
        # Merge parameters
        params = optimized_query.parameters.copy()
        if additional_params:
            params.update(additional_params)
        
        try:
            with driver.session(database=self.config.database) as session:
                result = session.run(optimized_query.cypher, params)
                
                records = []
                for record in result:
                    records.append(dict(record))
                
                logger.info(f"Executed optimized query: {optimized_query.description}")
                logger.info(f"Returned {len(records)} records")
                
                return records
                
        except Exception as e:
            logger.error(f"Failed to execute optimized query: {e}")
            logger.error(f"Query: {optimized_query.cypher}")
            logger.error(f"Parameters: {params}")
            raise
    
    def get_query_recommendations(
        self,
        query_type: QueryType,
        context: Dict[str, Any]
    ) -> List[str]:
        """Get recommendations for optimizing specific query types.
        
        Args:
            query_type: Type of query to optimize
            context: Context information for recommendations
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        if query_type == QueryType.ENTITY_EXPLORATION:
            recommendations.extend([
                "Use LIMIT to prevent large result sets",
                "Index on Entity.name for faster lookups",
                "Consider max_depth carefully - exponential growth",
                "Filter obsolete relationships for current view"
            ])
        
        elif query_type == QueryType.PATH_FINDING:
            recommendations.extend([
                "Use shortestPath() for single path queries",
                "Consider allShortestPaths() for multiple paths",
                "Set reasonable max_hops to avoid expensive traversals",
                "Index relationship properties used in WHERE clauses"
            ])
        
        elif query_type == QueryType.TEMPORAL_ANALYSIS:
            recommendations.extend([
                "Index on date properties (from_date, to_date, created_at)",
                "Use datetime() function for date comparisons",
                "Consider partitioning by time periods for large datasets",
                "Cache frequent temporal queries"
            ])
        
        elif query_type == QueryType.CONFLICT_DETECTION:
            recommendations.extend([
                "Limit scope with entity or relationship filters",
                "Use confidence thresholds to reduce false positives",
                "Index on subject, relationship, and confidence",
                "Consider running as batch job for large graphs"
            ])
        
        return recommendations
    
    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache.clear()
        logger.info("Query cache cleared")


def create_graph_query_optimizer(config: Optional[Neo4jConfig] = None) -> GraphQueryOptimizer:
    """Convenience function to create a graph query optimizer.
    
    Args:
        config: Neo4j configuration
        
    Returns:
        Configured GraphQueryOptimizer instance
    """
    return GraphQueryOptimizer(config)