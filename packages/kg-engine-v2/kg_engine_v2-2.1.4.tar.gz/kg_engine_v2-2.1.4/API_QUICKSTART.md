# Knowledge Graph Engine API - Quick Start

## 🚀 Start the API in 3 Steps

### Option 1: Local Development

1. **Start Neo4j**
   ```bash
   docker run --name neo4j -p7474:7474 -p7687:7687 -d \
       -e NEO4J_AUTH=neo4j/password \
       neo4j:latest
   ```

2. **Install Dependencies**
   ```bash
   pip install -e .
   pip install -r src/api/requirements.txt
   ```

3. **Run the API**
   ```bash
   python src/api/run_api.py
   ```

### Option 2: Docker Compose (Recommended)

1. **Start Everything**
   ```bash
   docker-compose up -d
   ```

That's it! The API will be available at http://localhost:8000

## 📖 Explore the API

- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Quick Test

```bash
# Test the API
python src/api/test_api.py
```

## 💡 First API Call

```bash
# Health check
curl http://localhost:8000/health

# Process some knowledge
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "descriptions": [
      "Alice works as a software engineer at Google",
      "Bob lives in San Francisco"
    ]
  }'

# Search the knowledge graph
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who works at Google?",
    "search_type": "both"
  }'
```

## 📚 Full Documentation

See [API README](src/api/README.md) for complete documentation and examples.