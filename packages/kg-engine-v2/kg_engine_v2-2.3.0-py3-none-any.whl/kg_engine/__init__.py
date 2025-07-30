"""KG Engine v2 - Advanced Knowledge Graph Engine with Semantic Search

Features:
- LLM-powered entity and relationship extraction
- Semantic relationship synonym handling (TEACH_IN ≈ WORKS_AT)
- Vector search with Neo4j and sentence transformers
- Smart duplicate detection and conflict resolution using semantic similarity
- Temporal relationship tracking with date ranges
- Hybrid search combining graph traversal and semantic similarity
- Natural language query understanding and response generation

Public API:
This package exports all classes and types needed for external usage.
"""

# Core Engine
from .core import KnowledgeGraphEngineV2

# Data Models and Types
from .models import (
    # Core data structures
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet, EdgeData,
    SearchResult, QueryResponse, ExtractedInfo, ParsedQuery,
    
    # Enums
    RelationshipStatus, SearchType
)

# Configuration
from .config import Neo4jConfig
from .config.neo4j_schema import Neo4jSchemaManager, setup_neo4j_schema

# Storage Layer (for advanced usage)
from .storage import VectorStore, GraphDB

# LLM Interface (for advanced usage)
from .llm import LLMInterface

# Utilities
from .utils.date_parser import parse_date
from .utils.graph_query_optimizer import GraphQueryOptimizer, QueryType
from .utils.neo4j_optimizer import Neo4jOptimizer
from .utils.classifier_detector import ClassifierDetector

# Model utilities
from .models.classifier_map import ClassifierMap

__version__ = "2.1.0"

# Core API - Essential classes for basic usage
__core_api__ = [
    "KnowledgeGraphEngineV2",
    "InputItem", 
    "GraphEdge",
    "EdgeMetadata", 
    "GraphTriplet",
    "EdgeData",
    "SearchResult",
    "QueryResponse",
    "RelationshipStatus",
    "SearchType",
    "ExtractedInfo",
    "ParsedQuery",
]

# Configuration API - Setup and configuration
__config_api__ = [
    "Neo4jConfig",
    "Neo4jSchemaManager", 
    "setup_neo4j_schema",
]

# Storage API - Advanced storage operations
__storage_api__ = [
    "VectorStore",
    "GraphDB",
]

# LLM API - Advanced LLM operations
__llm_api__ = [
    "LLMInterface",
]

# Utilities API - Helper functions and optimizers
__utils_api__ = [
    "parse_date",
    "GraphQueryOptimizer",
    "QueryType",
    "Neo4jOptimizer", 
    "ClassifierDetector",
    "ClassifierMap",
]

# Complete public API
__all__ = __core_api__ + __config_api__ + __storage_api__ + __llm_api__ + __utils_api__