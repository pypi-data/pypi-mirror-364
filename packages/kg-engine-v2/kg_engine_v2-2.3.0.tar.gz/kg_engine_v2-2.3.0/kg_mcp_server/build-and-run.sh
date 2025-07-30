#!/bin/bash

# KG Engine MCP Server - Build and Run Script
# This script builds and runs the MCP server as a standalone Docker container

set -e

echo "🚀 KG Engine MCP Server Build and Run Script"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your configuration before running the server."
        echo "   Required: NEO4J_PASSWORD and OPENAI_API_KEY (or LLM_BASE_URL + LLM_BEARER_KEY)"
        exit 1
    else
        echo "❌ No .env.example file found. Cannot create configuration."
        exit 1
    fi
fi

# Load environment variables
source .env

# Validate required environment variables
if [ -z "$NEO4J_PASSWORD" ]; then
    echo "❌ NEO4J_PASSWORD is required in .env file"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] && ([ -z "$LLM_BASE_URL" ] || [ -z "$LLM_BEARER_KEY" ]); then
    echo "❌ Either OPENAI_API_KEY or both LLM_BASE_URL and LLM_BEARER_KEY are required in .env file"
    exit 1
fi

# Build the Docker image (context is parent directory, dockerfile in current)
echo "🔨 Building Docker image..."
cd ..
docker build -f kg_mcp_server/Dockerfile -t kg-mcp-server .
cd kg_mcp_server

# Stop existing container if running
if docker ps -q -f name=kg-mcp-server | grep -q .; then
    echo "🛑 Stopping existing container..."
    docker stop kg-mcp-server
    docker rm kg-mcp-server
fi

# Run the container
echo "🏃 Starting MCP server container..."
docker run -d \
  --name kg-mcp-server \
  -p 3000:3000 \
  --env-file .env \
  kg-mcp-server

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if container is running
if docker ps -q -f name=kg-mcp-server | grep -q .; then
    echo "✅ MCP server is running!"
    echo ""
    echo "📊 Server Information:"
    echo "   Container: kg-mcp-server"
    echo "   Port: 3000"
    echo "   SSE Endpoint: http://localhost:3000/sse"
    echo ""
    echo "🔍 Useful commands:"
    echo "   View logs: docker logs kg-mcp-server"
    echo "   Stop server: docker stop kg-mcp-server"
    echo "   Remove container: docker rm kg-mcp-server"
    echo ""
    echo "🤖 Claude Desktop Configuration:"
    echo '   Add to claude_desktop_config.json:'
    echo '   {'
    echo '     "mcpServers": {'
    echo '       "kg-engine": {'
    echo '         "url": "http://localhost:3000/sse"'
    echo '       }'
    echo '     }'
    echo '   }'
else
    echo "❌ Failed to start MCP server. Check logs:"
    docker logs kg-mcp-server
    exit 1
fi