"""Neo4j optimization utilities for vector indexes and graph queries."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..config import Neo4jConfig

logger = logging.getLogger(__name__)


class SimilarityFunction(Enum):
    """Supported similarity functions for vector indexes."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


@dataclass
class VectorIndexConfig:
    """Configuration for Neo4j vector indexes."""
    index_name: str
    node_label: str
    property_name: str
    dimensions: int
    similarity_function: SimilarityFunction
    
    def to_cypher_options(self) -> Dict[str, Any]:
        """Convert to Cypher index options."""
        return {
            "indexConfig": {
                "vector.dimensions": self.dimensions,
                "vector.similarity_function": self.similarity_function.value
            }
        }


class Neo4jOptimizer:
    """Optimizer for Neo4j vector indexes and queries."""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize Neo4j optimizer.
        
        Args:
            config: Neo4j configuration
        """
        self.config = config or Neo4jConfig()
    
    def analyze_vector_index_performance(self, index_name: str) -> Dict[str, Any]:
        """Analyze vector index performance and suggest optimizations.
        
        Args:
            index_name: Name of the vector index to analyze
            
        Returns:
            Analysis results and optimization suggestions
        """
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            # Get index information
            index_info = session.run(
                "SHOW INDEXES YIELD name, type, state, populationPercent, options "
                "WHERE name = $index_name",
                index_name=index_name
            ).single()
            
            if not index_info:
                return {"error": f"Index {index_name} not found"}
            
            # Get index statistics
            stats_result = session.run(
                "CALL db.index.fulltext.queryNodes($index_name, '*') "
                "YIELD node RETURN count(node) as total_nodes",
                index_name=index_name
            )
            
            try:
                total_nodes = stats_result.single()["total_nodes"]
            except:
                # Fallback for vector indexes
                total_nodes = None
            
            # Analyze index configuration
            options = index_info.get("options", {})
            index_config = options.get("indexConfig", {})
            
            analysis = {
                "index_name": index_name,
                "type": index_info["type"],
                "state": index_info["state"],
                "population_percent": index_info["populationPercent"],
                "total_nodes": total_nodes,
                "current_config": {
                    "dimensions": index_config.get("vector.dimensions"),
                    "similarity_function": index_config.get("vector.similarity_function")
                },
                "suggestions": []
            }
            
            # Generate optimization suggestions
            if index_info["state"] != "ONLINE":
                analysis["suggestions"].append({
                    "type": "availability",
                    "message": f"Index is {index_info['state']}. Wait for completion or rebuild.",
                    "priority": "high"
                })
            
            if index_info["populationPercent"] < 100:
                analysis["suggestions"].append({
                    "type": "population",
                    "message": f"Index population is {index_info['populationPercent']}%. Allow time to complete.",
                    "priority": "medium"
                })
            
            # Memory and performance suggestions
            dimensions = index_config.get("vector.dimensions", 384)
            if dimensions > 1024:
                analysis["suggestions"].append({
                    "type": "memory",
                    "message": f"High dimensionality ({dimensions}) may impact performance. Consider dimensionality reduction.",
                    "priority": "medium"
                })
            
            return analysis
    
    def optimize_vector_index_config(
        self,
        current_config: VectorIndexConfig,
        data_size: int,
        query_patterns: List[str]
    ) -> VectorIndexConfig:
        """Suggest optimized vector index configuration.
        
        Args:
            current_config: Current index configuration
            data_size: Estimated number of vectors
            query_patterns: Common query patterns
            
        Returns:
            Optimized configuration
        """
        optimized_config = VectorIndexConfig(
            index_name=current_config.index_name,
            node_label=current_config.node_label,
            property_name=current_config.property_name,
            dimensions=current_config.dimensions,
            similarity_function=current_config.similarity_function
        )
        
        # Optimize similarity function based on use case
        if any("semantic" in pattern.lower() for pattern in query_patterns):
            # Cosine is generally better for semantic similarity
            optimized_config.similarity_function = SimilarityFunction.COSINE
        elif any("euclidean" in pattern.lower() for pattern in query_patterns):
            optimized_config.similarity_function = SimilarityFunction.EUCLIDEAN
        
        # Dimension optimization suggestions
        if data_size > 100000 and current_config.dimensions > 512:
            logger.info(f"Large dataset ({data_size} vectors) with high dimensions ({current_config.dimensions}). "
                       f"Consider reducing dimensions for better performance.")
        
        return optimized_config
    
    def create_optimized_vector_index(
        self,
        config: VectorIndexConfig,
        drop_existing: bool = False
    ) -> bool:
        """Create or recreate vector index with optimized configuration.
        
        Args:
            config: Vector index configuration
            drop_existing: Whether to drop existing index first
            
        Returns:
            True if successful
        """
        driver = self.config.get_driver()
        
        try:
            with driver.session(database=self.config.database) as session:
                # Drop existing index if requested
                if drop_existing:
                    try:
                        session.run(f"DROP INDEX {config.index_name} IF EXISTS")
                        logger.info(f"Dropped existing index {config.index_name}")
                    except Exception as e:
                        logger.warning(f"Failed to drop existing index: {e}")
                
                # Create new index with optimized configuration
                cypher_query = f"""
                CREATE VECTOR INDEX {config.index_name} IF NOT EXISTS
                FOR (n:{config.node_label}) ON (n.{config.property_name})
                OPTIONS {{
                  indexConfig: {{
                    `vector.dimensions`: {config.dimensions},
                    `vector.similarity_function`: '{config.similarity_function.value}'
                  }}
                }}
                """
                
                session.run(cypher_query)
                logger.info(f"Created optimized vector index {config.index_name}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to create optimized vector index: {e}")
            return False
    
    def optimize_graph_queries(self) -> Dict[str, List[str]]:
        """Generate optimized Cypher queries for common operations.
        
        Returns:
            Dictionary of optimized queries by operation type
        """
        return {
            "entity_relationships": [
                # Optimized entity relationship query with index hints
                """
                MATCH (e:Entity {name: $entity_name})
                CALL {
                  WITH e
                  MATCH (e)-[r:RELATES_TO]-(other:Entity)
                  WHERE r.obsolete = false
                  RETURN r, other
                  ORDER BY r.confidence DESC
                  LIMIT $limit
                }
                RETURN r, other
                """,
                
                # Alternative with Triplet nodes
                """
                MATCH (t:Triplet)
                WHERE (t.subject = $entity_name OR t.object = $entity_name)
                  AND t.obsolete = false
                RETURN t
                ORDER BY t.confidence DESC
                LIMIT $limit
                """
            ],
            
            "vector_similarity_with_graph": [
                # Hybrid vector + graph query
                """
                CALL db.index.vector.queryNodes($index_name, $k, $vector) 
                YIELD node AS triplet, score
                MATCH (subject:Entity {name: triplet.subject})
                MATCH (object:Entity {name: triplet.object})
                WHERE triplet.obsolete = false
                RETURN triplet, subject, object, score
                ORDER BY score DESC
                """,
                
                # Vector search with relationship filtering
                """
                CALL db.index.vector.queryNodes($index_name, $k * 2, $vector) 
                YIELD node AS triplet, score
                WHERE triplet.relationship IN $allowed_relationships
                  AND triplet.obsolete = false
                RETURN triplet, score
                ORDER BY score DESC
                LIMIT $k
                """
            ],
            
            "temporal_queries": [
                # Active relationships at specific time
                """
                MATCH (t:Triplet)
                WHERE t.obsolete = false
                  AND (t.from_date IS NULL OR t.from_date <= $query_date)
                  AND (t.to_date IS NULL OR t.to_date >= $query_date)
                  AND (t.subject = $entity OR t.object = $entity)
                RETURN t
                ORDER BY t.confidence DESC
                """,
                
                # Relationship history
                """
                MATCH (t:Triplet)
                WHERE (t.subject = $entity OR t.object = $entity)
                  AND t.relationship = $relationship_type
                RETURN t, 
                       CASE WHEN t.obsolete THEN 'obsolete' ELSE 'active' END as status
                ORDER BY coalesce(t.from_date, t.created_at) DESC
                """
            ],
            
            "conflict_detection": [
                # Find conflicting relationships
                """
                MATCH (t1:Triplet), (t2:Triplet)
                WHERE t1.subject = t2.subject
                  AND t1.relationship = t2.relationship
                  AND t1.object <> t2.object
                  AND t1.obsolete = false
                  AND t2.obsolete = false
                  AND id(t1) < id(t2)
                RETURN t1, t2, 
                       abs(t1.confidence - t2.confidence) as confidence_diff
                ORDER BY confidence_diff ASC
                """
            ]
        }
    
    def create_performance_indexes(self) -> List[str]:
        """Create additional indexes for better query performance.
        
        Returns:
            List of created index names
        """
        driver = self.config.get_driver()
        created_indexes = []
        
        # Index definitions for common query patterns
        indexes_to_create = [
            ("triplet_subject_idx", "CREATE INDEX triplet_subject_idx IF NOT EXISTS FOR (t:Triplet) ON (t.subject)"),
            ("triplet_object_idx", "CREATE INDEX triplet_object_idx IF NOT EXISTS FOR (t:Triplet) ON (t.object)"),
            ("triplet_relationship_idx", "CREATE INDEX triplet_relationship_idx IF NOT EXISTS FOR (t:Triplet) ON (t.relationship)"),
            ("triplet_obsolete_idx", "CREATE INDEX triplet_obsolete_idx IF NOT EXISTS FOR (t:Triplet) ON (t.obsolete)"),
            ("triplet_confidence_idx", "CREATE INDEX triplet_confidence_idx IF NOT EXISTS FOR (t:Triplet) ON (t.confidence)"),
            ("triplet_created_idx", "CREATE INDEX triplet_created_idx IF NOT EXISTS FOR (t:Triplet) ON (t.created_at)"),
            ("entity_name_idx", "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name)"),
            ("relates_to_obsolete_idx", "CREATE INDEX relates_to_obsolete_idx IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.obsolete)"),
        ]
        
        try:
            with driver.session(database=self.config.database) as session:
                for index_name, query in indexes_to_create:
                    try:
                        session.run(query)
                        created_indexes.append(index_name)
                        logger.info(f"Created index: {index_name}")
                    except Exception as e:
                        logger.warning(f"Failed to create index {index_name}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")
        
        return created_indexes
    
    def analyze_query_performance(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations.
        
        Args:
            query: Cypher query to analyze
            params: Query parameters
            
        Returns:
            Performance analysis results
        """
        driver = self.config.get_driver()
        
        try:
            with driver.session(database=self.config.database) as session:
                # Run query with profiling
                explain_query = f"EXPLAIN {query}"
                profile_query = f"PROFILE {query}"
                
                # Get execution plan
                explain_result = session.run(explain_query, params or {})
                explain_summary = explain_result.consume()
                
                # Get performance profile
                profile_result = session.run(profile_query, params or {})
                profile_summary = profile_result.consume()
                
                analysis = {
                    "query": query,
                    "execution_plan": {
                        "available": True,
                        "operators": []
                    },
                    "performance": {
                        "db_hits": profile_summary.counters.properties_set if hasattr(profile_summary, 'counters') else None,
                        "total_time": profile_summary.result_consumed_after if hasattr(profile_summary, 'result_consumed_after') else None,
                    },
                    "suggestions": []
                }
                
                # Analyze common performance issues
                query_lower = query.lower()
                
                if "match" in query_lower and "where" in query_lower:
                    if "index" not in query_lower:
                        analysis["suggestions"].append({
                            "type": "indexing",
                            "message": "Consider adding indexes for WHERE clause properties",
                            "priority": "medium"
                        })
                
                if query_lower.count("match") > 3:
                    analysis["suggestions"].append({
                        "type": "complexity",
                        "message": "Complex query with multiple MATCH clauses. Consider breaking into smaller queries.",
                        "priority": "medium"
                    })
                
                if "order by" in query_lower and "limit" not in query_lower:
                    analysis["suggestions"].append({
                        "type": "performance",
                        "message": "ORDER BY without LIMIT may be inefficient for large results",
                        "priority": "low"
                    })
                
                return analysis
                
        except Exception as e:
            logger.error(f"Failed to analyze query performance: {e}")
            return {
                "query": query,
                "error": str(e),
                "suggestions": [{
                    "type": "error",
                    "message": f"Query analysis failed: {e}",
                    "priority": "high"
                }]
            }
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics for optimization planning.
        
        Returns:
            Database statistics and metrics
        """
        driver = self.config.get_driver()
        
        try:
            with driver.session(database=self.config.database) as session:
                # Node counts
                node_stats = {}
                node_result = session.run("""
                    MATCH (n) 
                    RETURN labels(n) as labels, count(n) as count
                """)
                
                for record in node_result:
                    labels = record["labels"]
                    count = record["count"]
                    label_key = ":".join(sorted(labels)) if labels else "unlabeled"
                    node_stats[label_key] = count
                
                # Relationship counts
                rel_stats = {}
                rel_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                """)
                
                for record in rel_result:
                    rel_stats[record["type"]] = record["count"]
                
                # Index information
                index_result = session.run("SHOW INDEXES")
                indexes = []
                for record in index_result:
                    indexes.append({
                        "name": record["name"],
                        "type": record["type"], 
                        "state": record["state"],
                        "population_percent": record["populationPercent"]
                    })
                
                # Constraint information
                constraint_result = session.run("SHOW CONSTRAINTS")
                constraints = []
                for record in constraint_result:
                    constraints.append({
                        "name": record["name"],
                        "type": record["type"],
                        "description": record["description"]
                    })
                
                return {
                    "nodes": {
                        "total": sum(node_stats.values()),
                        "by_label": node_stats
                    },
                    "relationships": {
                        "total": sum(rel_stats.values()),
                        "by_type": rel_stats
                    },
                    "indexes": indexes,
                    "constraints": constraints,
                    "timestamp": session.run("RETURN datetime() as now").single()["now"]
                }
                
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {"error": str(e)}


def optimize_neo4j_setup(config: Optional[Neo4jConfig] = None) -> Dict[str, Any]:
    """Convenience function to set up optimized Neo4j configuration.
    
    Args:
        config: Neo4j configuration
        
    Returns:
        Optimization results
    """
    optimizer = Neo4jOptimizer(config)
    
    results = {
        "performance_indexes": [],
        "vector_index_analysis": {},
        "database_stats": {},
        "optimized_queries": {}
    }
    
    try:
        # Create performance indexes
        results["performance_indexes"] = optimizer.create_performance_indexes()
        
        # Analyze existing vector index
        try:
            results["vector_index_analysis"] = optimizer.analyze_vector_index_performance("triplet_embedding_index")
        except Exception as e:
            results["vector_index_analysis"] = {"error": str(e)}
        
        # Get database statistics
        results["database_stats"] = optimizer.get_database_statistics()
        
        # Get optimized queries
        results["optimized_queries"] = optimizer.optimize_graph_queries()
        
    except Exception as e:
        results["error"] = str(e)
    
    return results