# Knowledge Graph Engine REST API

A FastAPI-based REST API for the Knowledge Graph Engine v2, providing endpoints for processing natural language input and searching the knowledge graph with multi-tenant support.

## Features

- **Multi-tenant Support**: User ID (GUID) tracking for data isolation
- **Natural Language Processing**: Extract entities and relationships from text
- **Flexible Search**: Graph-based, vector-based, or hybrid search
- **Real-time Processing**: Async endpoints for better performance
- **Auto Documentation**: Interactive API docs at `/docs`

## Installation

```bash
# Install FastAPI dependencies
pip install -r src/api/requirements.txt

# Or install with main project
pip install -e .
```

## Running the API

### Option 1: Using the run script
```bash
python src/api/run_api.py
```

### Option 2: Direct with uvicorn
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: From project root
```bash
cd /path/to/project
python -m uvicorn src.api.main:app --reload
```

## Configuration

Environment variables:
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-api-key
```

## API Endpoints

### Health Check
```http
GET /health
```

Check API and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "engine_initialized": true,
  "version": "2.1.0"
}
```

### Process Input
```http
POST /process
```

Process natural language descriptions and extract relationships.

**Request Body:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "descriptions": [
    "Alice works as a software engineer at Google",
    "Bob lives in San Francisco"
  ],
  "metadata": {
    "source": "api_client",
    "session_id": "abc123"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "processed_items": 2,
  "new_edges": 3,
  "updated_edges": 0,
  "obsoleted_edges": 0,
  "processing_time_ms": 1250.5,
  "errors": []
}
```

### Search Knowledge Graph
```http
POST /search
```

Search the knowledge graph using natural language queries.

**Request Body:**
```json
{
  "query": "Who works in technology?",
  "search_type": "both",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "k": 10
}
```

**Search Types:**
- `graph`: Direct entity/relationship matching
- `vector`: Semantic similarity search
- `both`: Combined approach (recommended)

**Response:**
```json
{
  "query": "Who works in technology?",
  "search_type": "both",
  "answer": "Alice works as a software engineer at Google, which is in the technology industry.",
  "results": [
    {
      "subject": "Alice",
      "relationship": "works_as",
      "object": "software engineer",
      "confidence": 0.95,
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "metadata": {
        "summary": "Alice works as a software engineer at Google",
        "status": "active",
        "source": "api_client"
      }
    }
  ],
  "total_results": 1,
  "processing_time_ms": 145.3,
  "user_filter_applied": true
}
```

### Get Statistics
```http
GET /stats?user_id=123e4567-e89b-12d3-a456-426614174000
```

Get system statistics, optionally filtered by user.

**Response:**
```json
{
  "graph_stats": {
    "total_entities": 150,
    "total_edges": 342,
    "active_edges": 320,
    "obsolete_edges": 22
  },
  "vector_stats": {
    "total_triplets": 342,
    "collection_name": "kg_v2"
  },
  "filter_applied": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "note": "User-specific filtering requires metadata query implementation"
  }
}
```

## Usage Examples

### Python Client Example

```python
import requests
import json
from uuid import uuid4

# API base URL
BASE_URL = "http://localhost:8000"

# Create a user ID
user_id = str(uuid4())

# 1. Check health
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Process some information
process_data = {
    "user_id": user_id,
    "descriptions": [
        "Emma Johnson works as a data scientist at Microsoft",
        "Emma lives in Seattle and enjoys hiking",
        "John Smith is the CEO of TechCorp",
        "John graduated from MIT in 2010"
    ],
    "metadata": {
        "source": "python_client",
        "import_batch": "2024-01-01"
    }
}

response = requests.post(
    f"{BASE_URL}/process",
    json=process_data
)
result = response.json()
print(f"Processed {result['processed_items']} items")
print(f"Created {result['new_edges']} new relationships")

# 3. Search the knowledge graph
search_data = {
    "query": "Who works at Microsoft?",
    "search_type": "both",
    "user_id": user_id,
    "k": 5
}

response = requests.post(
    f"{BASE_URL}/search",
    json=search_data
)
search_result = response.json()
print(f"\nSearch Query: {search_result['query']}")
print(f"Answer: {search_result['answer']}")
print(f"Found {search_result['total_results']} results")

for result in search_result['results']:
    print(f"- {result['subject']} {result['relationship']} {result['object']}")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Process input
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "descriptions": [
      "Alice works at Google",
      "Bob is a friend of Alice"
    ]
  }'

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about Alice",
    "search_type": "both"
  }'

# Get stats
curl http://localhost:8000/stats?user_id=123e4567-e89b-12d3-a456-426614174000
```

### JavaScript/Fetch Example

```javascript
// Process input
const processInput = async (userId, descriptions) => {
  const response = await fetch('http://localhost:8000/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      descriptions: descriptions
    })
  });
  
  return await response.json();
};

// Search
const search = async (query, userId = null) => {
  const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      search_type: 'both',
      user_id: userId,
      k: 10
    })
  });
  
  return await response.json();
};

// Usage
const userId = '123e4567-e89b-12d3-a456-426614174000';

// Add knowledge
await processInput(userId, [
  'Sarah works as a designer at Apple',
  'Sarah graduated from RISD'
]);

// Search
const results = await search('Who works at Apple?', userId);
console.log(results.answer);
```

## Multi-Tenant Usage

The API supports multi-tenant scenarios through user ID tracking:

1. **Data Isolation**: Each user's data is tagged with their UUID
2. **Filtered Search**: Optional filtering by user ID in search queries
3. **User Statistics**: Per-user statistics and analytics

### Best Practices

1. **Always provide user_id** when processing input
2. **Use consistent UUIDs** for the same user across sessions
3. **Filter searches by user_id** for tenant isolation
4. **Monitor per-user usage** for billing/quotas

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid input)
- `401`: Unauthorized (if auth is enabled)
- `404`: Not found
- `500`: Internal server error
- `503`: Service unavailable (engine not initialized)

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Performance Tips

1. **Batch Processing**: Send multiple descriptions in one request
2. **Limit Results**: Use appropriate `k` values for search
3. **Search Type**: Use `graph` for exact matches, `vector` for semantic search
4. **Caching**: Implement client-side caching for repeated queries

## Docker Deployment

See [Docker README](./docker/README.md) for containerized deployment instructions.

## API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc

## License

MIT License - See project LICENSE file