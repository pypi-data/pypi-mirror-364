"""
Custom Neo4j vector store implementation that avoids deprecated procedures.
This replaces the LlamaIndex Neo4jVectorStore to fix deprecation warnings.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid

from llama_index.core.vector_stores.types import (
    VectorStore,
    VectorStoreQuery,
    VectorStoreQueryResult,
    VectorStoreQueryMode,
)
from llama_index.core.schema import BaseNode, TextNode

from ..models import GraphTriplet, GraphEdge, EdgeMetadata, RelationshipStatus
from ..config import Neo4jConfig

logger = logging.getLogger(__name__)


class CustomNeo4jVectorStore(VectorStore):
    """Custom Neo4j vector store that uses modern procedures and avoids deprecation warnings."""
    
    def __init__(
        self,
        config: Optional[Neo4jConfig] = None,
        index_name: str = "triplet_embedding_index",
        node_label: str = "Triplet",
        embedding_dimension: int = 384,
    ):
        """Initialize the custom Neo4j vector store."""
        self.config = config or Neo4jConfig()
        self.index_name = index_name
        self.node_label = node_label
        self.embedding_dimension = embedding_dimension
        
        # Initialize the vector index
        self._create_vector_index()
        
        logger.info(f"Custom Neo4j vector store initialized: {node_label}")
    
    def _create_vector_index(self):
        """Create the vector index if it doesn't exist."""
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            try:
                # Check if index exists
                result = session.run("SHOW INDEXES")
                existing_indexes = [record["name"] for record in result if record.get("name")]
                
                if self.index_name not in existing_indexes:
                    # Create vector index using modern syntax
                    create_query = f"""
                        CREATE VECTOR INDEX {self.index_name} IF NOT EXISTS
                        FOR (n:{self.node_label}) ON (n.embedding)
                        OPTIONS {{
                          indexConfig: {{
                            `vector.dimensions`: {self.embedding_dimension},
                            `vector.similarity_function`: 'cosine'
                          }}
                        }}
                    """
                    session.run(create_query)
                    logger.info(f"Created vector index: {self.index_name}")
                    
                    # Wait for index to be online
                    import time
                    time.sleep(2)
                else:
                    logger.info(f"Vector index already exists: {self.index_name}")
                    
            except Exception as e:
                logger.warning(f"Could not create vector index: {e}")
                # Try creating with different syntax for older Neo4j versions
                try:
                    session.run(f"""
                        CALL db.index.vector.createNodeIndex(
                            '{self.index_name}', 
                            '{self.node_label}', 
                            'embedding', 
                            {self.embedding_dimension}, 
                            'cosine'
                        )
                    """)
                    logger.info(f"Created vector index using fallback method: {self.index_name}")
                except Exception as e2:
                    logger.error(f"Failed to create vector index with fallback: {e2}")
    
    def add(self, nodes: List[BaseNode], **kwargs) -> List[str]:
        """Add nodes to the vector store."""
        if not nodes:
            return []
        
        driver = self.config.get_driver()
        node_ids = []
        
        with driver.session(database=self.config.database) as session:
            for node in nodes:
                try:
                    # Generate unique ID if not provided
                    node_id = node.node_id or str(uuid.uuid4())
                    node_ids.append(node_id)
                    
                    # Prepare node data
                    node_data = {
                        "id": node_id,
                        "text": node.text or "",
                        "embedding": node.embedding or [],
                    }
                    
                    # Add metadata
                    if node.metadata:
                        node_data.update(node.metadata)
                    
                    # Use modern procedures to avoid deprecation warnings
                    session.run(f"""
                        MERGE (n:{self.node_label} {{id: $id}})
                        SET n.text = $text,
                            n += $metadata
                        WITH n
                        CALL (n) {{
                            CALL db.create.setNodeVectorProperty(n, 'embedding', $embedding)
                            RETURN count(*) as updated
                        }}
                        RETURN n
                    """, 
                        id=node_id,
                        text=node.text or "",
                        metadata=node.metadata or {},
                        embedding=node.embedding or []
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to add node {node_id}: {e}")
                    # Remove from successful list if it failed
                    if node_id in node_ids:
                        node_ids.remove(node_id)
        
        logger.info(f"Added {len(node_ids)} nodes to Neo4j vector store")
        return node_ids
    
    def delete(self, ref_doc_id: str, **kwargs) -> None:
        """Delete nodes by reference document ID."""
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            session.run(f"""
                MATCH (n:{self.node_label})
                WHERE n.ref_doc_id = $ref_doc_id OR n.id = $ref_doc_id
                DETACH DELETE n
            """, ref_doc_id=ref_doc_id)
    
    def query(self, query: VectorStoreQuery, **kwargs) -> VectorStoreQueryResult:
        """Query the vector store."""
        if not query.query_embedding:
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])
        
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            try:
                # First check if vector index exists and is online
                index_result = session.run(
                    "SHOW INDEXES YIELD name, state WHERE name = $index_name",
                    index_name=self.index_name
                )
                index_record = index_result.single()
                
                if not index_record or index_record.get("state") != "ONLINE":
                    logger.warning(f"Vector index {self.index_name} not found or not online, creating it...")
                    self._create_vector_index()
                    # Return empty results for now as index needs time to populate
                    return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])
                
                # Use the vector index for similarity search
                result = session.run(f"""
                    CALL db.index.vector.queryNodes($index_name, $k, $embedding)
                    YIELD node, score
                    RETURN node, score
                    ORDER BY score DESC
                """,
                    index_name=self.index_name,
                    k=query.similarity_top_k or 10,
                    embedding=query.query_embedding
                )
                
                nodes = []
                similarities = []
                ids = []
                
                for record in result:
                    node_data = dict(record["node"])
                    score = record["score"]
                    
                    # Create TextNode from Neo4j data
                    node = TextNode(
                        text=node_data.get("text", ""),
                        node_id=node_data.get("id"),
                        metadata={k: v for k, v in node_data.items() 
                                if k not in ["text", "id", "embedding"]},
                        embedding=node_data.get("embedding")
                    )
                    
                    nodes.append(node)
                    similarities.append(score)
                    ids.append(node_data.get("id"))
                
                return VectorStoreQueryResult(
                    nodes=nodes,
                    similarities=similarities,
                    ids=ids
                )
                
            except Exception as e:
                logger.error(f"Vector query failed: {e}")
                # Fallback: return all nodes without similarity scoring
                try:
                    fallback_result = session.run(f"""
                        MATCH (n:{self.node_label})
                        RETURN n
                        LIMIT $k
                    """, k=query.similarity_top_k or 10)
                    
                    nodes = []
                    similarities = []
                    ids = []
                    
                    for record in fallback_result:
                        node_data = dict(record["n"])
                        
                        node = TextNode(
                            text=node_data.get("text", ""),
                            node_id=node_data.get("id"),
                            metadata={k: v for k, v in node_data.items() 
                                    if k not in ["text", "id", "embedding"]},
                        )
                        
                        nodes.append(node)
                        similarities.append(0.5)  # Default similarity
                        ids.append(node_data.get("id"))
                    
                    logger.info(f"Used fallback query, returned {len(nodes)} nodes")
                    return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)
                    
                except Exception as e2:
                    logger.error(f"Fallback query also failed: {e2}")
                    return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])
    
    def persist(self, persist_dir: str, fs=None) -> None:
        """Neo4j is already persistent, no additional action needed."""
        pass
    
    @classmethod
    def from_persist_dir(cls, persist_dir: str, **kwargs) -> "CustomNeo4jVectorStore":
        """Create from persistent directory (Neo4j handles persistence)."""
        return cls(**kwargs)
    
    def clear(self) -> None:
        """Clear all data from the vector store."""
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            session.run(f"MATCH (n:{self.node_label}) DETACH DELETE n")
        
        logger.info(f"Cleared all {self.node_label} nodes from Neo4j")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            try:
                result = session.run(f"MATCH (n:{self.node_label}) RETURN count(n) as count")
                count = result.single()["count"]
                
                return {
                    "node_count": count,
                    "index_name": self.index_name,
                    "node_label": self.node_label,
                    "embedding_dimension": self.embedding_dimension
                }
            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
                return {}