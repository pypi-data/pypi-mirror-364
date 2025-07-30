"""Configuration for Knowledge Graph Engine"""
from .neo4j_config import Neo4jConfig
from .neo4j_schema import setup_neo4j_schema

__all__ = [
    "Neo4jConfig",
    "setup_neo4j_schema",
]