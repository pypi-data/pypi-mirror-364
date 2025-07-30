# API Reference

Comprehensive API documentation for the Knowledge Graph Engine v2.

## Core API

- [KnowledgeGraphEngineV2](engine.md) - Main engine class
- [Data Models](models.md) - Core data structures
- [Storage API](storage.md) - Graph and vector storage interfaces
- [LLM Interface](llm.md) - Language model integration

## New Features

- [Edge Classifier](edge-classifier.md) - Intelligent edge categorization system
- [CRUD Operations](crud-operations.md) - Complete create, read, update, delete API
- [External Usage](external-usage.md) - Using KG Engine as external package

## Utilities

- [Query Optimization](optimization.md) - Performance optimization utilities
- [Date Parser](date-parser.md) - Temporal data parsing
- [Configuration](configuration.md) - System configuration

## REST API

- [API Server](../../kg_api_server/README.md) - Production-ready FastAPI server

## Quick Reference

### Basic Usage

```python
from kg_engine import KnowledgeGraphEngineV2, InputItem, Neo4jConfig

# Initialize
engine = KnowledgeGraphEngineV2(
    api_key="your-key",
    neo4j_config=Neo4jConfig()
)

# Process
engine.process_input([
    InputItem("Alice works at Google")
])

# Search
response = engine.search("Who works at Google?")
```

### Available Imports

```python
from kg_engine import (
    # Core
    KnowledgeGraphEngineV2, InputItem, GraphEdge, EdgeMetadata,
    GraphTriplet, EdgeData, SearchResult, QueryResponse,
    
    # Enums
    RelationshipStatus, SearchType, QueryType,
    
    # Config
    Neo4jConfig, setup_neo4j_schema,
    
    # Utils
    parse_date, ClassifierDetector, ClassifierMap,
    
    # Version
    __version__
)
```