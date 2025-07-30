"""KG Engine v2 - Advanced Knowledge Graph Engine with Semantic Search

Features:
- LLM-powered entity and relationship extraction
- Semantic relationship synonym handling (TEACH_IN ≈ WORKS_AT)
- Vector search with Neo4j and sentence transformers
- Smart duplicate detection and conflict resolution using semantic similarity
- Temporal relationship tracking with date ranges
- Hybrid search combining graph traversal and semantic similarity
- Natural language query understanding and response generation
"""

from .core import KnowledgeGraphEngineV2
from .models import (
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet,
    SearchResult, QueryResponse, RelationshipStatus, SearchType,
    ExtractedInfo, ParsedQuery
)

__version__ = "2.1.0"
__all__ = [
    "KnowledgeGraphEngineV2",
    "InputItem", 
    "GraphEdge",
    "EdgeMetadata", 
    "GraphTriplet",
    "SearchResult",
    "QueryResponse",
    "RelationshipStatus",
    "SearchType",
    "ExtractedInfo",
    "ParsedQuery",
]