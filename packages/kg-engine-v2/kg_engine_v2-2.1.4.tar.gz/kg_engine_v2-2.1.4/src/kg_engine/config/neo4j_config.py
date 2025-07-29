"""Neo4j configuration and connection management."""

import os
from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()


class Neo4jConfig:
    """Neo4j database configuration and connection management."""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        """Initialize Neo4j configuration.
        
        Args:
            uri: Neo4j connection URI (default: from NEO4J_URI env var)
            username: Neo4j username (default: from NEO4J_USERNAME env var)
            password: Neo4j password (default: from NEO4J_PASSWORD env var)
            database: Neo4j database name (default: from NEO4J_DATABASE env var)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        
        self._driver: Optional[Driver] = None
    
    def get_driver(self) -> Driver:
        """Get or create Neo4j driver instance."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
        return self._driver
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def verify_connectivity(self) -> bool:
        """Verify connection to Neo4j database."""
        try:
            driver = self.get_driver()
            driver.verify_connectivity()
            return True
        except Exception:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information (without password)."""
        return {
            "uri": self.uri,
            "username": self.username,
            "database": self.database,
            "connected": self.verify_connectivity()
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Default configuration instance
neo4j_config = Neo4jConfig()