"""
Data models for Knowledge Graph Engine v2
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class RelationshipStatus(Enum):
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class SearchType(Enum):
    DIRECT = "direct"
    SEMANTIC = "semantic"
    BOTH = "both"


@dataclass
class InputItem:
    description: str
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeMetadata:
    summary: str
    created_at: datetime = field(default_factory=datetime.now)
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    obsolete: bool = False
    result: Optional[str] = None
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    confidence: float = 1.0
    source: Optional[str] = None
    user_id: Optional[str] = None  # User ID (GUID) for multi-tenant support
    additional_metadata: Dict[str, Any] = field(default_factory=dict)  # For extra metadata
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = {
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'from_date': self.from_date.isoformat() if self.from_date else None,
            'to_date': self.to_date.isoformat() if self.to_date else None,
            'obsolete': self.obsolete,
            'result': self.result,
            'status': self.status.value,
            'confidence': self.confidence,
            'source': self.source,
            'user_id': self.user_id
        }
        # Merge additional metadata
        base_dict.update(self.additional_metadata)
        return base_dict


@dataclass
class GraphEdge:
    subject: str
    relationship: str
    object: str
    metadata: EdgeMetadata
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'edge_id': self.edge_id,
            'subject': self.subject,
            'relationship': self.relationship,
            'object': self.object,
            'metadata': self.metadata.to_dict()
        }


@dataclass
class GraphTriplet:
    edge: GraphEdge
    vector_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    vector_text: Optional[str] = None
    
    def to_vector_text(self) -> str:
        """Create text representation for vectorization"""
        if self.vector_text:
            return self.vector_text
            
        base_text = f"{self.edge.subject} {self.edge.relationship} {self.edge.object}"
        summary = self.edge.metadata.summary
        
        if summary and summary.lower() not in base_text.lower():
            self.vector_text = f"{base_text} - {summary}"
        else:
            self.vector_text = base_text
            
        return self.vector_text


@dataclass
class ExtractedInfo:
    subject: str
    relationship: str
    object: str
    summary: str
    is_negation: bool = False
    confidence: float = 1.0
    

@dataclass
class ParsedQuery:
    entities: List[str]
    relationships: List[str]
    search_type: SearchType
    query_intent: str = "search"  # search, count, exists, etc.
    temporal_context: Optional[str] = None


@dataclass
class SearchResult:
    triplet: GraphTriplet
    score: float
    source: str  # "graph", "vector", "hybrid"
    explanation: Optional[str] = None
    

@dataclass
class QueryResponse:
    results: List[SearchResult]
    total_found: int
    query_time_ms: float
    answer: Optional[str] = None
    confidence: float = 1.0