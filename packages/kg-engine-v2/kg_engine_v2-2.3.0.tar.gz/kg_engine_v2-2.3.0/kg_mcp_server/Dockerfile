# KG Engine MCP Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the KG Engine package files (context is parent directory)
COPY setup.py /kg_engine/setup.py
COPY src /kg_engine/src
COPY README.md /kg_engine/README.md

# Install KG Engine
WORKDIR /kg_engine
RUN pip install --no-cache-dir -e .

# Switch back to app directory
WORKDIR /app

# Copy MCP server files (from kg_mcp_server subdirectory)
COPY kg_mcp_server/requirements.txt .
COPY kg_mcp_server/server.py .

# Install MCP dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp && \
    chown -R mcp:mcp /app && \
    chown -R mcp:mcp /kg_engine
USER mcp

# Set environment variables (non-sensitive defaults only)
ENV PYTHONPATH=/kg_engine:$PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV NEO4J_URI=bolt://localhost:7687
ENV NEO4J_USERNAME=neo4j
ENV NEO4J_DATABASE=neo4j
ENV OPENAI_MODEL=gpt-4o-mini

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/sse || exit 1

# Run the MCP server
CMD ["python", "server.py"]