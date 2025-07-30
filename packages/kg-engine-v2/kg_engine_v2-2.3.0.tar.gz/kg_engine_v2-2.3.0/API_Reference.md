# KG Engine v2 - API Reference

This document provides a comprehensive reference for all exported types and classes available when using KG Engine v2 as an external package.

## Quick Start

```python
from kg_engine import KnowledgeGraphEngineV2, InputItem, Neo4jConfig

# Initialize
config = Neo4jConfig()
engine = KnowledgeGraphEngineV2(api_key="your-key", neo4j_config=config)

# Process data
results = engine.process_input([InputItem("Alice works at Google")])
```

## API Categories

The API is organized into logical categories for different use cases:

### 🔧 Core API (Essential)
*Basic classes for standard usage*

### ⚙️ Configuration API  
*Setup and configuration classes*

### 🗄️ Storage API (Advanced)
*Direct storage operations*

### 🤖 LLM API (Advanced)
*Language model integration*

### 🛠️ Utilities API
*Helper functions and optimizers*

---

## 🔧 Core API Reference

### `KnowledgeGraphEngineV2`
Main engine class for knowledge graph operations.

```python
from kg_engine import KnowledgeGraphEngineV2

engine = KnowledgeGraphEngineV2(
    api_key="your-openai-key",          # OpenAI API key or "ollama" for local
    model="gpt-4o",                     # Model name  
    base_url=None,                      # Custom API base URL
    vector_collection="kg_v2",          # Vector collection name
    neo4j_config=None,                  # Neo4j configuration
    bearer_token=None                   # Bearer token for auth
)
```

**Key Methods:**
- `process_input(items: List[InputItem]) -> Dict[str, Any]`
- `search(query: str, search_type: SearchType, k: int) -> QueryResponse`
- `get_node_relations(node_name: str) -> List[SearchResult]`
- `get_stats() -> Dict[str, Any]`
- `clear_all_data() -> bool`

### `InputItem`
Data structure for input text and metadata.

```python
from kg_engine import InputItem

item = InputItem(
    description="Alice works at Google",
    metadata={
        "source": "web_form",
        "user_id": "123",
        "timestamp": "2024-01-01T00:00:00Z"
    }
)
```

### `EdgeData`
Structure for creating edges programmatically.

```python
from kg_engine import EdgeData, EdgeMetadata

edge = EdgeData(
    subject="Alice",
    relationship="WORKS_AT", 
    object="Google",
    metadata=EdgeMetadata(
        summary="Alice works at Google",
        confidence=0.95,
        category="employment"
    )
)
```

### `EdgeMetadata`
Metadata for edges with temporal and confidence information.

```python
from kg_engine import EdgeMetadata, RelationshipStatus, parse_date

metadata = EdgeMetadata(
    summary="Descriptive summary",
    confidence=0.95,                    # 0.0 to 1.0
    source="data_source",
    user_id="user123",
    category="business",
    from_date=parse_date("2022-01-01"),
    to_date=parse_date("2024-01-01"),
    status=RelationshipStatus.ACTIVE,
    obsolete=False
)
```

### `GraphEdge`
Represents a relationship in the graph.

```python
from kg_engine import GraphEdge

# GraphEdge has lazy loading - access via safe methods
subject = edge.get_subject_safe()
relationship = edge.get_relationship_safe() 
object = edge.get_object_safe()
```

### `SearchResult`
Individual search result with confidence score.

```python
# Returned from search operations
result = SearchResult(
    triplet=graph_triplet,      # GraphTriplet
    score=0.95,                 # Confidence score
    source="vector_graph",      # Search source
    explanation="Match reason"  # Human-readable explanation
)
```

### `QueryResponse`
Complete search response with results and metadata.

```python
response = QueryResponse(
    results=[...],              # List[SearchResult]
    total_found=25,            # Total matches found
    query_time_ms=150.5,       # Processing time
    answer="Generated answer",  # LLM-generated answer
    confidence=0.85            # Overall confidence
)
```

### Enums

```python
from kg_engine import RelationshipStatus, SearchType

# Relationship status
RelationshipStatus.ACTIVE
RelationshipStatus.OBSOLETE
RelationshipStatus.PENDING

# Search types
SearchType.DIRECT      # Graph traversal only
SearchType.SEMANTIC    # Vector search only  
SearchType.BOTH        # Hybrid search
```

---

## ⚙️ Configuration API Reference

### `Neo4jConfig`
Neo4j database connection configuration.

```python
from kg_engine import Neo4jConfig

config = Neo4jConfig(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password",
    database="neo4j"
)

# Test connection
if config.verify_connectivity():
    print("Connected to Neo4j")
```

### `Neo4jSchemaManager`
Manage Neo4j database schema.

```python
from kg_engine import Neo4jSchemaManager

manager = Neo4jSchemaManager(config)

# Setup complete schema
results = manager.setup_schema()
print(f"Created {len(results['constraints'])} constraints")

# Get current schema info
info = manager.get_schema_info()
```

### `setup_neo4j_schema()`
Convenience function for schema setup.

```python
from kg_engine import setup_neo4j_schema, Neo4jConfig

config = Neo4jConfig()
results = setup_neo4j_schema(config)
```

---

## 🗄️ Storage API Reference (Advanced)

### `GraphDB`
Direct Neo4j graph database operations.

```python
from kg_engine import GraphDB, Neo4jConfig

graph_db = GraphDB(Neo4jConfig())

# Basic operations
entities = graph_db.get_entities()
relationships = graph_db.get_relationships()
stats = graph_db.get_stats()

# CRUD operations
success = graph_db.add_edge_data(edge_data)
edge = graph_db.get_edge_by_id("edge_id")
edges = graph_db.list_edges(skip=0, limit=50)

# Node operations
node = graph_db.get_node_by_name("Alice")
nodes = graph_db.list_nodes(limit=100)
```

### `VectorStore`
Vector search operations.

```python
from kg_engine import VectorStore, Neo4jConfig

vector_store = VectorStore(
    collection_name="my_collection",
    neo4j_config=Neo4jConfig()
)

# Search operations
results = vector_store.search("query text", k=10)
stats = vector_store.get_stats()
```

---

## 🤖 LLM API Reference (Advanced)

### `LLMInterface`
Direct language model operations.

```python
from kg_engine import LLMInterface, ClassifierMap

llm = LLMInterface(
    api_key="your-key",
    model="gpt-4o",
    base_url=None,                    # For custom endpoints
    classifier_map=classifier_map    # For edge classification
)

# Extract entities and relationships
extracted = llm.extract_entities_relationships("Alice works at Google")

# Parse queries
parsed = llm.parse_query("Who works in tech?", relationship_types)

# Generate answers
answer = llm.generate_answer("Who is Alice?", context_summaries)
```

### `ClassifierMap`
Manage edge classification categories.

```python
from kg_engine import ClassifierMap, GraphDB

classifier_map = ClassifierMap(graph_db)

# Get categories and edges
categories = classifier_map.get_all_categories()
edges = classifier_map.get_edges_by_classifier("business")
stats = classifier_map.get_stats()
```

---

## 🛠️ Utilities API Reference

### `parse_date()`
Parse date strings into datetime objects.

```python
from kg_engine import parse_date

dates = [
    parse_date("2024-01-15"),          # ISO format
    parse_date("January 15, 2024"),    # Natural language
    parse_date("last week"),           # Relative dates
    parse_date("invalid"),             # Returns None
]
```

### `GraphQueryOptimizer`
Optimize graph database queries.

```python
from kg_engine import GraphQueryOptimizer, QueryType, Neo4jConfig

optimizer = GraphQueryOptimizer(Neo4jConfig())

# Available query types
QueryType.ENTITY_EXPLORATION
QueryType.PATH_FINDING
QueryType.CONFLICT_DETECTION
QueryType.TEMPORAL_ANALYSIS
```

### `Neo4jOptimizer`
Neo4j performance optimization.

```python
from kg_engine import Neo4jOptimizer, Neo4jConfig

optimizer = Neo4jOptimizer(Neo4jConfig())

# Analyze index performance
analysis = optimizer.analyze_vector_index_performance("index_name")
```

### `ClassifierDetector`
Detect and classify edge types.

```python
from kg_engine import ClassifierDetector

detector = ClassifierDetector(classifier_map, embedder)

# Detect category for edge
category = detector.detect_category("WORKS_AT")
best_edge = detector.find_best_edge_match("employed_by", "business")
```

---

## Usage Patterns

### Basic Usage Pattern
```python
from kg_engine import KnowledgeGraphEngineV2, InputItem, Neo4jConfig

# Setup
config = Neo4jConfig()
engine = KnowledgeGraphEngineV2(api_key="key", neo4j_config=config)

# Process
results = engine.process_input([
    InputItem("Alice works at Google"),
    InputItem("Bob lives in San Francisco")
])

# Search
response = engine.search("Who works in technology?")
```

### Advanced Usage Pattern
```python
from kg_engine import (
    GraphDB, VectorStore, EdgeData, EdgeMetadata, 
    Neo4jConfig, parse_date
)

# Direct storage operations
graph_db = GraphDB(Neo4jConfig())
vector_store = VectorStore("collection")

# Create edge manually
edge = EdgeData(
    subject="Alice",
    relationship="WORKS_AT",
    object="Google", 
    metadata=EdgeMetadata(
        summary="Alice works at Google",
        from_date=parse_date("2022-01-01")
    )
)

graph_db.add_edge_data(edge)
```

### Schema Management Pattern
```python
from kg_engine import setup_neo4j_schema, Neo4jSchemaManager, Neo4jConfig

# Quick setup
config = Neo4jConfig()
setup_neo4j_schema(config)

# Advanced management
manager = Neo4jSchemaManager(config)
info = manager.get_schema_info()
```

## Type Hints and IDE Support

All classes include comprehensive type hints for full IDE support:

```python
from typing import List, Dict, Any, Optional
from kg_engine import InputItem, SearchResult, QueryResponse

def process_data(items: List[InputItem]) -> Dict[str, Any]:
    # Full type checking and autocompletion
    pass
```

## Error Handling

All operations include proper error handling:

```python
from kg_engine import KnowledgeGraphEngineV2, Neo4jConfig

try:
    config = Neo4jConfig()
    if not config.verify_connectivity():
        raise ConnectionError("Cannot connect to Neo4j")
    
    engine = KnowledgeGraphEngineV2(api_key="key", neo4j_config=config)
    results = engine.process_input(items)
    
except Exception as e:
    print(f"Error: {e}")
```

---

## Version Information

```python
from kg_engine import __version__
print(f"KG Engine v{__version__}")  # "2.1.0"
```

This API reference covers all exported types and classes. For additional examples, see the `examples/` directory.