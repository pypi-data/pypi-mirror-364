# Quick Start Guide

Get up and running with Knowledge Graph Engine v2 in just a few minutes.

## 🆕 Version 2.1.0 Updates
- **Performance Optimizations**: 50-74% faster queries with advanced optimization
- **Smart Caching**: Query result caching with 5-minute TTL for near-instant repeated queries
- **GraphEdge Refactoring**: Lazy loading with safe accessors, 18% smaller codebase
- **Dynamic Relationships**: WORKS_AT, LIVES_IN instead of generic RELATES_TO
- **Safe Data Access**: Robust error handling prevents "Relationship not populated" errors
- **Enhanced Examples**: Comprehensive test suite with relationship fix validation

## 🚀 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **Neo4j 5.x** running (local or remote)
- **OpenAI API key** (optional, for LLM features)

## 📦 Installation

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd kg-engine-v2

# Install dependencies
pip install -e .

# Or install specific requirements
pip install neo4j>=5.0.0 sentence-transformers>=2.2.0 openai>=1.0.0 python-dotenv>=1.0.0
```

### 2. Set Up Neo4j

**Option A: Local Neo4j**
```bash
# Download and start Neo4j Desktop or Docker
docker run --name neo4j -p7474:7474 -p7687:7687 -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

**Option B: Neo4j Aura (Cloud)**
1. Create account at [neo4j.com/aura](https://neo4j.com/aura)
2. Create new database instance
3. Note connection details

### 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# Optional: OpenAI for LLM features
OPENAI_API_KEY=your-openai-api-key

# Optional: Ollama for local LLM
OLLAMA_BASE_URL=http://localhost:11434/v1
EOF
```

## 🎯 Basic Usage

### 1. Initialize the Engine

```python
from src.kg_engine import KnowledgeGraphEngineV2, InputItem
from src.kg_engine.config import Neo4jConfig

# Initialize Neo4j configuration
neo4j_config = Neo4jConfig()

# Create the engine
engine = KnowledgeGraphEngineV2(
    api_key="your-openai-api-key",  # or "ollama" for local LLM
    vector_store_type="neo4j",
    neo4j_config=neo4j_config
)

print("✅ Engine initialized successfully!")
```

### 2. Add Your First Knowledge

```python
# Add some facts about people and organizations
facts = [
    InputItem(description="Alice works as a software engineer at Google"),
    InputItem(description="Bob lives in San Francisco"),
    InputItem(description="Charlie is the CEO of Microsoft"),
    InputItem(description="Alice graduated from MIT in 2020")
]

# Process the facts (extracts entities and relationships automatically)
for fact in facts:
    result = engine.process_input([fact])
    print(f"Added {result['new_edges']} new relationships")
```

### 3. Search Your Knowledge Graph

```python
# Ask questions in natural language
queries = [
    "Who works at Google?",
    "Where does Bob live?", 
    "What companies are mentioned?",
    "Tell me about Alice"
]

for query in queries:
    response = engine.search(query)
    print(f"\nQ: {query}")
    print(f"A: {response.answer}")
    print(f"Found {len(response.results)} related facts")
```

### 4. Explore Relationships (Optimized)

```python
# Get detailed information about entities using optimized methods
alice_info = engine.get_node_relations("Alice", filter_obsolete=True)

print("Alice's relationships:")
for result in alice_info:
    edge = result.triplet.edge
    # Use safe accessors to prevent errors
    subject = edge.get_subject_safe() or "Unknown"
    relationship = edge.get_relationship_safe() or "Unknown"
    obj = edge.get_object_safe() or "Unknown"
    status = "ACTIVE" if not edge.metadata.obsolete else "OBSOLETE"
    print(f"  - {subject} {relationship} {obj} [{status}]")

# Optional: Filter by source
alice_user_info = engine.get_node_relations("Alice", source="user_input")
print(f"Alice has {len(alice_user_info)} relationships from user input")
```

## 🔍 Optimized Search Performance (v2.1.0)

### Fast Cached Queries

```python
# First query: ~100ms, subsequent queries: < 1ms (cached)
query = "Who works in technology?"

# First call
start_time = time.time()
response1 = engine.search(query)
first_time = (time.time() - start_time) * 1000
print(f"First search: {first_time:.1f}ms")

# Cached call
start_time = time.time()
response2 = engine.search(query)
cached_time = (time.time() - start_time) * 1000
print(f"Cached search: {cached_time:.1f}ms ({first_time/cached_time:.0f}x faster)")

# Safe data access (no more "Relationship not populated" errors)
for result in response1.results[:3]:
    edge = result.triplet.edge
    subject = edge.get_subject_safe() or "Unknown"
    relationship = edge.get_relationship_safe() or "Unknown"
    obj = edge.get_object_safe() or "Unknown"
    print(f"  - {subject} {relationship} {obj} (score: {result.score:.3f})")
```

### Enhanced Semantic Understanding

```python
# The enhanced search now understands conceptual relationships
search_examples = [
    "Who works in technology?",      # Finds software engineers, developers
    "Who was born in Europe?",       # Recognizes European cities
    "What do people do for hobbies?" # Prioritizes "enjoys" relationships
]

for query in search_examples:
    response = engine.search(query)
    print(f"\nQ: {query} (Query time: {response.query_time_ms:.1f}ms)")
    print(f"A: {response.answer}")
    print(f"Confidence: {response.confidence:.2f}")
```

## 🔄 Working with Updates and Conflicts

### Handle Changing Information with Conflict Analysis

```python
# Add initial information
engine.process_input([InputItem(description="Alice lives in Boston")])

# Update with new information (automatically handles conflicts)
result = engine.process_input([InputItem(description="Alice moved to Seattle in 2024")])
print(f"Processing result: {result['obsoleted_edges']} relationships obsoleted")

# Use optimized conflict analysis
conflicts = engine.analyze_conflicts(entity_name="Alice", relationship_type="LIVES_IN")
print(f"Found {len(conflicts)} potential conflicts for Alice's location")

# Check the results with safe accessors
alice_locations = engine.get_node_relations("Alice")
print("Alice's location history:")
for result in alice_locations:
    edge = result.triplet.edge
    if edge.get_relationship_safe() == "LIVES_IN":
        obj = edge.get_object_safe() or "Unknown"
        status = "CURRENT" if not edge.metadata.obsolete else "PAST"
        print(f"  - Lives in {obj} [{status}]")
```

### Handle Negations

```python
# Remove relationships with natural language
engine.process_input([InputItem(description="Alice no longer works at Google")])

# The system automatically finds and obsoletes matching relationships
```

## 🔍 Advanced Search Features

### 1. Direct Graph Search

```python
# Find exact matches in the graph
response = engine.search("Alice", search_type="direct")
```

### 2. Optimized Semantic Vector Search

```python
# Find conceptually similar information with caching
response = engine.search("software developer", search_type="semantic")
# Might find "Alice works as software engineer"
print(f"Vector search completed in {response.query_time_ms:.1f}ms")

# Safe data access
for result in response.results:
    edge = result.triplet.edge
    subject = edge.get_subject_safe()
    relationship = edge.get_relationship_safe()
    obj = edge.get_object_safe()
    if subject and relationship and obj:
        print(f"Found: {subject} {relationship} {obj}")
```

### 3. Hybrid Search (Recommended)

```python
# Combines both approaches for best results
response = engine.search("tech companies", search_type="both")
```

## 📊 Monitor System Health

```python
# Check system statistics (including optimization stats)
stats = engine.get_stats()
print(f"Total entities: {stats['graph_stats']['total_entities']}")
print(f"Active relationships: {stats['graph_stats']['active_edges']}")
print(f"Vector embeddings: {stats['vector_stats']['total_triplets']}")

# New: Check optimization performance
if 'optimization_stats' in stats:
    opt_stats = stats['optimization_stats']
    print(f"\nOptimization Performance:")
    print(f"  Cache hit rate: {opt_stats.get('cache_hit_rate', 0):.1%}")
    print(f"  Average query time: {opt_stats.get('avg_query_time_ms', 0):.1f}ms")
    print(f"  Queries cached: {opt_stats.get('cached_queries', 0)}")

# Verify Neo4j connection
from src.kg_engine.config import Neo4jConfig
config = Neo4jConfig()
if config.verify_connectivity():
    print("✅ Neo4j connection healthy")
else:
    print("❌ Neo4j connection issue")
```

## 🧪 Run Examples

```python
# Run the included examples
python src/examples/examples.py

# Run biographical knowledge graph demo
python src/examples/bio_example.py

# Run simple biographical demo
python src/examples/simple_bio_demo.py
```

Expected output:
```
✅ Neo4j connection verified
🤖 LLM Interface initialized: gpt-4.1-nano via OpenAI
🚀 Knowledge Graph Engine v2 initialized
   - Vector store: kg_v2 (neo4j)
   - Graph database: Neo4j (persistent)
   - LLM interface: gpt-4.1-nano via OpenAI

=== Example: Semantic Relationship Handling ===
1. Adding: John Smith teaches at MIT
   Result: 1 new edge(s) created
...
```

## 🛠️ Configuration Options

### Environment Variables

```bash
# Neo4j Settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# LLM Settings  
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-nano

# Ollama Settings (alternative to OpenAI)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2:3b

# Vector Store Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_TYPE=neo4j

# Performance Tuning
NEO4J_POOL_SIZE=10
QUERY_TIMEOUT=30
```

### Code Configuration

```python
from src.kg_engine.config import Neo4jConfig

# Custom Neo4j configuration
config = Neo4jConfig(
    uri="bolt://your-neo4j-server:7687",
    username="your-username", 
    password="your-password",
    database="your-database"
)

# Custom engine settings
engine = KnowledgeGraphEngineV2(
    api_key="your-api-key",
    model="gpt-4",
    vector_collection="custom_collection",
    neo4j_config=config
)
```

## 🚨 Troubleshooting

### Common Issues

**1. Neo4j Connection Failed**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Test connection
python -c "from src.kg_engine.config import Neo4jConfig; print('✅' if Neo4jConfig().verify_connectivity() else '❌')"
```

**2. LLM API Issues**
```python
# Use Ollama as fallback
engine = KnowledgeGraphEngineV2(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3.2:3b"
)
```

**3. Vector Index Issues**
```python
# Check vector index status and performance indexes
from src.kg_engine.config.neo4j_schema import setup_neo4j_schema
setup_neo4j_schema()  # Recreates indexes if needed

# Verify performance indexes
print("Creating performance indexes...")
engine.graph_db._ensure_performance_indexes()
print("Performance indexes verified")
```

**4. "Relationship not populated" Errors**
```python
# Always use safe accessors to prevent errors
edge = result.triplet.edge
if edge.has_graph_data():
    subject, relationship, obj = edge.get_graph_data()
else:
    subject = edge.get_subject_safe() or "Unknown"
    relationship = edge.get_relationship_safe() or "Unknown"
    obj = edge.get_object_safe() or "Unknown"

print(f"Safe access: {subject} {relationship} {obj}")
```

## 🎓 Next Steps

- **Learn More**: Check out [Configuration Guide](./configuration.md)
- **See Examples**: Review [Usage Examples](./examples.md)
- **Best Practices**: Read [Best Practices](./best-practices.md)
- **API Reference**: Explore [API Documentation](../api/README.md)
- **Architecture**: Understand [System Architecture](../architecture/overview.md)

## 💡 Tips for Success

1. **Start Simple**: Begin with basic facts and gradually add complexity
2. **Monitor Performance**: Keep an eye on query times and memory usage
3. **Use Descriptive Text**: More context helps with better relationship extraction
4. **Regular Backups**: Neo4j data should be backed up regularly
5. **Experiment**: Try different search types to see what works best for your use case

Ready to build your knowledge graph? Let's go! 🚀