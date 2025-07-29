"""Neo4j schema management and setup utilities."""

from typing import List, Dict, Any, Optional
from neo4j import Session, Driver
from .neo4j_config import Neo4jConfig


class Neo4jSchemaManager:
    """Manages Neo4j database schema setup and maintenance."""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize schema manager.
        
        Args:
            config: Neo4j configuration instance
        """
        self.config = config or Neo4jConfig()
    
    def setup_schema(self) -> Dict[str, List[str]]:
        """Set up complete Neo4j schema including constraints, indexes, and vector indexes.
        
        Returns:
            Dict with lists of created constraints, indexes, and vector indexes
        """
        results = {
            "constraints": [],
            "indexes": [], 
            "vector_indexes": []
        }
        
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            # Create constraints
            constraints = self._create_constraints(session)
            results["constraints"].extend(constraints)
            
            # Create regular indexes
            indexes = self._create_indexes(session)
            results["indexes"].extend(indexes)
            
            # Create vector indexes
            vector_indexes = self._create_vector_indexes(session)
            results["vector_indexes"].extend(vector_indexes)
        
        return results
    
    def _create_constraints(self, session: Session) -> List[str]:
        """Create database constraints."""
        constraints = [
            "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
            "CREATE CONSTRAINT triplet_unique IF NOT EXISTS FOR (t:Triplet) REQUIRE (t.subject, t.relationship, t.object) IS UNIQUE"
            # Note: Value constraints (IN, range checks) are not supported in older Neo4j versions
            # Data validation will be handled at the application level instead
        ]
        
        created = []
        for constraint in constraints:
            try:
                session.run(constraint)
                created.append(constraint.split("IF NOT EXISTS")[0].strip())
            except Exception as e:
                print(f"Warning: Could not create constraint: {e}")
        
        return created
    
    def _create_indexes(self, session: Session) -> List[str]:
        """Create database indexes."""
        indexes = [
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
            "CREATE INDEX entity_created_index IF NOT EXISTS FOR (e:Entity) ON (e.created_at)",
            "CREATE INDEX triplet_status_index IF NOT EXISTS FOR (t:Triplet) ON (t.status)",
            "CREATE INDEX triplet_obsolete_index IF NOT EXISTS FOR (t:Triplet) ON (t.obsolete)",
            "CREATE INDEX triplet_confidence_index IF NOT EXISTS FOR (t:Triplet) ON (t.confidence)",
            "CREATE INDEX triplet_created_index IF NOT EXISTS FOR (t:Triplet) ON (t.created_at)",
            "CREATE INDEX triplet_from_date_index IF NOT EXISTS FOR (t:Triplet) ON (t.from_date)",
            "CREATE INDEX triplet_to_date_index IF NOT EXISTS FOR (t:Triplet) ON (t.to_date)",
            "CREATE INDEX triplet_source_index IF NOT EXISTS FOR (t:Triplet) ON (t.source)"
        ]
        
        created = []
        for index in indexes:
            try:
                session.run(index)
                created.append(index.split("IF NOT EXISTS")[0].strip())
            except Exception as e:
                print(f"Warning: Could not create index: {e}")
        
        return created
    
    def _create_vector_indexes(self, session: Session) -> List[str]:
        """Create vector indexes for embeddings."""
        vector_indexes = [
            """
            CREATE VECTOR INDEX triplet_embedding_index IF NOT EXISTS
            FOR (t:Triplet) ON (t.embedding)
            OPTIONS {
              indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
              }
            }
            """
        ]
        
        created = []
        for index in vector_indexes:
            try:
                session.run(index.strip())
                created.append("triplet_embedding_index")
            except Exception as e:
                print(f"Warning: Could not create vector index: {e}")
        
        return created
    
    def drop_schema(self) -> Dict[str, List[str]]:
        """Drop all schema elements (constraints, indexes, vector indexes).
        
        WARNING: This will remove all schema elements but preserve data.
        
        Returns:
            Dict with lists of dropped elements
        """
        results = {
            "constraints": [],
            "indexes": [],
            "vector_indexes": []
        }
        
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            # Get existing constraints
            constraint_result = session.run("SHOW CONSTRAINTS")
            for record in constraint_result:
                name = record.get("name")
                if name:
                    try:
                        session.run(f"DROP CONSTRAINT {name}")
                        results["constraints"].append(name)
                    except Exception as e:
                        print(f"Warning: Could not drop constraint {name}: {e}")
            
            # Get existing indexes (including vector indexes)
            index_result = session.run("SHOW INDEXES")
            for record in index_result:
                name = record.get("name")
                index_type = record.get("type", "")
                if name and name not in ["__label_id", "__rel_id"]:  # Skip system indexes
                    try:
                        session.run(f"DROP INDEX {name}")
                        if "VECTOR" in index_type.upper():
                            results["vector_indexes"].append(name)
                        else:
                            results["indexes"].append(name)
                    except Exception as e:
                        print(f"Warning: Could not drop index {name}: {e}")
        
        return results
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get current schema information."""
        driver = self.config.get_driver()
        
        with driver.session(database=self.config.database) as session:
            # Get constraints
            constraints = []
            constraint_result = session.run("SHOW CONSTRAINTS")
            for record in constraint_result:
                constraints.append({
                    "name": record.get("name"),
                    "description": record.get("description"),
                    "type": record.get("type")
                })
            
            # Get indexes
            indexes = []
            vector_indexes = []
            index_result = session.run("SHOW INDEXES")
            for record in index_result:
                index_info = {
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "state": record.get("state"),
                    "population_percent": record.get("populationPercent")
                }
                
                if "VECTOR" in record.get("type", "").upper():
                    vector_indexes.append(index_info)
                elif record.get("name") not in ["__label_id", "__rel_id"]:
                    indexes.append(index_info)
        
        return {
            "constraints": constraints,
            "indexes": indexes,
            "vector_indexes": vector_indexes
        }


def setup_neo4j_schema(config: Optional[Neo4jConfig] = None) -> Dict[str, List[str]]:
    """Convenience function to set up Neo4j schema.
    
    Args:
        config: Neo4j configuration instance
        
    Returns:
        Dict with lists of created schema elements
    """
    schema_manager = Neo4jSchemaManager(config)
    return schema_manager.setup_schema()