# Quick Start Guide

Get up and running with Knowledge Graph Engine v2 in just a few minutes.

## 🆕 Version 2.1.0 Updates
- **Improved Search**: Better semantic understanding with dynamic thresholds
- **New Import Structure**: `from src.kg_engine import ...` (organized into submodules)
- **Enhanced Examples**: Biographical knowledge graph demonstrations

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

### 4. Explore Relationships

```python
# Get detailed information about entities
alice_info = engine.graph_db.get_entity_relationships("Alice")

print("Alice's relationships:")
for triplet in alice_info:
    edge = triplet.edge
    status = "ACTIVE" if not edge.metadata.obsolete else "OBSOLETE"
    print(f"  - {edge.subject} {edge.relationship} {edge.object} [{status}]")
```

## 🔍 Enhanced Search Capabilities (v2.1.0)

### Improved Semantic Understanding

```python
# The enhanced search now understands conceptual relationships
search_examples = [
    "Who works in technology?",      # Finds software engineers, developers
    "Who was born in Europe?",       # Recognizes European cities
    "What do people do for hobbies?" # Prioritizes "enjoys" relationships
]

for query in search_examples:
    response = engine.search(query)
    print(f"\nQ: {query}")
    print(f"A: {response.answer}")
    for result in response.results[:3]:
        edge = result.triplet.edge
        print(f"  - {edge.subject} {edge.relationship} {edge.object} (score: {result.score:.3f})")
```

## 🔄 Working with Updates and Conflicts

### Handle Changing Information

```python
# Add initial information
engine.process_input([InputItem(description="Alice lives in Boston")])

# Update with new information (automatically handles conflicts)
engine.process_input([InputItem(description="Alice moved to Seattle in 2024")])

# Check the results
alice_locations = engine.graph_db.find_edges(subject="Alice", relationship="LIVES_IN", filter_obsolete=False)

print("Alice's location history:")
for triplet in alice_locations:
    edge = triplet.edge
    status = "CURRENT" if not edge.metadata.obsolete else "PAST"
    print(f"  - Lives in {edge.object} [{status}]")
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

### 2. Semantic Vector Search

```python
# Find conceptually similar information
response = engine.search("software developer", search_type="semantic")
# Might find "Alice works as software engineer"
```

### 3. Hybrid Search (Recommended)

```python
# Combines both approaches for best results
response = engine.search("tech companies", search_type="both")
```

## 📊 Monitor System Health

```python
# Check system statistics
stats = engine.get_stats()
print(f"Total entities: {stats['graph_stats']['total_entities']}")
print(f"Active relationships: {stats['graph_stats']['active_edges']}")
print(f"Vector embeddings: {stats['vector_stats']['total_triplets']}")

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
# Check vector index status
from src.neo4j_schema import setup_neo4j_schema
setup_neo4j_schema()  # Recreates indexes if needed
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