"""
Neo4j graph database implementation for Knowledge Graph Engine v2
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid

from ..models import GraphEdge, GraphTriplet, SearchResult, RelationshipStatus, EdgeData, EdgeMetadata
from ..config import Neo4jConfig
from ..utils.neo4j_optimizer import Neo4jOptimizer
from ..utils.graph_query_optimizer import GraphQueryOptimizer, QueryType

logger = logging.getLogger(__name__)


class GraphDB:
    """Neo4j-based graph database for persistent graph storage"""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        self.config = config or Neo4jConfig()
        self.driver = self.config.get_driver()
        self.entity_aliases = {}  # Store entity name variations (could be moved to Neo4j)
        
        # Initialize optimizers
        self.neo4j_optimizer = Neo4jOptimizer(self.config)
        self.query_optimizer = GraphQueryOptimizer(self.config)
        
        # Query result cache
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes TTL
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Initialize performance indexes on first use
        self._indexes_created = False
    
    def _ensure_performance_indexes(self) -> bool:
        """Ensure performance indexes are created (called lazily)"""
        if self._indexes_created:
            return True
            
        try:
            logger.info("Creating performance indexes...")
            created = self.neo4j_optimizer.create_performance_indexes()
            if created:
                logger.info(f"Created {len(created)} performance indexes: {', '.join(created)}")
                self._indexes_created = True
                return True
            else:
                logger.warning("No indexes were created")
                return False
        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")
            return False
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Generate cache key for method and parameters"""
        import hashlib
        key_data = f"{method}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        age = (datetime.now() - self._cache_timestamps[cache_key]).total_seconds()
        return age < self._cache_ttl
    
    def _set_cache(self, cache_key: str, result: Any) -> None:
        """Store result in cache"""
        self._query_cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now()
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """Get result from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self._query_cache[cache_key]
        
        # Clean up expired cache entry
        if cache_key in self._query_cache:
            del self._query_cache[cache_key]
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]
        
        return None
    
    def vector_similarity_search_with_graph(
        self, 
        vector: List[float], 
        k: int = 10,
        index_name: str = "triplet_embedding_index",
        relationship_types: Optional[List[str]] = None,
        confidence_threshold: float = 0.3,
        filter_obsolete: bool = True
    ) -> List[SearchResult]:
        """
        Optimized vector similarity search integrated with graph structure.
        
        Args:
            vector: Query vector for similarity search
            k: Number of results to return
            index_name: Name of the vector index to use
            relationship_types: Filter by specific relationship types
            confidence_threshold: Minimum confidence threshold
            filter_obsolete: Whether to filter out obsolete relationships
            
        Returns:
            List of SearchResult objects with vector scores and graph data
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "vector_similarity_search_with_graph",
            vector_hash=hash(tuple(vector)),
            k=k,
            index_name=index_name,
            relationship_types=relationship_types,
            confidence_threshold=confidence_threshold,
            filter_obsolete=filter_obsolete
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build optimized query based on available optimization patterns
                if relationship_types:
                    # Use relationship filtering optimization
                    query = """
                    CALL db.index.vector.queryNodes($index_name, $k_expanded, $vector) 
                    YIELD node AS triplet, score
                    WHERE triplet.relationship IN $allowed_relationships
                      AND triplet.confidence >= $confidence_threshold
                      AND ($filter_obsolete = false OR triplet.obsolete = false)
                    WITH triplet, score
                    MATCH (subject:Entity {name: triplet.subject})
                    MATCH (object:Entity {name: triplet.object})
                    RETURN triplet, subject, object, score
                    ORDER BY score DESC
                    LIMIT $k
                    """
                    params = {
                        "index_name": index_name,
                        "k_expanded": k * 2,  # Expand search then filter
                        "k": k,
                        "vector": vector,
                        "allowed_relationships": relationship_types,
                        "confidence_threshold": confidence_threshold,
                        "filter_obsolete": filter_obsolete
                    }
                else:
                    # Standard vector similarity with graph integration
                    query = """
                    CALL db.index.vector.queryNodes($index_name, $k_expanded, $vector) 
                    YIELD node AS triplet, score
                    WHERE triplet.confidence >= $confidence_threshold
                      AND ($filter_obsolete = false OR triplet.obsolete = false)
                    WITH triplet, score
                    MATCH (subject:Entity {name: triplet.subject})
                    MATCH (object:Entity {name: triplet.object})
                    RETURN triplet, subject, object, score
                    ORDER BY score DESC
                    LIMIT $k
                    """
                    params = {
                        "index_name": index_name,
                        "k_expanded": k * 2,
                        "k": k,
                        "vector": vector,
                        "confidence_threshold": confidence_threshold,
                        "filter_obsolete": filter_obsolete
                    }
                
                result = session.run(query, params)
                search_results = []
                
                for record in result:
                    # Create GraphEdge from triplet node properties
                    triplet_node = record["triplet"]
                    score = record["score"]
                    
                    # Convert triplet node to GraphEdge
                    edge = self._triplet_node_to_edge(triplet_node)
                    triplet = GraphTriplet(edge=edge, vector_id=triplet_node.get("vector_id"))
                    
                    search_result = SearchResult(
                        triplet=triplet,
                        score=float(score),
                        source="vector_graph",
                        explanation=f"Vector similarity with graph integration (score: {score:.3f})"
                    )
                    search_results.append(search_result)
                
                # Cache the results
                self._set_cache(cache_key, search_results)
                
                logger.info(f"Vector similarity search returned {len(search_results)} results")
                return search_results
                
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            # Fallback to basic search without vector index
            return self._fallback_similarity_search(vector, k, confidence_threshold, filter_obsolete)
    
    def _triplet_node_to_edge(self, triplet_node) -> GraphEdge:
        """Convert a Triplet node from Neo4j to GraphEdge"""
        node_props = dict(triplet_node)
        
        # Parse dates
        created_at = node_props.get("created_at")
        if created_at and hasattr(created_at, 'to_native'):
            created_at = created_at.to_native()
        elif isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()
        
        from_date = node_props.get("from_date")
        if from_date and hasattr(from_date, 'to_native'):
            from_date = from_date.to_native()
        elif isinstance(from_date, str):
            from_date = datetime.fromisoformat(from_date)
        
        to_date = node_props.get("to_date")
        if to_date and hasattr(to_date, 'to_native'):
            to_date = to_date.to_native()
        elif isinstance(to_date, str):
            to_date = datetime.fromisoformat(to_date)
        
        metadata = EdgeMetadata(
            summary=node_props.get("summary", ""),
            created_at=created_at,
            from_date=from_date,
            to_date=to_date,
            obsolete=node_props.get("obsolete", False),
            status=RelationshipStatus(node_props.get("status", "active")),
            confidence=node_props.get("confidence", 1.0),
            source=node_props.get("source", ""),
            user_id=node_props.get("user_id", "")
        )
        
        # Create edge with graph data
        edge = GraphEdge.create_for_storage(
            edge_id=node_props.get("edge_id", str(uuid.uuid4())),
            metadata=metadata
        )
        
        edge.set_graph_data(
            subject=node_props.get("subject", ""),
            relationship=node_props.get("relationship", ""),
            object=node_props.get("object", "")
        )
        
        return edge
    
    def _fallback_similarity_search(
        self,
        vector: List[float],
        k: int,
        confidence_threshold: float,
        filter_obsolete: bool
    ) -> List[SearchResult]:
        """Fallback search when vector index is not available"""
        logger.warning("Using fallback similarity search - vector index not available")
        
        # Simple text-based fallback (this would be replaced with actual embedding similarity)
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get all active triplets and do basic filtering
                obsolete_filter = "AND t.obsolete = false" if filter_obsolete else ""
                
                result = session.run(
                    f"""
                    MATCH (t:Triplet)
                    WHERE t.confidence >= $confidence_threshold
                      {obsolete_filter}
                    RETURN t
                    ORDER BY t.confidence DESC
                    LIMIT $k
                    """,
                    confidence_threshold=confidence_threshold,
                    k=k
                )
                
                search_results = []
                for record in result:
                    edge = self._triplet_node_to_edge(record["t"])
                    triplet = GraphTriplet(edge=edge)
                    
                    search_result = SearchResult(
                        triplet=triplet,
                        score=edge.metadata.confidence,  # Use confidence as fallback score
                        source="fallback",
                        explanation="Fallback search by confidence"
                    )
                    search_results.append(search_result)
                
                return search_results
                
        except Exception as e:
            logger.error(f"Error in fallback similarity search: {e}")
            return []
        
    def add_edge_data(self, edge_data: EdgeData) -> bool:
        """Add an edge to the graph using EdgeData"""
        try:
            # Validate edge data
            if not edge_data.subject or not edge_data.relationship or not edge_data.object:
                logger.error(f"Edge data missing required fields")
                return False
                
            edge_id = edge_data.edge_id or str(uuid.uuid4())
                
            with self.driver.session(database=self.config.database) as session:
                # Create or merge entities
                session.run(
                    """
                    MERGE (subject:Entity {name: $subject_name})
                    ON CREATE SET subject.type = 'Unknown', subject.created_at = datetime()
                    
                    MERGE (object:Entity {name: $object_name})
                    ON CREATE SET object.type = 'Unknown', object.created_at = datetime()
                    """,
                    subject_name=edge_data.subject,
                    object_name=edge_data.object
                )
                
                # Create the edge with dynamic relationship type
                # Use APOC or dynamic query construction
                query = f"""
                    MATCH (subject:Entity {{name: $subject_name}})
                    MATCH (object:Entity {{name: $object_name}})
                    CREATE (subject)-[r:`{edge_data.relationship}` {{
                        edge_id: $edge_id,
                        summary: $summary,
                        obsolete: $obsolete,
                        status: $status,
                        confidence: $confidence,
                        created_at: datetime($created_at),
                        from_date: CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END,
                        to_date: CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END,
                        source: $source,
                        user_id: $user_id
                    }}]->(object)
                    RETURN r
                """
                
                result = session.run(
                    query,
                    subject_name=edge_data.subject,
                    object_name=edge_data.object,
                    edge_id=edge_id,
                    summary=edge_data.metadata.summary,
                    obsolete=edge_data.metadata.obsolete,
                    status=edge_data.metadata.status.value,
                    confidence=edge_data.metadata.confidence,
                    created_at=edge_data.metadata.created_at.isoformat() if edge_data.metadata.created_at else datetime.now().isoformat(),
                    from_date=edge_data.metadata.from_date.isoformat() if edge_data.metadata.from_date else None,
                    to_date=edge_data.metadata.to_date.isoformat() if edge_data.metadata.to_date else None,
                    source=edge_data.metadata.source or "",
                    user_id=edge_data.metadata.user_id or ""
                )
                
                if result.single():
                    logger.info(f"Added edge: {edge_data.subject} -{edge_data.relationship}-> {edge_data.object}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error adding edge to graph: {e}")
            return False
    
    def add_edge(self, edge: GraphEdge) -> bool:
        """Legacy method - requires edge to have populated graph data"""
        try:
            # Create EdgeData from GraphEdge
            edge_data = EdgeData(
                subject=edge.subject,
                relationship=edge.relationship,
                object=edge.object,
                metadata=edge.metadata,
                edge_id=edge.edge_id
            )
            return self.add_edge_data(edge_data)
        except ValueError as e:
            logger.error(f"Edge missing required graph data: {e}")
            return False
    
    def update_edge_metadata(self, edge_id: str, metadata: EdgeMetadata) -> bool:
        """Update metadata for an existing edge (relationship type agnostic)"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Find edge by ID regardless of relationship type
                result = session.run(
                    """
                    MATCH ()-[r {edge_id: $edge_id}]->()
                    SET r.summary = $summary,
                        r.obsolete = $obsolete,
                        r.status = $status,
                        r.confidence = $confidence,
                        r.created_at = datetime($created_at),
                        r.from_date = CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END,
                        r.to_date = CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END,
                        r.source = $source,
                        r.user_id = $user_id
                    RETURN r
                    """,
                    edge_id=edge_id,
                    summary=metadata.summary,
                    obsolete=metadata.obsolete,
                    status=metadata.status.value,
                    confidence=metadata.confidence,
                    created_at=metadata.created_at.isoformat() if metadata.created_at else datetime.now().isoformat(),
                    from_date=metadata.from_date.isoformat() if metadata.from_date else None,
                    to_date=metadata.to_date.isoformat() if metadata.to_date else None,
                    source=metadata.source or "",
                    user_id=metadata.user_id or ""
                )
                
                if result.single():
                    logger.info(f"Updated edge metadata: {edge_id}")
                    return True
                else:
                    logger.warning(f"Edge not found: {edge_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating edge: {e}")
            return False
    
    def update_edge(self, edge: GraphEdge) -> bool:
        """Update an existing edge - only updates metadata"""
        return self.update_edge_metadata(edge.edge_id, edge.metadata)
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph (relationship type agnostic)"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH ()-[r {edge_id: $edge_id}]->()
                    DELETE r
                    RETURN count(r) as deleted_count
                    """,
                    edge_id=edge_id
                )
                
                deleted_count = result.single()["deleted_count"]
                if deleted_count > 0:
                    logger.info(f"Deleted edge: {edge_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            return False
    
    def find_edges(self, subject: str = None, relationship: str = None, 
                   obj: str = None, filter_obsolete: bool = True) -> List[GraphTriplet]:
        """Find edges matching the given criteria"""
        results = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build the query dynamically based on provided criteria
                where_clauses = []
                params = {}
                
                if subject:
                    where_clauses.append("s.name = $subject")
                    params["subject"] = subject
                    
                if obj:
                    where_clauses.append("o.name = $object")
                    params["object"] = obj
                    
                if filter_obsolete:
                    where_clauses.append("r.obsolete = false")
                
                # If relationship is specified, match specific type
                if relationship:
                    query_parts = [f"MATCH (s:Entity)-[r:`{relationship}`]->(o:Entity)"]
                else:
                    # Match any relationship type
                    query_parts = ["MATCH (s:Entity)-[r]->(o:Entity)"]
                
                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))
                
                query_parts.append("RETURN s, r, o, type(r) as rel_type")
                query = "\n".join(query_parts)
                
                result = session.run(query, params)
                
                for record in result:
                    edge = self._record_to_edge_v2(record["s"], record["r"], record["o"], record["rel_type"])
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                
                return results
                
        except Exception as e:
            logger.error(f"Error finding edges: {e}")
            return []
    
    def find_conflicting_edges(self, edge_data: EdgeData) -> List[GraphEdge]:
        """Find edges that would conflict with the new edge"""
        conflicts = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Look for edges with same subject and relationship type but different object
                query = f"""
                    MATCH (s:Entity {{name: $subject}})
                          -[r:`{edge_data.relationship}`]->
                          (o:Entity)
                    WHERE o.name <> $object AND r.obsolete = false
                    RETURN s, r, o, type(r) as rel_type
                """
                
                result = session.run(
                    query,
                    subject=edge_data.subject,
                    object=edge_data.object
                )
                
                for record in result:
                    edge = self._record_to_edge_v2(record["s"], record["r"], record["o"], record["rel_type"])
                    conflicts.append(edge)
                
                return conflicts
                
        except Exception as e:
            logger.error(f"Error finding conflicts: {e}")
            return []
    
    def detect_relationship_conflicts_optimized(
        self,
        entity_name: Optional[str] = None,
        relationship_type: Optional[str] = None,
        confidence_threshold: float = 0.5,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Advanced conflict detection using optimized queries.
        
        Args:
            entity_name: Specific entity to check for conflicts
            relationship_type: Specific relationship type to check
            confidence_threshold: Minimum confidence for considering conflicts
            limit: Maximum number of conflicts to return
            
        Returns:
            List of conflict information dictionaries
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "detect_relationship_conflicts_optimized",
            entity_name=entity_name,
            relationship_type=relationship_type,
            confidence_threshold=confidence_threshold,
            limit=limit
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Custom optimized query for relationship-based storage
            with self.driver.session(database=self.config.database) as session:
                # Build dynamic query based on parameters
                entity_filter = ""
                params = {"confidence_threshold": confidence_threshold, "limit": limit}
                
                if entity_name:
                    entity_filter = "AND (startNode(r1).name = $entity_name OR endNode(r1).name = $entity_name)"
                    params["entity_name"] = entity_name
                
                if relationship_type:
                    rel_type_filter = f":{relationship_type}"
                else:
                    rel_type_filter = ""
                
                # Query to find conflicting relationships
                query = f"""
                    MATCH (subject:Entity)
                    MATCH (subject)-[r1{rel_type_filter}]->(obj1:Entity)
                    MATCH (subject)-[r2{rel_type_filter}]->(obj2:Entity)
                    WHERE r1.obsolete = false
                      AND r2.obsolete = false
                      AND r1.confidence >= $confidence_threshold
                      AND r2.confidence >= $confidence_threshold
                      AND obj1 <> obj2
                      AND elementId(r1) < elementId(r2)
                      {entity_filter}
                    RETURN subject.name as conflicted_entity,
                           type(r1) as conflicted_relationship,
                           [obj1.name, obj2.name] as conflicting_objects,
                           abs(r1.confidence - r2.confidence) as confidence_diff,
                           r1, r2, obj1, obj2
                    ORDER BY confidence_diff ASC
                    LIMIT $limit
                """
                
                result = session.run(query, params)
                
                conflicts = []
                for record in result:
                    # Get the subject entity node
                    subject_entity = {"name": record["conflicted_entity"]}
                    
                    # Create edge objects for the conflicting relationships
                    edge1 = self._record_to_edge_v2(
                        subject_entity, record["r1"], record["obj1"], record["conflicted_relationship"]
                    )
                    edge2 = self._record_to_edge_v2(
                        subject_entity, record["r2"], record["obj2"], record["conflicted_relationship"]  
                    )
                    
                    conflict_info = {
                        "conflicted_entity": record["conflicted_entity"],
                        "conflicted_relationship": record["conflicted_relationship"],
                        "conflicting_objects": record["conflicting_objects"],
                        "confidence_diff": record["confidence_diff"],
                        "higher_confidence_edge": edge1 if record["r1"]["confidence"] > record["r2"]["confidence"] else edge2,
                        "lower_confidence_edge": edge1 if record["r1"]["confidence"] <= record["r2"]["confidence"] else edge2
                    }
                    conflicts.append(conflict_info)
                
                # Cache the results
                self._set_cache(cache_key, conflicts)
                
                logger.info(f"Detected {len(conflicts)} relationship conflicts")
                return conflicts
            
        except Exception as e:
            logger.error(f"Error in optimized conflict detection: {e}")
            return []
    
    def analyze_entity_temporal_relationships(
        self,
        entity_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        show_evolution: bool = True,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Advanced temporal analysis of entity relationships.
        
        Args:
            entity_name: Entity to analyze
            start_date: Start date for analysis (ISO format)
            end_date: End date for analysis (ISO format)
            show_evolution: Whether to show relationship evolution
            limit: Maximum number of results
            
        Returns:
            List of temporal relationship information
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "analyze_entity_temporal_relationships",
            entity_name=entity_name,
            start_date=start_date,
            end_date=end_date,
            show_evolution=show_evolution,
            limit=limit
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Custom optimized query for relationship-based storage
            with self.driver.session(database=self.config.database) as session:
                # Build date filters
                date_filters = []
                params = {"entity_name": entity_name, "limit": limit}
                
                if start_date:
                    date_filters.append("(r.from_date IS NULL OR r.from_date >= datetime($start_date))")
                    params["start_date"] = start_date
                
                if end_date:
                    date_filters.append("(r.to_date IS NULL OR r.to_date <= datetime($end_date))")
                    params["end_date"] = end_date
                
                date_filter = ""
                if date_filters:
                    date_filter = "AND " + " AND ".join(date_filters)
                
                if show_evolution:
                    # Show relationship evolution over time
                    query = f"""
                        MATCH (entity:Entity {{name: $entity_name}})
                        MATCH (entity)-[r]-(connected:Entity)
                        WHERE 1=1 {date_filter}
                        WITH r, connected,
                             CASE 
                               WHEN r.obsolete = true THEN 'ended'
                               WHEN r.to_date IS NOT NULL AND r.to_date < datetime() THEN 'expired'
                               ELSE 'active'
                             END as status,
                             coalesce(r.from_date, r.created_at) as start_time
                        RETURN r, connected,
                               status,
                               start_time,
                               type(r) as relationship_type,
                               connected.name as connected_entity
                        ORDER BY start_time DESC
                        LIMIT $limit
                    """
                else:
                    # Show active relationships in time period
                    query = f"""
                        MATCH (entity:Entity {{name: $entity_name}})
                        MATCH (entity)-[r]-(connected:Entity)
                        WHERE r.obsolete = false
                          {date_filter}
                        RETURN r, connected,
                               type(r) as relationship_type,
                               connected.name as connected_entity,
                               r.confidence as confidence
                        ORDER BY r.confidence DESC
                        LIMIT $limit
                    """
                
                result = session.run(query, params)
                
                temporal_data = []
                for record in result:
                    # Create entity node objects
                    entity_node = {"name": entity_name}
                    connected_node = record["connected"]
                    relationship = record["r"]
                    
                    # Create edge object (direction determined by relationship in query)
                    edge = self._record_to_edge_v2(
                        entity_node, relationship, connected_node, record["relationship_type"]
                    )
                    
                    temporal_info = {
                        "entity": entity_name,
                        "connected_entity": record["connected_entity"],
                        "relationship_type": record["relationship_type"],
                        "edge": edge
                    }
                    
                    if show_evolution:
                        temporal_info.update({
                            "status": record["status"],
                            "start_time": record["start_time"]
                        })
                    else:
                        temporal_info.update({
                            "confidence": record["confidence"]
                        })
                    
                    temporal_data.append(temporal_info)
                
                # Cache the results
                self._set_cache(cache_key, temporal_data)
                
                logger.info(f"Temporal analysis returned {len(temporal_data)} results for {entity_name}")
                return temporal_data
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return []
    
    def find_relationship_paths(
        self,
        start_entity: str,
        end_entity: str,
        max_hops: int = 4,
        avoid_obsolete: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find relationship paths between two entities using optimized algorithms.
        
        Args:
            start_entity: Starting entity name
            end_entity: Target entity name
            max_hops: Maximum number of hops
            avoid_obsolete: Whether to avoid obsolete relationships
            limit: Maximum number of paths to return
            
        Returns:
            List of path information dictionaries
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "find_relationship_paths",
            start_entity=start_entity,
            end_entity=end_entity,
            max_hops=max_hops,
            avoid_obsolete=avoid_obsolete,
            limit=limit
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Use optimized path finding query
            optimized_query = self.query_optimizer.optimize_path_finding(
                start_entity=start_entity,
                end_entity=end_entity,
                max_hops=max_hops,
                avoid_obsolete=avoid_obsolete
            )
            
            # Execute the optimized query
            records = self.query_optimizer.execute_optimized_query(
                optimized_query,
                additional_params={"limit": limit}
            )
            
            paths_data = []
            for record in records:
                path_info = {
                    "start_entity": start_entity,
                    "end_entity": end_entity,
                    "path_length": record["path_length"],
                    "path_confidence": record["path_confidence"],
                    "relationship_chain": record["relationship_chain"],
                    "entities_in_path": [node["name"] for node in record["entities_in_path"]],
                    "path": record["path"]
                }
                paths_data.append(path_info)
            
            # Cache the results
            self._set_cache(cache_key, paths_data)
            
            logger.info(f"Found {len(paths_data)} paths from {start_entity} to {end_entity}")
            return paths_data
            
        except Exception as e:
            logger.error(f"Error in path finding: {e}")
            return []
    
    def discover_relationship_patterns(
        self,
        pattern_description: str,
        entity_types: Optional[Dict[str, str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Discover complex relationship patterns using optimized pattern matching.
        
        Args:
            pattern_description: Natural language description of pattern
            entity_types: Entity type constraints
            limit: Maximum number of results
            
        Returns:
            List of pattern match information
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "discover_relationship_patterns",
            pattern_description=pattern_description,
            entity_types=entity_types,
            limit=limit
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Use optimized pattern matching query
            optimized_query = self.query_optimizer.optimize_pattern_matching(
                pattern_description=pattern_description,
                entity_types=entity_types
            )
            
            # Execute the optimized query
            records = self.query_optimizer.execute_optimized_query(
                optimized_query,
                additional_params={"limit": limit}
            )
            
            patterns_data = []
            for record in records:
                if "t" in record:
                    # Single triplet pattern
                    pattern_info = {
                        "pattern_type": "single_triplet",
                        "triplet": self._triplet_node_to_edge(record["t"]),
                        "subject": record.get("subject"),
                        "object": record.get("object"),
                        "confidence": record["confidence"]
                    }
                else:
                    # Multi-entity pattern
                    pattern_info = {
                        "pattern_type": "multi_entity",
                        "entities": [record.get("a"), record.get("intermediate"), record.get("b")],
                        "connection_path": record.get("connection_path", []),
                        "path_confidence": record.get("path_confidence", 0.0)
                    }
                
                patterns_data.append(pattern_info)
            
            # Cache the results
            self._set_cache(cache_key, patterns_data)
            
            logger.info(f"Discovered {len(patterns_data)} patterns for '{pattern_description}'")
            return patterns_data
            
        except Exception as e:
            logger.error(f"Error in pattern discovery: {e}")
            return []
    
    def find_duplicate_edges(self, edge_data: EdgeData) -> List[GraphEdge]:
        """Find exact duplicate edges"""
        duplicates = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                query = f"""
                    MATCH (s:Entity {{name: $subject}})
                          -[r:`{edge_data.relationship}`]->
                          (o:Entity {{name: $object}})
                    WHERE r.obsolete = false
                    RETURN s, r, o, type(r) as rel_type
                """
                
                result = session.run(
                    query,
                    subject=edge_data.subject,
                    object=edge_data.object
                )
                
                for record in result:
                    edge = self._record_to_edge_v2(record["s"], record["r"], record["o"], record["rel_type"])
                    duplicates.append(edge)
                
                return duplicates
                
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    def get_entity_relationships_optimized(
        self, 
        entity: str, 
        filter_obsolete: bool = True,
        max_depth: int = 1,
        relationship_types: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[GraphTriplet]:
        """
        Optimized entity relationship exploration with depth control and caching.
        
        Args:
            entity: Entity name to explore
            filter_obsolete: Whether to filter obsolete relationships
            max_depth: Maximum relationship depth (1 for direct, 2+ for multi-hop)
            relationship_types: Specific relationship types to include
            limit: Maximum number of results
            
        Returns:
            List of GraphTriplet objects
        """
        # Ensure indexes are created
        self._ensure_performance_indexes()
        
        # Check cache
        cache_key = self._get_cache_key(
            "get_entity_relationships_optimized",
            entity=entity,
            filter_obsolete=filter_obsolete,
            max_depth=max_depth,
            relationship_types=relationship_types,
            limit=limit
        )
        
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Use optimized query from GraphQueryOptimizer
            optimized_query = self.query_optimizer.optimize_entity_exploration(
                entity_name=entity,
                max_depth=max_depth,
                relationship_types=relationship_types,
                include_obsolete=not filter_obsolete
            )
            
            # Execute the optimized query
            records = self.query_optimizer.execute_optimized_query(
                optimized_query,
                additional_params={"limit": limit}
            )
            
            results = []
            for record in records:
                if max_depth == 1:
                    # Single-hop results
                    edge = self._record_to_edge_v2(
                        record["start"], 
                        record["r"], 
                        record["connected"],
                        record.get("relationship_type", "RELATES_TO")
                    )
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                else:
                    # Multi-hop results - create path representation
                    path = record["path"]
                    nodes = path.nodes
                    relationships = path.relationships
                    
                    # Create triplet for each relationship in path
                    for i, rel in enumerate(relationships):
                        if i < len(nodes) - 1:
                            subject_node = nodes[i]
                            object_node = nodes[i + 1]
                            edge = self._record_to_edge_v2(
                                subject_node,
                                rel,
                                object_node,
                                rel.type
                            )
                            triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                            results.append(triplet)
            
            # Cache the results
            self._set_cache(cache_key, results)
            
            logger.info(f"Optimized entity exploration returned {len(results)} results for {entity}")
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized entity relationships: {e}")
            # Fallback to original method
            return self.get_entity_relationships(entity, filter_obsolete)
    
    def get_entity_relationships(self, entity: str, filter_obsolete: bool = True) -> List[GraphTriplet]:
        """Get all relationships for an entity"""
        results = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Find edges where entity is subject or object (any relationship type)
                obsolete_filter = "AND r.obsolete = false" if filter_obsolete else ""
                
                result = session.run(
                    f"""
                    MATCH (e:Entity {{name: $entity}})
                    MATCH (e)-[r]-(other:Entity)
                    WHERE 1=1 {obsolete_filter}
                    RETURN e, r, other, type(r) as rel_type,
                           CASE WHEN startNode(r) = e THEN 'subject' ELSE 'object' END as role
                    """,
                    entity=entity
                )
                
                for record in result:
                    # Reconstruct edge with correct direction
                    if record["role"] == "subject":
                        edge = self._record_to_edge_v2(record["e"], record["r"], record["other"], record["rel_type"])
                    else:
                        edge = self._record_to_edge_v2(record["other"], record["r"], record["e"], record["rel_type"])
                    
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting entity relationships: {e}")
            return []
    
    def get_entities(self) -> List[str]:
        """Get all entities in the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run("MATCH (e:Entity) RETURN e.name as name")
                return [record["name"] for record in result]
                
        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []
    
    def get_relationships(self) -> List[str]:
        """Get all relationship types in the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get all relationship types using CALL db.relationshipTypes()
                result = session.run(
                    """
                    CALL db.relationshipTypes() YIELD relationshipType
                    RETURN relationshipType
                    """
                )
                return [record["relationshipType"] for record in result]
                
        except Exception as e:
            logger.error(f"Error getting relationships: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get entity count
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                
                # Get edge counts (all relationship types)
                edge_stats = session.run(
                    """
                    MATCH ()-[r]->()
                    WHERE r.edge_id IS NOT NULL
                    RETURN count(r) as total,
                           sum(CASE WHEN r.obsolete = false OR r.obsolete IS NULL THEN 1 ELSE 0 END) as active,
                           sum(CASE WHEN r.obsolete = true THEN 1 ELSE 0 END) as obsolete
                    """
                ).single()
                
                # Get relationship types
                relationships = self.get_relationships()
                
                return {
                    "total_entities": entity_count,
                    "total_edges": edge_stats["total"] or 0,
                    "active_edges": edge_stats["active"] or 0,
                    "obsolete_edges": edge_stats["obsolete"] or 0,
                    "relationship_types": len(relationships),
                    "relationships": relationships[:20]  # Show first 20
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def normalize_entity_name(self, name: str) -> str:
        """Normalize entity names for consistent matching"""
        if not name:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = name.lower().strip()
        
        # Check for aliases
        if normalized in self.entity_aliases:
            return self.entity_aliases[normalized]
        
        return normalized
    
    def add_entity_alias(self, alias: str, canonical_name: str):
        """Add an alias for an entity"""
        self.entity_aliases[alias.lower().strip()] = canonical_name.lower().strip()
        
        # TODO: Consider storing aliases in Neo4j for persistence
        # Could create an ALIAS_OF relationship between entities
    
    def clear_graph(self) -> bool:
        """Clear all data from the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Delete all relationships and nodes
                session.run("MATCH (n) DETACH DELETE n")
                self.entity_aliases.clear()
                logger.info("Cleared all graph data")
                return True
                
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export graph data to dictionary for serialization"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Export edges (all relationship types)
                edges_result = session.run(
                    """
                    MATCH (s:Entity)-[r]->(o:Entity)
                    WHERE r.edge_id IS NOT NULL
                    RETURN s, r, o, type(r) as rel_type
                    """
                )
                
                edges = []
                for record in edges_result:
                    edge = self._record_to_edge_v2(record["s"], record["r"], record["o"], record["rel_type"])
                    edge_dict = edge.to_dict()
                    # Include relationship type in export
                    edge_dict['relationship_type'] = record["rel_type"]
                    edges.append(edge_dict)
                
                return {
                    "edges": edges,
                    "aliases": self.entity_aliases,
                    "stats": self.get_stats()
                }
                
        except Exception as e:
            logger.error(f"Error exporting graph: {e}")
            return {"error": str(e)}
    
    def import_from_dict(self, data: Dict[str, Any]) -> bool:
        """Import graph data from dictionary"""
        try:
            # Clear existing data
            self.clear_graph()
            
            # Import aliases
            if "aliases" in data:
                self.entity_aliases = data["aliases"]
            
            # Import edges
            if "edges" in data:
                
                for edge_dict in data["edges"]:
                    # Reconstruct metadata
                    metadata_data = edge_dict["metadata"]
                    
                    metadata = EdgeMetadata(
                        summary=metadata_data["summary"],
                        created_at=datetime.fromisoformat(metadata_data["created_at"]),
                        from_date=datetime.fromisoformat(metadata_data["from_date"]) if metadata_data.get("from_date") else None,
                        to_date=datetime.fromisoformat(metadata_data["to_date"]) if metadata_data.get("to_date") else None,
                        obsolete=metadata_data.get("obsolete", False),
                        result=metadata_data.get("result"),
                        status=RelationshipStatus(metadata_data.get("status", "active")),
                        confidence=metadata_data.get("confidence", 1.0),
                        source=metadata_data.get("source"),
                        user_id=metadata_data.get("user_id")
                    )
                    
                    # Use EdgeData for import with relationship type
                    rel_type = edge_dict.get("relationship_type") or edge_dict.get("relationship", "RELATES_TO")
                    edge_data = EdgeData(
                        subject=edge_dict["subject"],
                        relationship=rel_type,
                        object=edge_dict["object"],
                        metadata=metadata,
                        edge_id=edge_dict["edge_id"]
                    )
                    
                    self.add_edge_data(edge_data)
            
            logger.info(f"Imported {len(data.get('edges', []))} edges")
            return True
            
        except Exception as e:
            logger.error(f"Error importing graph data: {e}")
            return False
    
    def _record_to_edge_v2(self, subject_node, relationship, object_node, rel_type: str) -> GraphEdge:
        """Convert Neo4j record to GraphEdge with dynamic relationship type"""
        # Extract relationship properties
        rel_props = dict(relationship)
        
        # Parse dates
        created_at = rel_props.get("created_at")
        if created_at and hasattr(created_at, 'to_native'):
            created_at = created_at.to_native()
        elif isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()
            
        from_date = rel_props.get("from_date")
        if from_date and hasattr(from_date, 'to_native'):
            from_date = from_date.to_native()
        elif isinstance(from_date, str):
            from_date = datetime.fromisoformat(from_date)
            
        to_date = rel_props.get("to_date")
        if to_date and hasattr(to_date, 'to_native'):
            to_date = to_date.to_native()
        elif isinstance(to_date, str):
            to_date = datetime.fromisoformat(to_date)
        
        metadata = EdgeMetadata(
            summary=rel_props.get("summary", ""),
            created_at=created_at,
            from_date=from_date,
            to_date=to_date,
            obsolete=rel_props.get("obsolete", False),
            status=RelationshipStatus(rel_props.get("status", "active")),
            confidence=rel_props.get("confidence", 1.0),
            source=rel_props.get("source", ""),
            user_id=rel_props.get("user_id", "")
        )
        
        # Create edge with minimal data
        edge = GraphEdge.create_for_storage(
            edge_id=rel_props.get("edge_id", str(uuid.uuid4())),
            metadata=metadata
        )
        
        # Set graph data from Neo4j
        edge.set_graph_data(
            subject=subject_node["name"],
            relationship=rel_type,  # Use the actual relationship type from Neo4j
            object=object_node["name"]
        )
        
        return edge
    
    def _record_to_edge(self, subject_node, relationship, object_node) -> GraphEdge:
        """Legacy method - for backward compatibility"""
        # For old RELATES_TO edges, get relationship from property
        rel_type = dict(relationship).get("relationship", "RELATES_TO")
        return self._record_to_edge_v2(subject_node, relationship, object_node, rel_type)
    
    def get_edge_by_id(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by its ID"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH (s:Entity)-[r {edge_id: $edge_id}]->(o:Entity)
                    RETURN s, r, o, type(r) as rel_type
                    """,
                    edge_id=edge_id
                )
                
                record = result.single()
                if record:
                    return self._record_to_edge_v2(
                        record["s"], record["r"], record["o"], record["rel_type"]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting edge by ID: {e}")
            return None
    
    def migrate_relates_to_edges(self) -> Dict[str, int]:
        """Migrate old RELATES_TO edges to use dynamic relationship types"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Count edges to migrate
                count_result = session.run(
                    """
                    MATCH ()-[r:RELATES_TO]->()
                    WHERE r.relationship IS NOT NULL
                    RETURN count(r) as count
                    """
                ).single()
                
                total_count = count_result["count"]
                if total_count == 0:
                    logger.info("No RELATES_TO edges to migrate")
                    return {"migrated": 0, "errors": 0}
                
                logger.info(f"Starting migration of {total_count} RELATES_TO edges")
                
                # Get all RELATES_TO edges
                result = session.run(
                    """
                    MATCH (s:Entity)-[old:RELATES_TO]->(o:Entity)
                    WHERE old.relationship IS NOT NULL
                    RETURN s, old, o, old.relationship as rel_type
                    """
                )
                
                migrated = 0
                errors = 0
                
                for record in result:
                    try:
                        rel_type = record["rel_type"]
                        old_rel = record["old"]
                        
                        # Create new edge with dynamic type
                        edge_data = EdgeData(
                            subject=record["s"]["name"],
                            relationship=rel_type,
                            object=record["o"]["name"],
                            metadata=EdgeMetadata(
                                summary=old_rel.get("summary", ""),
                                created_at=old_rel.get("created_at"),
                                from_date=old_rel.get("from_date"),
                                to_date=old_rel.get("to_date"),
                                obsolete=old_rel.get("obsolete", False),
                                status=RelationshipStatus(old_rel.get("status", "active")),
                                confidence=old_rel.get("confidence", 1.0),
                                source=old_rel.get("source", ""),
                                user_id=old_rel.get("user_id", "")
                            ),
                            edge_id=old_rel.get("edge_id")
                        )
                        
                        # Add new edge
                        if self.add_edge_data(edge_data):
                            # Delete old edge
                            session.run(
                                """
                                MATCH ()-[r:RELATES_TO {edge_id: $edge_id}]->()
                                DELETE r
                                """,
                                edge_id=old_rel.get("edge_id")
                            )
                            migrated += 1
                        else:
                            errors += 1
                            
                    except Exception as e:
                        logger.error(f"Error migrating edge: {e}")
                        errors += 1
                
                logger.info(f"Migration complete: {migrated} migrated, {errors} errors")
                return {"migrated": migrated, "errors": errors}
                
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return {"migrated": 0, "errors": -1}
    
    def clear_query_cache(self) -> None:
        """Clear the query result cache"""
        self._query_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = datetime.now()
        valid_entries = sum(1 for key in self._cache_timestamps.keys() 
                           if self._is_cache_valid(key))
        
        return {
            "total_entries": len(self._query_cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._query_cache) - valid_entries,
            "cache_ttl_seconds": self._cache_ttl,
            "indexes_created": self._indexes_created
        }
    
    def force_create_indexes(self) -> bool:
        """Force creation of performance indexes"""
        self._indexes_created = False
        return self._ensure_performance_indexes()
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        try:
            # Get database statistics
            db_stats = self.neo4j_optimizer.get_database_statistics()
            
            # Get cache statistics
            cache_stats = self.get_cache_stats()
            
            # Get query recommendations
            recommendations = {
                "entity_exploration": self.query_optimizer.get_query_recommendations(
                    QueryType.ENTITY_EXPLORATION, {}
                ),
                "path_finding": self.query_optimizer.get_query_recommendations(
                    QueryType.PATH_FINDING, {}
                ),
                "temporal_analysis": self.query_optimizer.get_query_recommendations(
                    QueryType.TEMPORAL_ANALYSIS, {}
                ),
                "conflict_detection": self.query_optimizer.get_query_recommendations(
                    QueryType.CONFLICT_DETECTION, {}
                )
            }
            
            return {
                "database_stats": db_stats,
                "cache_stats": cache_stats,
                "optimization_recommendations": recommendations,
                "available_optimized_methods": [
                    "vector_similarity_search_with_graph",
                    "get_entity_relationships_optimized", 
                    "detect_relationship_conflicts_optimized",
                    "analyze_entity_temporal_relationships",
                    "find_relationship_paths",
                    "discover_relationship_patterns"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization stats: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Clean up Neo4j driver connection"""
        if hasattr(self, 'driver'):
            self.driver.close()