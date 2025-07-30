# KG Engine API Server

A standalone FastAPI application that demonstrates how to use the `kg_engine` package as an external dependency to build powerful knowledge graph applications.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Neo4j 5.x running locally or remotely
- OpenAI API key (optional, for LLM features)

### Installation

1. **Install the KG Engine package** (from the parent directory):
   ```bash
   cd ..
   pip install -e .
   ```

2. **Install API server dependencies**:
   ```bash
   cd kg_api_server
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

4. **Start the server**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

   Or run directly:
   ```bash
   python app/main.py
   ```

### Access the API

- **API Documentation**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

## 📖 API Endpoints

### Core Operations

- `POST /process` - Process natural language texts and extract relationships
- `POST /search` - Search the knowledge graph with hybrid search
- `GET /stats` - Get comprehensive system statistics

### CRUD Operations

- `POST /edges` - Create new edges manually
- `GET /nodes/{node_name}/relations` - Get all relations for a node

### Advanced Features

- `POST /nodes/merge` - Merge nodes with auto/manual strategies

## 🔧 Usage Examples

### Process Natural Language Text

```bash
curl -X POST "http://localhost:8080/process" \
     -H "Content-Type: application/json" \
     -d '{
       "texts": [
         "Alice works as a software engineer at Google",
         "Bob moved to San Francisco last year"
       ],
       "source": "api_demo"
     }'
```

### Search the Knowledge Graph

```bash
curl -X POST "http://localhost:8080/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Who works in technology?",
       "search_type": "hybrid",
       "limit": 10
     }'
```

### Create Manual Edge

```bash
curl -X POST "http://localhost:8080/edges" \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "John",
       "relationship": "WORKS_AT",
       "object": "Microsoft",
       "summary": "John works at Microsoft as a product manager",
       "confidence": 0.95
     }'
```

### Merge Nodes

```bash
curl -X POST "http://localhost:8080/nodes/merge" \
     -H "Content-Type: application/json" \
     -d '{
       "source_node": "John Smith",
       "target_node": "John",
       "merge_type": "auto"
     }'
```

## 🏗️ Architecture

This API server demonstrates the **external usage pattern** for the KG Engine:

```python
# Import as external package
from kg_engine import (
    KnowledgeGraphEngineV2, InputItem, Neo4jConfig,
    EdgeData, EdgeMetadata, parse_date
)

# Initialize and use
config = Neo4jConfig(uri="bolt://localhost:7687", ...)
engine = KnowledgeGraphEngineV2(api_key="...", neo4j_config=config)
```

### Key Features Demonstrated

- ✅ **Complete CRUD operations** for edges and nodes
- ✅ **Semantic search** with hybrid graph/vector search
- ✅ **Natural language processing** with LLM integration
- ✅ **Node merging** with automatic and manual strategies
- ✅ **Real-time statistics** and monitoring
- ✅ **Full Neo4j integration** with optimized queries
- ✅ **Production-ready** error handling and logging

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8080` |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` |
| `OPENAI_API_KEY` | OpenAI API key | Required for LLM features |
| `OPENAI_MODEL` | OpenAI model | `gpt-4o-mini` |

### Neo4j Setup

1. **Install Neo4j**: https://neo4j.com/download/
2. **Start Neo4j**: `neo4j start`
3. **Access Browser**: http://localhost:7474
4. **Set password** for the `neo4j` user

## 🧪 Testing

### Run API Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Manual Testing

```bash
# Check health
curl http://localhost:8080/health

# Get statistics
curl http://localhost:8080/stats

# Test with example data
python test_api_client.py
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t kg-api-server .
```

### Run Container

```bash
docker run -p 8080:8080 \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  -e NEO4J_PASSWORD=your_password \
  -e OPENAI_API_KEY=your_key \
  kg-api-server
```

### Docker Compose

```yaml
version: '3.8'
services:
  kg-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_PASSWORD=password
      - OPENAI_API_KEY=your_key
    depends_on:
      - neo4j
  
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
```

## 📚 API Reference

### Request/Response Models

All API endpoints use Pydantic models for validation:

- `ProcessTextRequest/Response` - Text processing operations
- `SearchRequest/Response` - Knowledge graph search
- `CreateEdgeRequest` - Manual edge creation
- `NodeMergeRequest` - Node merging operations

See the interactive documentation at `/docs` for complete schemas.

### Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation error)
- `500` - Internal Server Error
- `503` - Service Unavailable (engine not initialized)

## 🔍 Monitoring

### Health Checks

The `/health` endpoint provides comprehensive status:

```json
{
  "status": "healthy",
  "kg_engine_version": "2.1.0",
  "neo4j_connected": true,
  "engine_initialized": true
}
```

### Statistics

The `/stats` endpoint provides system metrics:

```json
{
  "graph_statistics": {
    "total_relationships": 1250,
    "total_entities": 543
  },
  "vector_statistics": {...},
  "kg_engine_version": "2.1.0"
}
```

## 🤝 Contributing

This API server serves as a reference implementation. To contribute:

1. Fork the main KG Engine repository
2. Make changes to the core package in `/src`
3. Update this API server to demonstrate new features
4. Submit a pull request

## 📄 License

MIT License - see the main KG Engine repository for details.

## 🆘 Support

- **Documentation**: See `/docs` in the main repository
- **Issues**: Report bugs in the main KG Engine repository
- **API Docs**: Visit `/docs` when the server is running

---

**This is a demonstration project showing how to use KG Engine v2 as an external package.**