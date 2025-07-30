# Using KG Engine as External Package

This guide explains how to use the Knowledge Graph Engine v2 as an external dependency in your own projects.

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd kg-engine-v2

# Install in development mode
pip install -e .

# Or install with all optional dependencies
pip install -e ".[all]"
```

### From PyPI (when published)

```bash
pip install kg-engine-v2
```

## Available Imports

The KG Engine exports all necessary components for external use:

```python
from kg_engine import (
    # Core Components
    KnowledgeGraphEngineV2,      # Main engine class
    InputItem,                   # Input data structure
    GraphEdge,                   # Edge representation
    EdgeMetadata,                # Edge metadata
    GraphTriplet,                # Subject-Relationship-Object
    EdgeData,                    # Edge creation data
    SearchResult,                # Search result structure
    QueryResponse,               # Query response wrapper
    ExtractedInfo,               # Extracted relationship info
    ParsedQuery,                 # Parsed query structure
    
    # Enums
    RelationshipStatus,          # ACTIVE, OBSOLETE
    SearchType,                  # DIRECT, SEMANTIC, BOTH
    QueryType,                   # Query optimization types
    
    # Configuration
    Neo4jConfig,                 # Database configuration
    Neo4jSchemaManager,          # Schema management
    setup_neo4j_schema,          # Schema setup function
    
    # Storage (Advanced)
    VectorStore,                 # Vector storage interface
    GraphDB,                     # Graph database interface
    
    # LLM (Advanced)
    LLMInterface,                # LLM integration
    
    # Utilities
    parse_date,                  # Date parsing utility
    GraphQueryOptimizer,         # Query optimization
    Neo4jOptimizer,              # Neo4j-specific optimization
    ClassifierDetector,          # Edge classification
    ClassifierMap,               # Category management
    
    # Version
    __version__                  # Package version
)
```

## Basic Usage

### 1. Initialize the Engine

```python
from kg_engine import KnowledgeGraphEngineV2, Neo4jConfig

# Configure Neo4j connection
config = Neo4jConfig(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password",
    database="neo4j"  # Optional, defaults to "neo4j"
)

# Create engine instance
engine = KnowledgeGraphEngineV2(
    api_key="your-openai-key",  # Or "ollama" for local LLM
    model="gpt-4o-mini",
    neo4j_config=config
)
```

### 2. Process Natural Language

```python
from kg_engine import InputItem

# Create input items
items = [
    InputItem(
        description="Alice works as a software engineer at Google",
        metadata={"source": "resume", "confidence": 0.95}
    ),
    InputItem(
        description="Bob graduated from MIT in 2020",
        metadata={"source": "linkedin"}
    )
]

# Process items
result = engine.process_input(items)

print(f"Created {result['new_edges']} new relationships")
print(f"Updated {result['updated_edges']} existing relationships")
```

### 3. Search the Graph

```python
from kg_engine import SearchType

# Natural language search
response = engine.search(
    query="Who works in technology?",
    search_type=SearchType.BOTH,  # Hybrid search
    k=10  # Top 10 results
)

# Access results
print(f"Answer: {response.answer}")
for result in response.results:
    edge = result.triplet.edge
    print(f"{edge.get_subject_safe()} {edge.get_relationship_safe()} {edge.get_object_safe()}")
```

### 4. Direct Edge Creation

```python
from kg_engine import EdgeData, EdgeMetadata, RelationshipStatus, parse_date

# Create edge metadata
metadata = EdgeMetadata(
    summary="John is the CTO of TechCorp",
    confidence=0.95,
    source="manual_entry",
    category="business",
    from_date=parse_date("January 2023"),
    status=RelationshipStatus.ACTIVE
)

# Create edge
edge_data = EdgeData(
    subject="John",
    relationship="WORKS_AS",
    object="CTO at TechCorp",
    metadata=metadata
)

# Add to graph (direct access)
success = engine.graph_db.add_edge_data(edge_data)
```

## Advanced Usage

### Custom Configuration

```python
import os
from kg_engine import KnowledgeGraphEngineV2, Neo4jConfig

# Load from environment
config = Neo4jConfig(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)

# Use Ollama for local LLM
engine = KnowledgeGraphEngineV2(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3.2:3b",
    neo4j_config=config
)
```

### Error Handling

```python
from kg_engine import KnowledgeGraphEngineV2
from kg_engine.exceptions import (
    DuplicateEdgeError,
    InvalidNodeError,
    Neo4jConnectionError
)

try:
    engine = KnowledgeGraphEngineV2(...)
    result = engine.process_input(items)
except Neo4jConnectionError:
    print("Failed to connect to Neo4j")
except DuplicateEdgeError:
    print("Edge already exists")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Direct Database Access

For advanced operations, access the database directly:

```python
# Get statistics
stats = engine.get_stats()
print(f"Total relationships: {stats['graph_stats']['total_relationships']}")

# Direct graph queries
with engine.graph_db.driver.session() as session:
    result = session.run(
        "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10"
    )
    for record in result:
        print(record)

# Node operations
relations = engine.get_node_relations(
    node_name="Alice",
    max_depth=2,
    filter_obsolete=True
)
```

## Example: Building a Personal Assistant

```python
from kg_engine import (
    KnowledgeGraphEngineV2, 
    InputItem, 
    Neo4jConfig,
    SearchType
)

class PersonalAssistant:
    def __init__(self):
        self.engine = KnowledgeGraphEngineV2(
            api_key="your-key",
            neo4j_config=Neo4jConfig()
        )
    
    def remember(self, fact: str):
        """Remember a fact"""
        result = self.engine.process_input([
            InputItem(fact, metadata={"source": "user"})
        ])
        return f"Remembered: {result['new_edges']} new facts"
    
    def recall(self, question: str):
        """Recall information"""
        response = self.engine.search(
            query=question,
            search_type=SearchType.BOTH
        )
        return response.answer or "I don't know that yet"
    
    def forget(self, about: str):
        """Forget information about something"""
        # Mark relationships as obsolete
        relations = self.engine.get_node_relations(about)
        for rel in relations:
            edge_id = rel.triplet.edge.edge_id
            self.engine.graph_db.mark_edge_obsolete(edge_id)
        return f"Forgot {len(relations)} facts about {about}"

# Usage
assistant = PersonalAssistant()
assistant.remember("My birthday is May 15th")
assistant.remember("I prefer coffee over tea")
print(assistant.recall("When is my birthday?"))
```

## REST API Usage

If you prefer REST API over programmatic access:

```python
import requests

class KGEngineClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def process_text(self, texts):
        response = requests.post(
            f"{self.base_url}/process",
            json={"texts": texts}
        )
        return response.json()
    
    def search(self, query):
        response = requests.post(
            f"{self.base_url}/search",
            json={"query": query}
        )
        return response.json()
```

## Complete Example Project

See the `kg_api_server/` directory for a complete FastAPI project that uses the KG Engine as an external dependency.

## Type Hints and IDE Support

The package includes comprehensive type hints for better IDE support:

```python
from kg_engine import KnowledgeGraphEngineV2, InputItem, QueryResponse

def process_knowledge(engine: KnowledgeGraphEngineV2, facts: list[str]) -> QueryResponse:
    """Process facts and return search results"""
    items = [InputItem(fact) for fact in facts]
    engine.process_input(items)
    return engine.search("What do we know?")
```

## Best Practices

1. **Connection Management**: Reuse engine instances
2. **Batch Processing**: Process multiple items together
3. **Error Handling**: Always handle potential failures
4. **Resource Cleanup**: Engine handles cleanup automatically
5. **Configuration**: Use environment variables for credentials

## Troubleshooting

### Import Errors

```python
# If imports fail, check installation
import sys
print(sys.path)
print("Looking for kg_engine...")

try:
    import kg_engine
    print(f"Found kg_engine version {kg_engine.__version__}")
except ImportError as e:
    print(f"Import failed: {e}")
```

### Connection Issues

```python
# Test Neo4j connection
from kg_engine import Neo4jConfig

config = Neo4jConfig()
if config.verify_connectivity():
    print("Neo4j connection successful")
else:
    print("Failed to connect to Neo4j")
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Now engine operations will show detailed logs
engine = KnowledgeGraphEngineV2(...)
```