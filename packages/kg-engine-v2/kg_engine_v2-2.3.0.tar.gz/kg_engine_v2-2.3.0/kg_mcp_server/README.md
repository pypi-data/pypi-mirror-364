# KG Engine MCP Server

A Model Context Protocol (MCP) server that provides Claude and other AI assistants with direct access to the Knowledge Graph Engine. This server uses FastMCP with SSE transport for efficient communication.

## 🚀 Quick Start

### Prerequisites

- Docker installed on your system
- Neo4j database (local or cloud)
- OpenAI API key or compatible LLM endpoint

### Option 1: Standalone Docker (Recommended)

Build and run the MCP server as a standalone container:

```bash
# Clone the repository and navigate to the MCP server directory
git clone <repository-url>
cd llama_neo4j_demo/kg_mcp_server

# Build the Docker image (from parent directory)
cd ..
docker build -f kg_mcp_server/Dockerfile -t kg-mcp-server .
cd kg_mcp_server

# Run the container with your configuration
docker run -d \
  --name kg-mcp-server \
  -p 3000:3000 \
  -e NEO4J_URI="bolt://your-neo4j-host:7687" \
  -e NEO4J_USERNAME="neo4j" \
  -e NEO4J_PASSWORD="your-password" \
  -e NEO4J_DATABASE="neo4j" \
  -e OPENAI_API_KEY="your-openai-key" \
  kg-mcp-server

# Check if the server is running
docker logs kg-mcp-server
```

### Option 2: Docker with Neo4j

If you need a local Neo4j instance, use docker-compose:

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# NEO4J_PASSWORD=your-secure-password
# OPENAI_API_KEY=your-openai-key

# Start both Neo4j and MCP server
docker-compose up -d

# View logs
docker-compose logs -f mcp-server
```

### Option 3: Development Setup

For local development without Docker:

```bash
# Install KG Engine from parent directory
cd ..
pip install -e .

# Return to MCP server directory and install dependencies
cd kg_mcp_server
pip install -r requirements.txt

# Set environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_PASSWORD="password"
export OPENAI_API_KEY="your-key"

# Run the server
python server.py
```

## 🤖 Claude Desktop Configuration

### 1. Start the MCP Server

Choose one of the options above to start the server. The server will be available at:
- **URL**: `http://localhost:3000`
- **SSE Endpoint**: `http://localhost:3000/sse`

### 2. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the KG Engine MCP server configuration:

```json
{
  "mcpServers": {
    "kg-engine": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## 📚 Available Tools

The MCP server provides 11 comprehensive tools for knowledge graph operations:

### Knowledge Processing
- **`process_text`** - Process natural language to extract and store knowledge
- **`search`** - Search the graph using natural language queries

### Node Operations
- **`get_node`** - Retrieve all relationships for a specific entity
- **`update_node`** - Update properties of an existing node
- **`delete_node`** - Delete a node (with cascade options)
- **`merge_nodes`** - AI-powered merge of duplicate entities

### Edge Operations
- **`create_edge`** - Create relationships between entities
- **`get_edges`** - Get all relationships for a node
- **`update_edge`** - Update relationship properties and status
- **`delete_edge`** - Delete specific relationships

### System
- **`get_stats`** - Get knowledge graph statistics

Each tool includes comprehensive parameter validation, descriptions, and examples designed to be easily understood by AI assistants.

## 💬 Example Usage

### Building Knowledge
```
Human: Store this information: "Alice works at Google as a senior engineer. She reports to Bob who is the engineering manager."

Claude: I'll store this team information in the knowledge graph using the process_text tool.

[Uses process_text tool]

Successfully stored the information about Alice and Bob, including their roles at Google and reporting relationship.
```

### Querying Knowledge
```
Human: Who works at Google?

Claude: Let me search the knowledge graph for people who work at Google.

[Uses search tool]

Based on the knowledge graph: Alice works at Google as a senior engineer, and Bob works at Google as an engineering manager.
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` | Yes |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` | Yes |
| `NEO4J_PASSWORD` | Neo4j password | `password` | Yes |
| `NEO4J_DATABASE` | Neo4j database name | `neo4j` | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `LLM_BASE_URL` | Custom LLM endpoint | - | No |
| `LLM_BEARER_KEY` | Custom LLM API key | - | No |
| `OPENAI_MODEL` | Model name | `gpt-4o-mini` | No |

*Either `OPENAI_API_KEY` or both `LLM_BASE_URL` and `LLM_BEARER_KEY` are required.

### Docker Environment File

Create a `.env` file for docker-compose:

```bash
# Neo4j Configuration
NEO4J_PASSWORD=your-secure-password

# LLM Configuration (choose one)
OPENAI_API_KEY=your-openai-key
# OR
LLM_BASE_URL=https://your-llm-endpoint.com
LLM_BEARER_KEY=your-llm-key

# Optional
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

## 🐳 Docker Details

### Standalone Dockerfile

The provided Dockerfile creates a self-contained image that includes:
- Python 3.11 runtime
- KG Engine package installed from source
- MCP server dependencies
- Non-root user for security
- All necessary environment variable support

### Build Arguments

Build the image from the parent directory:

```bash
# From the parent directory of kg_mcp_server
docker build -f kg_mcp_server/Dockerfile -t kg-mcp-server .

# Or use environment variables at runtime (recommended for security)
docker run -d \
  --name kg-mcp-server \
  -p 3000:3000 \
  --env-file kg_mcp_server/.env \
  kg-mcp-server
```

### Health Checking

To check if your server is running properly:

```bash
# Check container status
docker ps

# View logs
docker logs kg-mcp-server

# Test the server endpoint
curl http://localhost:3000/sse
```

## 🛠️ Development

### Local Development

For development with automatic reloading:

```bash
# Install in development mode
cd ..
pip install -e .
cd kg_mcp_server

# Install dev dependencies
pip install -r requirements.txt

# Set debug logging
export LOG_LEVEL=DEBUG

# Run the server
python server.py
```

### Testing Tools

Test individual tools programmatically:

```python
import requests

# Test the SSE endpoint
response = requests.get("http://localhost:3000/sse")
print(f"Server status: {response.status_code}")

# The MCP tools are accessible through Claude Desktop
# or other MCP-compatible clients
```

## 🆘 Troubleshooting

### Common Issues

1. **"Failed to connect to Neo4j"**
   ```bash
   # Check Neo4j is running and accessible
   docker logs neo4j  # if using docker-compose
   # Verify credentials and connection string
   ```

2. **"Failed to import kg_engine"**
   ```bash
   # Ensure KG Engine is installed
   cd .. && pip install -e .
   ```

3. **Claude not connecting**
   ```bash
   # Verify server is running
   curl http://localhost:3000/sse
   # Check Claude Desktop config path
   # Restart Claude Desktop after config changes
   ```

4. **Docker build fails**
   ```bash
   # Clean build with no cache (run from parent directory)
   cd .. && docker build --no-cache -f kg_mcp_server/Dockerfile -t kg-mcp-server .
   
   # Check if setup.py exists in parent directory
   ls setup.py src/
   ```

### Quick Diagnosis

```bash
# Check server status
docker ps | grep kg-mcp-server

# View server logs
docker logs kg-mcp-server

# Test server response
curl -v http://localhost:3000/sse
```

### Performance Tips

- Use SSD storage for Neo4j data volumes
- Allocate sufficient memory to Neo4j (see docker-compose.yml)
- Monitor server logs for connection issues
- Use connection pooling for high-load scenarios

## 📄 License

MIT License - Same as KG Engine v2