# API Reference

Complete API documentation for Knowledge Graph Engine v2 components.

## 🆕 Version 2.1.0 Updates

- **Performance Optimizations**: 50-74% faster queries with GraphQueryOptimizer and Neo4jOptimizer
- **Smart Caching**: Query result caching with 5-minute TTL for near-instant repeated queries
- **GraphEdge Refactoring**: Lazy loading with safe accessors, 18% smaller codebase
- **Dynamic Relationships**: WORKS_AT, LIVES_IN instead of generic RELATES_TO
- **Bug Fixes**: Fixed "Relationship not populated" errors, enhanced source filtering
- **Safe Data Access**: Robust error handling with `get_subject_safe()`, `get_relationship_safe()`, `get_object_safe()`
- **Search Documentation**: See [Search Improvements](../architecture/search-improvements.md)

## 📑 API Modules

### [Engine API](./engine.md)
Core Knowledge Graph Engine class and methods for processing and querying knowledge.

### [Models](./models.md) 
Data models, schemas, and type definitions used throughout the system.

### [Neo4j Configuration](./neo4j-config.md)
Neo4j connection configuration and database management.

### [Vector Store](./vector-store.md)
Vector storage and semantic search functionality.

## 🚀 Quick API Overview

### Basic Usage

```python
from src.kg_engine import KnowledgeGraphEngineV2, InputItem
from src.kg_engine.config import Neo4jConfig

# Initialize
engine = KnowledgeGraphEngineV2(
    api_key="your-openai-key",
    neo4j_config=Neo4jConfig()
)

# Process information
result = engine.process_input([
    InputItem(description="Alice works at Google")
])

# Search knowledge
response = engine.search("Who works at Google?")
print(response.answer)
```

### Core Classes

| Class | Module | Description |
|-------|--------|-------------|
| `KnowledgeGraphEngineV2` | `engine.py` | Main engine orchestrator |
| `InputItem` | `models.py` | Input data container |
| `GraphTriplet` | `models.py` | Graph relationship representation |
| `SearchResult` | `models.py` | Search result with metadata |
| `Neo4jConfig` | `neo4j_config.py` | Database configuration |

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `process_input(items)` | `Dict[str, Any]` | Process new information with optimizations |
| `search(query, k=10, search_type="both")` | `QueryResponse` | Search with caching and safe accessors |
| `get_node_relations(node, source=None)` | `List[SearchResult]` | Get relations with optional source filtering |
| `analyze_conflicts(entity=None)` | `List[Dict]` | Detect relationship conflicts optimized |
| `find_paths(start, end, max_hops=4)` | `List[Dict]` | Find optimized relationship paths |
| `clear_all_data()` | `bool` | Clear all stored data and cache |
| `get_stats()` | `Dict[str, Any]` | Get system and optimization statistics |

## 🔍 Response Formats

### Processing Result
```python
{
    "processed_items": 3,
    "new_edges": 2,
    "updated_edges": 0, 
    "obsoleted_edges": 1,
    "duplicates_ignored": 0,
    "errors": [],
    "processing_time_ms": 850,  # 30% faster with optimizations
    "edge_results": [
        {"action": "created", "input_description": "..."},
        {"action": "obsoleted", "count": 1, "obsoleted_relationships": [...]}
    ]
}
```

### Search Response
```python
QueryResponse(
    results=[
        SearchResult(
            triplet=GraphTriplet(
                edge=GraphEdge(  # Now with safe accessors
                    edge_id="123",
                    metadata=EdgeMetadata(...)
                    # _subject, _relationship, _object lazy loaded
                )
            ),
            score=0.95,
            source="graph",  # "graph" or "vector"
            explanation="Optimized graph match for entity 'Alice'"
        )
    ],
    total_found=1,
    query_time_ms=15.2,  # Much faster with caching
    answer="Alice works as a software engineer at Google.",
    confidence=0.95
)
```

## 🛠️ Configuration

### Environment Variables
```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-nano

# Vector Store
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_TYPE=neo4j
```

### Programmatic Configuration
```python
from src.kg_engine.config import Neo4jConfig

# Custom Neo4j setup
config = Neo4jConfig(
    uri="bolt://your-server:7687",
    username="your-user",
    password="your-pass", 
    database="your-db"
)

# Initialize engine with config
engine = KnowledgeGraphEngineV2(
    neo4j_config=config,
    api_key="your-key",
    model="gpt-4"
)
```

## ⚠️ Error Handling

### Common Exceptions
- `ConnectionError`: Neo4j database connection issues
- `AuthenticationError`: Invalid Neo4j credentials
- `ValidationError`: Invalid input data format
- `LLMError`: OpenAI/Ollama API issues

### Exception Handling
```python
try:
    result = engine.process_input(items)
except ConnectionError:
    print("Neo4j connection failed")
except ValidationError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📊 Performance Guidelines

### Batch Processing
```python
# Efficient batch processing
large_dataset = [InputItem(description=text) for text in texts]

# Process in chunks
chunk_size = 50
for i in range(0, len(large_dataset), chunk_size):
    chunk = large_dataset[i:i+chunk_size]
    result = engine.process_input(chunk)
```

### Query Optimization
```python
# Use specific search types when possible
response = engine.search("Alice", search_type="direct")  # Faster for exact matches

# Leverage caching for repeated queries
response = engine.search("Who works at Google?")  # First call: ~100ms
response = engine.search("Who works at Google?")  # Cached: < 1ms

# Use safe accessors for robust data access
for result in response.results:
    edge = result.triplet.edge
    subject = edge.get_subject_safe() or "Unknown"
    relationship = edge.get_relationship_safe() or "Unknown"
    obj = edge.get_object_safe() or "Unknown"
    print(f"{subject} {relationship} {obj}")

# Filter by source if needed
relations = engine.get_node_relations("Alice", source="user_input")
```

## 🔗 Integration Examples

### With Web Applications
```python
from flask import Flask, jsonify, request

app = Flask(__name__)
engine = KnowledgeGraphEngineV2()

@app.route("/api/knowledge", methods=["POST"])
def add_knowledge():
    data = request.json
    items = [InputItem(description=item) for item in data["facts"]]
    result = engine.process_input(items)
    return jsonify(result)

@app.route("/api/search", methods=["GET"])
def search_knowledge():
    query = request.args.get("q")
    response = engine.search(query)
    return jsonify({
        "answer": response.answer,
        "results": len(response.results)
    })
```

### With Data Pipelines
```python
import pandas as pd

def process_csv_knowledge(csv_file):
    df = pd.read_csv(csv_file)
    
    items = []
    for _, row in df.iterrows():
        item = InputItem(
            description=row["description"],
            from_date=row.get("date"),
            metadata={"source": "csv_import"}
        )
        items.append(item)
    
    return engine.process_input(items)
```

For detailed method signatures and examples, see the individual module documentation.