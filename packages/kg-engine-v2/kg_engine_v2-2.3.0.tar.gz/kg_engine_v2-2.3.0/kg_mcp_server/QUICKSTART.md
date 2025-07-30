# KG Engine MCP Server - Quick Start Guide

Get up and running with the KG Engine MCP Server in under 5 minutes.

## Prerequisites

- Docker installed and running
- Neo4j database (local or cloud)
- OpenAI API key or compatible LLM endpoint

## Option 1: Automated Setup (Recommended)

```bash
# 1. Navigate to the MCP server directory
cd kg_mcp_server

# 2. Run the automated build and run script
./build-and-run.sh
```

The script will:
- Check if Docker is running
- Create `.env` from template if needed
- Build the Docker image
- Start the container
- Provide Claude Desktop configuration

## Option 2: Manual Setup

### Step 1: Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit with your settings
nano .env
```

Required settings in `.env`:
```bash
NEO4J_PASSWORD=your-secure-password
OPENAI_API_KEY=your-openai-key
```

### Step 2: Build and Run

```bash
# Build the image (from parent directory)
cd .. && docker build -f kg_mcp_server/Dockerfile -t kg-mcp-server . && cd kg_mcp_server

# Run the container
docker run -d \
  --name kg-mcp-server \
  -p 3000:3000 \
  --env-file .env \
  kg-mcp-server
```

### Step 3: Verify

```bash
# Check if running
docker ps | grep kg-mcp-server

# View logs
docker logs kg-mcp-server

# Test endpoint
curl http://localhost:3000/sse
```

## Option 3: With Local Neo4j

If you need a local Neo4j database:

```bash
# Edit .env to use local Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_PASSWORD=password

# Start with docker-compose (includes Neo4j)
docker-compose up -d
```

## Claude Desktop Setup

1. **Location of config file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "kg-engine": {
         "url": "http://localhost:3000/sse"
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Test with Claude

Try these example conversations:

### Store Knowledge
```
Human: Store this information: "Alice works at Google as a senior engineer. She reports to Bob who is the engineering manager."

Claude: I'll store this team information in the knowledge graph.
[Uses process_text tool]
```

### Query Knowledge  
```
Human: Who works at Google?

Claude: Let me search the knowledge graph.
[Uses search tool]
Based on the knowledge graph: Alice works at Google as a senior engineer, and Bob works at Google as an engineering manager.
```

## Troubleshooting

### Server won't start
```bash
# Check logs
docker logs kg-mcp-server

# Common issues:
# - Neo4j connection failed: Check NEO4J_URI and credentials
# - Missing API key: Check OPENAI_API_KEY in .env
```

### Claude can't connect
```bash
# Verify server is running
curl http://localhost:3000/sse

# Check Claude config file path is correct
# Restart Claude Desktop after config changes
```

### Build failures
```bash
# Clean rebuild (from parent directory)
cd .. && docker build --no-cache -f kg_mcp_server/Dockerfile -t kg-mcp-server .

# Check parent directory has setup.py
ls setup.py src/
```

## Management Commands

```bash
# View logs
docker logs kg-mcp-server

# Stop server
docker stop kg-mcp-server

# Start server  
docker start kg-mcp-server

# Remove container
docker rm kg-mcp-server

# Rebuild image (from parent directory)
cd .. && docker build --no-cache -f kg_mcp_server/Dockerfile -t kg-mcp-server .
```

## Success Indicators

✅ **Container running**: `docker ps` shows kg-mcp-server  
✅ **Server responds**: `curl http://localhost:3000/sse` returns data  
✅ **Claude connected**: Claude shows kg-engine tools available  
✅ **Neo4j accessible**: No connection errors in logs  

## Next Steps

Once running, you can:
- Use all 11 MCP tools through Claude Desktop
- Build knowledge graphs from natural language
- Search and query your data semantically
- Manage nodes and relationships programmatically

For detailed documentation, see [README.md](README.md).