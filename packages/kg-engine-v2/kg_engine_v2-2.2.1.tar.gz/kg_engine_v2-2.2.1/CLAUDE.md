# Knowledge Graph Engine v2 - Project Overview

## 🎯 Project Description

A modern, production-ready knowledge graph engine built entirely on **Neo4j** for persistent graph storage and vector search capabilities. The system combines graph database operations with semantic vector search to provide intelligent information storage, retrieval, and reasoning.

### Key Features
- **Neo4j-Native**: Complete Neo4j integration for both graph and vector operations
- **Enhanced Semantic Search**: Improved vector search with dynamic thresholds and contextual boosting
- **Smart Query Understanding**: Context-aware search with semantic category matching  
- **LLM Integration**: OpenAI/Ollama support for entity extraction and query processing
- **Conflict Resolution**: Intelligent handling of contradicting information with temporal tracking
- **Modern Architecture**: Clean, modular design with comprehensive error handling
- **Performance Optimizations**: Query caching, advanced algorithms, and optimized data access

### Technology Stack
- **Database**: Neo4j 5.x (graph + vector storage)
- **Language**: Python 3.8+
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: OpenAI API / Ollama (with pattern matching fallback)
- **Query Language**: Cypher
- **Vector Search**: Custom Neo4j vector store implementation
- **Caching**: 5-minute TTL query result caching

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Interface │    │   Graph Database │    │  Vector Store   │
│                 │    │                  │    │                 │
│ • Entity Extract│    │ • Neo4j Native   │    │ • Neo4j Vectors │
│ • Query Parse   │    │ • Query Cache    │    │ • Semantic      │
│ • Answer Gen.   │    │ • Optimizations  │    │ • Search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │ KG Engine v2        │
                    │  (Optimized)        │
                    │                     │
                    │ • Process Input     │
                    │ • Smart Updates     │
                    │ • Hybrid Search     │
                    │ • Natural Language  │
                    └─────────────────────┘
```

## 📁 Project Structure

```
src/
├── kg_engine/                    # Knowledge Graph Engine
│   ├── core/
│   │   └── engine.py            # Main KG Engine
│   ├── models/
│   │   └── models.py            # Data models and schemas
│   ├── storage/
│   │   ├── graph_db.py          # Neo4j graph operations
│   │   ├── neo4j_vector_store.py # Neo4j vector storage
│   │   ├── custom_neo4j_vector_store.py # Modern Neo4j vector implementation
│   │   ├── vector_store.py      # Unified vector store interface
│   │   ├── vector_store_adapter.py # Adapter pattern
│   │   └── vector_store_factory.py # Factory for vector stores
│   ├── llm/
│   │   └── llm_interface.py     # LLM integration (OpenAI/Ollama)
│   ├── config/
│   │   ├── neo4j_config.py      # Neo4j connection configuration
│   │   └── neo4j_schema.py      # Schema management
│   └── utils/
│       ├── date_parser.py        # Temporal data parsing
│       ├── graph_query_optimizer.py # Advanced query optimization
│       └── neo4j_optimizer.py    # Neo4j query optimization
├── examples/                     # Usage examples
│   ├── examples.py              # Basic examples
│   ├── bio_example.py           # Biographical demo
│   └── simple_bio_demo.py       # Simple demo
└── test_neo4j_integration.py    # Test suite

docs/                            # Comprehensive documentation
├── architecture/                # System design and workflows
├── user-guide/                  # Getting started and usage
├── api/                         # API reference
└── development/                 # Development setup and testing

examples.py                      # Usage examples and demos
tests/                          # Test suite
setup.py                        # Package configuration
```

## 🎯 Core Capabilities

### 1. **Intelligent Information Processing**
- Automatic entity and relationship extraction from natural language
- Semantic conflict resolution with temporal tracking
- Duplicate detection and relationship merging
- Negation handling ("Alice no longer works at...")

### 2. **Enhanced Semantic Search**
- **Dynamic Similarity Thresholds**: Base threshold of 0.3 with context-specific adjustments
- **Query-Specific Boosting**: Contextual relevance scoring for different query types
- **Semantic Category Matching**: Understanding conceptual relationships (technology → software engineer)
- **Geographic Intelligence**: Recognizes European cities and geographic relationships
- **Smart Filtering**: Distinguishes work, hobbies, locations, and other relationship types

#### Search Improvements (v2.1.0)
- Lowered similarity thresholds from 0.7 to 0.3 for better recall
- Added contextual boosting (+0.2-0.3) for relevant relationships  
- Enhanced semantic category definitions for common query patterns
- Improved handling of:
  - Technology/profession queries ("Who works in tech?")
  - Geographic queries ("Who was born in Europe?")
  - Activity queries ("What do people do for hobbies?")
  - Photography and other specific interests

### 3. **Production Features**
- ACID compliance through Neo4j transactions
- Comprehensive error handling and fallback mechanisms
- Performance optimization with query analysis and caching
- Modern Neo4j procedures (no deprecation warnings)
- Optimized queries with 50-74% performance improvements
- Smart caching system with 5-minute TTL
- Query result deduplication and ranking

## 🆕 Recent Updates (v2.1.0)

### Performance Optimizations
- **Optimized Graph Queries**: Implemented GraphQueryOptimizer and Neo4jOptimizer classes
- **Smart Caching**: Added query result caching with TTL management
- **18% Code Reduction**: Refactored engine.py from 632 to 520 lines while adding features
- **Performance Gains**: 50-74% improvement in common query patterns

### GraphEdge Refactoring
- Removed redundant subject/relationship/object fields
- Implemented lazy loading with cached properties
- Added safe accessors: `get_subject_safe()`, `get_relationship_safe()`, `get_object_safe()`
- Dynamic relationship types (WORKS_AT, LIVES_IN) instead of generic RELATES_TO

### Bug Fixes
- Fixed "Relationship not populated" error by changing `r.relationship` to `type(r)` in queries
- Enhanced _update_counters method with safe key access
- Added source parameter filtering to get_node_relations

## 📚 Documentation

Comprehensive documentation available in `/docs`:

- **[Quick Start](docs/user-guide/quick-start.md)**: Get running in 5 minutes
- **[Architecture](docs/architecture/overview.md)**: System design and components
- **[Workflows](docs/architecture/workflows.md)**: Process flows and diagrams
- **[API Reference](docs/api/README.md)**: Complete API documentation
- **[Migration Guide](docs/development/migration-v2.md)**: Upgrading to v2.1.0

## 🔧 Development Guidelines

### Code Style & Standards
- **Modular Design**: Single responsibility principle
- **Clean Architecture**: Clear separation of concerns
- **Type Hints**: Full type annotation for all functions
- **Error Handling**: Graceful degradation and comprehensive logging
- **Documentation**: Docstrings for all public methods

### Semantic Conventions
Use comments like `#AI-TODO`, `#AI-REVIEW`, `#AI-QUESTION` to mark areas for AI assistance:
- Use `#AI-REVIEW` for code that needs review or refactoring
- Use `#AI-QUESTION` for areas where you need clarification
- Use `#AI-TODO` for tasks that need to be completed later
- Use `#AI-REFACTORING` for code that needs performance or readability improvements

### Development Rules
- **Neo4j-First**: All graph operations must use Neo4j (no NetworkX, no ChromaDB)
- **Modern Standards**: Use current Neo4j procedures and avoid deprecated features
- **Testing**: Write tests for critical functionality
- **Performance**: Optimize queries and use appropriate indexes
- **Documentation**: Update docs when changing APIs
- **Safe Access**: Always use safe accessors for optional GraphEdge fields
- **Caching**: Leverage the built-in query caching system for repeated operations
- **Query Optimization**: Use GraphQueryOptimizer and Neo4jOptimizer for complex queries

### Forbidden Practices
- ❌ **No ChromaDB**: Legacy ChromaDB code has been removed
- ❌ **No NetworkX**: All graph operations use Neo4j
- ❌ **No Deprecated Neo4j APIs**: Use modern procedures only
- ❌ **No Mixed Storage**: Neo4j is the single source of truth

## 🚀 Getting Started

1. **Prerequisites**: Python 3.8+, Neo4j 5.x
2. **Installation**: `pip install -e .`
3. **Configuration**: Set up `.env` with Neo4j credentials
4. **Quick Test**: `python examples.py`

See [Quick Start Guide](docs/user-guide/quick-start.md) for detailed setup instructions.

## 📊 Performance Characteristics

- **Graph Operations**: ~1-5ms per operation (50-74% faster with optimizations)
- **Vector Search**: ~20-100ms depending on dataset size  
- **End-to-End Processing**: ~200-500ms per input item
- **Semantic Search**: High precision with contextual filtering
- **Scalability**: Designed for 10k-1M+ relationships
- **Cache Performance**: Near-instant retrieval for cached queries (< 1ms)
- **Query Optimization**: 
  - Entity exploration: O(degree) for single-hop, O(degree^n) for n-hop
  - Path finding: Uses Neo4j's shortestPath algorithm
  - Conflict detection: O(n²) with constraints

## 🔍 Key Use Cases

- **Personal Knowledge Management**: Meeting notes, contacts, tasks
- **Customer Relationship Management**: Customer interactions and history
- **Research & Documentation**: Scientific papers, citations, findings
- **Business Intelligence**: Company relationships, market analysis
- **Content Management**: Document relationships, topic modeling

## 🧪 Testing

Comprehensive test suite available:
- `test_neo4j_integration.py`: Core integration tests
- `test_optimizations.py`: Performance optimization validation
- `test_relationship_fix.py`: Relationship population tests
- `test_quick_relationship_fix.py`: Quick validation tests

Run all tests: `python -m pytest tests/`

## 🔧 Key Implementation Details

### GraphEdge Model
```python
@dataclass
class GraphEdge:
    edge_id: str
    metadata: EdgeMetadata
    
    # Lazy-loaded from Neo4j
    _subject: Optional[str] = None
    _relationship: Optional[str] = None
    _object: Optional[str] = None
    
    # Safe accessors
    def get_subject_safe(self) -> Optional[str]
    def get_relationship_safe(self) -> Optional[str]
    def get_object_safe(self) -> Optional[str]
```

### Optimized Query Example
```python
# Old: Generic RELATES_TO with property
MATCH (s)-[r:RELATES_TO {relationship: 'works_at'}]->(o)

# New: Dynamic relationship types
MATCH (s)-[r:WORKS_AT]->(o)
```

---

**Version**: 2.1.0  
**Architecture**: Neo4j-Native Knowledge Graph with Optimizations  
**Status**: Production Ready  
**Last Updated**: January 2025

