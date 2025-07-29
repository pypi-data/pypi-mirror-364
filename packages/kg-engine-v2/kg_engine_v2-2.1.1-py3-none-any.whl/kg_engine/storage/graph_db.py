"""
Neo4j graph database implementation for Knowledge Graph Engine v2
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid

from ..models import GraphEdge, GraphTriplet, SearchResult, RelationshipStatus
from ..config import Neo4jConfig

logger = logging.getLogger(__name__)


class GraphDB:
    """Neo4j-based graph database for persistent graph storage"""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        self.config = config or Neo4jConfig()
        self.driver = self.config.get_driver()
        self.entity_aliases = {}  # Store entity name variations (could be moved to Neo4j)
        
    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge to the graph"""
        try:
            # Validate edge data
            if not self._validate_edge(edge):
                logger.error(f"Edge validation failed: {edge}")
                return False
            with self.driver.session(database=self.config.database) as session:
                # Create or merge entities
                session.run(
                    """
                    MERGE (subject:Entity {name: $subject_name})
                    ON CREATE SET subject.type = 'Unknown', subject.created_at = datetime()
                    
                    MERGE (object:Entity {name: $object_name})
                    ON CREATE SET object.type = 'Unknown', object.created_at = datetime()
                    """,
                    subject_name=edge.subject,
                    object_name=edge.object
                )
                
                # Create the edge relationship
                session.run(
                    """
                    MATCH (subject:Entity {name: $subject_name})
                    MATCH (object:Entity {name: $object_name})
                    CREATE (subject)-[r:RELATES_TO {
                        edge_id: $edge_id,
                        relationship: $relationship,
                        summary: $summary,
                        obsolete: $obsolete,
                        status: $status,
                        confidence: $confidence,
                        created_at: datetime($created_at),
                        from_date: CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END,
                        to_date: CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END,
                        source: $source
                    }]->(object)
                    """,
                    subject_name=edge.subject,
                    object_name=edge.object,
                    edge_id=edge.edge_id,
                    relationship=edge.relationship,
                    summary=edge.metadata.summary,
                    obsolete=edge.metadata.obsolete,
                    status=edge.metadata.status.value,
                    confidence=edge.metadata.confidence,
                    created_at=edge.metadata.created_at.isoformat() if edge.metadata.created_at else datetime.now().isoformat(),
                    from_date=edge.metadata.from_date.isoformat() if edge.metadata.from_date else None,
                    to_date=edge.metadata.to_date.isoformat() if edge.metadata.to_date else None,
                    source=edge.metadata.source or ""
                )
                
                logger.info(f"Added edge: {edge.subject} -{edge.relationship}-> {edge.object}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding edge to graph: {e}")
            return False
    
    def update_edge(self, edge: GraphEdge) -> bool:
        """Update an existing edge"""
        try:
            # Validate edge data
            if not self._validate_edge(edge):
                logger.error(f"Edge validation failed: {edge}")
                return False
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH (subject:Entity {name: $subject_name})
                          -[r:RELATES_TO {edge_id: $edge_id}]->
                          (object:Entity {name: $object_name})
                    SET r.relationship = $relationship,
                        r.summary = $summary,
                        r.obsolete = $obsolete,
                        r.status = $status,
                        r.confidence = $confidence,
                        r.created_at = datetime($created_at),
                        r.from_date = CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END,
                        r.to_date = CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END,
                        r.source = $source
                    RETURN r
                    """,
                    subject_name=edge.subject,
                    object_name=edge.object,
                    edge_id=edge.edge_id,
                    relationship=edge.relationship,
                    summary=edge.metadata.summary,
                    obsolete=edge.metadata.obsolete,
                    status=edge.metadata.status.value,
                    confidence=edge.metadata.confidence,
                    created_at=edge.metadata.created_at.isoformat() if edge.metadata.created_at else datetime.now().isoformat(),
                    from_date=edge.metadata.from_date.isoformat() if edge.metadata.from_date else None,
                    to_date=edge.metadata.to_date.isoformat() if edge.metadata.to_date else None,
                    source=edge.metadata.source or ""
                )
                
                if result.single():
                    logger.info(f"Updated edge: {edge.edge_id}")
                    return True
                else:
                    # Edge doesn't exist, add it
                    return self.add_edge(edge)
                    
        except Exception as e:
            logger.error(f"Error updating edge: {e}")
            return False
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH ()-[r:RELATES_TO {edge_id: $edge_id}]->()
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
                query_parts = ["MATCH (s:Entity)-[r:RELATES_TO]->(o:Entity)"]
                where_clauses = []
                params = {}
                
                if subject:
                    where_clauses.append("s.name = $subject")
                    params["subject"] = subject
                    
                if obj:
                    where_clauses.append("o.name = $object")
                    params["object"] = obj
                    
                if relationship:
                    where_clauses.append("r.relationship = $relationship")
                    params["relationship"] = relationship
                    
                if filter_obsolete:
                    where_clauses.append("r.obsolete = false")
                
                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))
                
                query_parts.append("RETURN s, r, o")
                query = "\n".join(query_parts)
                
                result = session.run(query, params)
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"])
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                
                return results
                
        except Exception as e:
            logger.error(f"Error finding edges: {e}")
            return []
    
    def find_conflicting_edges(self, new_edge: GraphEdge) -> List[GraphEdge]:
        """Find edges that would conflict with the new edge"""
        conflicts = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Look for edges with same subject and relationship but different object
                result = session.run(
                    """
                    MATCH (s:Entity {name: $subject})
                          -[r:RELATES_TO {relationship: $relationship}]->
                          (o:Entity)
                    WHERE o.name <> $object AND r.obsolete = false
                    RETURN s, r, o
                    """,
                    subject=new_edge.subject,
                    relationship=new_edge.relationship,
                    object=new_edge.object
                )
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"])
                    conflicts.append(edge)
                
                return conflicts
                
        except Exception as e:
            logger.error(f"Error finding conflicts: {e}")
            return []
    
    def find_duplicate_edges(self, new_edge: GraphEdge) -> List[GraphEdge]:
        """Find exact duplicate edges"""
        duplicates = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH (s:Entity {name: $subject})
                          -[r:RELATES_TO {relationship: $relationship}]->
                          (o:Entity {name: $object})
                    WHERE r.obsolete = false
                    RETURN s, r, o
                    """,
                    subject=new_edge.subject,
                    relationship=new_edge.relationship,
                    object=new_edge.object
                )
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"])
                    duplicates.append(edge)
                
                return duplicates
                
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    def get_entity_relationships(self, entity: str, filter_obsolete: bool = True) -> List[GraphTriplet]:
        """Get all relationships for an entity"""
        results = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Find edges where entity is subject or object
                obsolete_filter = "AND r.obsolete = false" if filter_obsolete else ""
                
                result = session.run(
                    f"""
                    MATCH (e:Entity {{name: $entity}})
                    MATCH (e)-[r:RELATES_TO]-(other:Entity)
                    WHERE 1=1 {obsolete_filter}
                    RETURN e, r, other,
                           CASE WHEN startNode(r) = e THEN 'subject' ELSE 'object' END as role
                    """,
                    entity=entity
                )
                
                for record in result:
                    # Reconstruct edge with correct direction
                    if record["role"] == "subject":
                        edge = self._record_to_edge(record["e"], record["r"], record["other"])
                    else:
                        edge = self._record_to_edge(record["other"], record["r"], record["e"])
                    
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
                result = session.run(
                    """
                    MATCH ()-[r:RELATES_TO]->()
                    RETURN DISTINCT r.relationship as relationship
                    """
                )
                return [record["relationship"] for record in result if record["relationship"]]
                
        except Exception as e:
            logger.error(f"Error getting relationships: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get entity count
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                
                # Get edge counts
                edge_stats = session.run(
                    """
                    MATCH ()-[r:RELATES_TO]->()
                    RETURN count(r) as total,
                           sum(CASE WHEN r.obsolete = false THEN 1 ELSE 0 END) as active,
                           sum(CASE WHEN r.obsolete = true THEN 1 ELSE 0 END) as obsolete
                    """
                ).single()
                
                # Get relationship types
                relationships = self.get_relationships()
                
                return {
                    "total_entities": entity_count,
                    "total_edges": edge_stats["total"],
                    "active_edges": edge_stats["active"],
                    "obsolete_edges": edge_stats["obsolete"],
                    "relationship_types": len(relationships),
                    "relationships": relationships[:20]  # Show first 20
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def _normalize_entity_name(self, name: str) -> str:
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
                # Export edges
                edges_result = session.run(
                    """
                    MATCH (s:Entity)-[r:RELATES_TO]->(o:Entity)
                    RETURN s, r, o
                    """
                )
                
                edges = []
                for record in edges_result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"])
                    edges.append(edge.to_dict())
                
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
                from ..models import EdgeMetadata
                
                for edge_data in data["edges"]:
                    # Reconstruct edge object
                    metadata_data = edge_data["metadata"]
                    
                    metadata = EdgeMetadata(
                        summary=metadata_data["summary"],
                        created_at=datetime.fromisoformat(metadata_data["created_at"]),
                        from_date=datetime.fromisoformat(metadata_data["from_date"]) if metadata_data.get("from_date") else None,
                        to_date=datetime.fromisoformat(metadata_data["to_date"]) if metadata_data.get("to_date") else None,
                        obsolete=metadata_data.get("obsolete", False),
                        result=metadata_data.get("result"),
                        status=RelationshipStatus(metadata_data.get("status", "active")),
                        confidence=metadata_data.get("confidence", 1.0),
                        source=metadata_data.get("source")
                    )
                    
                    edge = GraphEdge(
                        subject=edge_data["subject"],
                        relationship=edge_data["relationship"],
                        object=edge_data["object"],
                        metadata=metadata,
                        edge_id=edge_data["edge_id"]
                    )
                    
                    self.add_edge(edge)
            
            logger.info(f"Imported {len(data.get('edges', []))} edges")
            return True
            
        except Exception as e:
            logger.error(f"Error importing graph data: {e}")
            return False
    
    def _record_to_edge(self, subject_node, relationship, object_node) -> GraphEdge:
        """Convert Neo4j record to GraphEdge"""
        from ..models import EdgeMetadata
        
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
            source=rel_props.get("source", "")
        )
        
        return GraphEdge(
            subject=subject_node["name"],
            relationship=rel_props.get("relationship", ""),
            object=object_node["name"],
            metadata=metadata,
            edge_id=rel_props.get("edge_id", str(uuid.uuid4()))
        )
    
    def _validate_edge(self, edge: GraphEdge) -> bool:
        """Validate edge data before adding to database"""
        # Check required fields
        if not edge.subject or not edge.relationship or not edge.object:
            logger.error("Edge missing required fields: subject, relationship, or object")
            return False
        
        # Validate metadata
        if not edge.metadata:
            logger.error("Edge missing metadata")
            return False
        
        # Validate confidence range (0.0 to 1.0)
        confidence = edge.metadata.confidence
        if confidence is not None and (confidence < 0.0 or confidence > 1.0):
            logger.error(f"Confidence value {confidence} outside valid range [0.0, 1.0]")
            return False
        
        # Validate status
        if edge.metadata.status not in [RelationshipStatus.ACTIVE, RelationshipStatus.OBSOLETE]:
            logger.error(f"Invalid status: {edge.metadata.status}")
            return False
        
        # Validate obsolete flag is boolean
        if not isinstance(edge.metadata.obsolete, bool):
            logger.error(f"Obsolete flag must be boolean, got: {type(edge.metadata.obsolete)}")
            return False
        
        return True
    
    def __del__(self):
        """Clean up Neo4j driver connection"""
        if hasattr(self, 'driver'):
            self.driver.close()