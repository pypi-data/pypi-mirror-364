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
    category: Optional[str] = None  # Classifier category (location, business, relations, etc.)
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
            'user_id': self.user_id,
            'category': self.category
        }
        # Merge additional metadata
        base_dict.update(self.additional_metadata)
        return base_dict


@dataclass
class GraphEdge:
    """
    Represents an edge in the knowledge graph.
    
    In Neo4j, edges are stored with specific relationship types:
    (subject:Entity) -[:WORKS_AT {edge_id, metadata...}]-> (object:Entity)
    
    The subject, relationship type, and object are derived from the graph structure,
    not stored redundantly in the edge.
    """
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: EdgeMetadata = field(default_factory=EdgeMetadata)
    
    # These fields are populated when loading from Neo4j, not stored
    _subject: Optional[str] = field(default=None, init=False, repr=False)
    _relationship: Optional[str] = field(default=None, init=False, repr=False)
    _object: Optional[str] = field(default=None, init=False, repr=False)
    
    @property
    def subject(self) -> str:
        """Get subject node name (populated from Neo4j)"""
        if self._subject is None:
            raise ValueError("Subject not populated. Edge must be loaded from Neo4j.")
        return self._subject
    
    @property
    def relationship(self) -> str:
        """Get relationship type (populated from Neo4j)"""
        if self._relationship is None:
            raise ValueError("Relationship not populated. Edge must be loaded from Neo4j.")
        return self._relationship
    
    @property
    def object(self) -> str:
        """Get object node name (populated from Neo4j)"""
        if self._object is None:
            raise ValueError("Object not populated. Edge must be loaded from Neo4j.")
        return self._object
    
    def set_graph_data(self, subject: str, relationship: str, object: str) -> None:
        """Set the graph structure data (used when loading from Neo4j)"""
        self._subject = subject
        self._relationship = relationship
        self._object = object
    
    def has_graph_data(self) -> bool:
        """Check if graph data is populated"""
        return self._subject is not None and self._relationship is not None and self._object is not None
    
    def get_graph_data(self) -> tuple[str, str, str]:
        """Get graph data as tuple (subject, relationship, object)"""
        if not self.has_graph_data():
            raise ValueError("Graph data not populated. Edge must be loaded from Neo4j.")
        return self._subject, self._relationship, self._object
    
    def get_subject_safe(self) -> Optional[str]:
        """Get subject without raising error if not populated"""
        return self._subject
    
    def get_relationship_safe(self) -> Optional[str]:
        """Get relationship without raising error if not populated"""
        return self._relationship
    
    def get_object_safe(self) -> Optional[str]:
        """Get object without raising error if not populated"""
        return self._object
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (includes graph data if available)"""
        result = {
            'edge_id': self.edge_id,
            'metadata': self.metadata.to_dict()
        }
        # Include graph data if populated
        if self._subject is not None:
            result['subject'] = self._subject
            result['relationship'] = self._relationship
            result['object'] = self._object
        return result
    
    @classmethod
    def create_for_storage(cls, edge_id: Optional[str] = None, 
                          metadata: Optional[EdgeMetadata] = None) -> 'GraphEdge':
        """Create a minimal edge for storage (without graph data)"""
        return cls(
            edge_id=edge_id or str(uuid.uuid4()),
            metadata=metadata or EdgeMetadata(summary="")
        )


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
            
        # Use safe accessors to handle edges without populated graph data
        if self.edge.has_graph_data():
            subject, relationship, obj = self.edge.get_graph_data()
            base_text = f"{subject} {relationship} {obj}"
        else:
            # Fallback for edges without graph data
            base_text = f"Edge {self.edge.edge_id}"
        summary = self.edge.metadata.summary
        
        if summary and summary.lower() not in base_text.lower():
            self.vector_text = f"{base_text} - {summary}"
        else:
            self.vector_text = base_text
            
        return self.vector_text


@dataclass
class EdgeData:
    """Helper class for passing edge creation data"""
    subject: str
    relationship: str
    object: str
    metadata: EdgeMetadata
    edge_id: Optional[str] = None


@dataclass
class ExtractedInfo:
    subject: str
    relationship: str
    object: str
    summary: str
    is_negation: bool = False
    confidence: float = 1.0
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    category: Optional[str] = None
    

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