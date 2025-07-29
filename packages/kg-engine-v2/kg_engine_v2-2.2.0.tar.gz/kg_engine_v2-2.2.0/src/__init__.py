"""Knowledge Graph Engine v2 - Root package"""

from kg_engine import (
    KnowledgeGraphEngineV2,
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