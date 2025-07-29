# Development Documentation

This section contains information for developers working on or contributing to Knowledge Graph Engine v2.

## 📑 Development Guides

### [Setup Guide](./setup.md)
Development environment setup, dependencies, and configuration.

### [Testing](./testing.md)
Test suite structure, running tests, and adding new tests.

### [Contributing](./contributing.md)
Guidelines for contributing code, reporting issues, and submitting PRs.

### [Performance](./performance.md)
Performance optimization guidelines, profiling, and benchmarking.

## 🛠️ Development Environment

### Prerequisites
- **Python 3.8+** with pip
- **Neo4j 5.x** running locally or accessible remotely
- **Git** for version control
- **Optional**: Docker for containerized development

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd kg-engine-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Verify setup
python -m pytest tests/
python examples.py
```

## 🧪 Development Workflow

### 1. **Feature Development**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... edit code ...

# Run tests
python -m pytest tests/

# Check code quality
black src/
flake8 src/
mypy src/

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/your-feature-name
```

### 2. **Running Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_engine.py

# Run with coverage
python -m pytest --cov=src tests/

# Run integration tests (requires Neo4j)
python -m pytest tests/test_neo4j_integration.py -v
```

### 3. **Code Quality**
```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# All quality checks
python -m pytest --cov=src tests/ && black --check src/ && flake8 src/ && mypy src/
```

## 📁 Project Structure

```
src/
├── engine.py                     # Main engine implementation
├── models.py                     # Data models and types
├── graph_db.py                   # Neo4j graph operations
├── neo4j_vector_store.py         # Vector storage implementation
├── custom_neo4j_vector_store.py  # Custom vector store (modern Neo4j)
├── vector_store.py               # Vector store interface
├── vector_store_adapter.py       # Adapter pattern implementation
├── vector_store_factory.py       # Factory for store creation
├── llm_interface.py              # LLM integration layer
├── neo4j_config.py              # Database configuration
├── neo4j_schema.py              # Schema management
├── neo4j_optimizer.py           # Query optimization
├── graph_query_optimizer.py     # Advanced query optimization
├── date_parser.py               # Date parsing utilities
└── __init__.py                  # Package initialization

tests/
├── test_engine.py               # Engine unit tests
├── test_models.py               # Model validation tests
├── test_graph_db.py             # Graph database tests
├── test_vector_store.py         # Vector store tests
├── test_llm_interface.py        # LLM interface tests
├── test_neo4j_integration.py    # Integration tests
└── conftest.py                  # Test configuration

docs/
├── architecture/                # System architecture docs
├── user-guide/                  # User documentation
├── api/                         # API reference
└── development/                 # Development guides
```

## 🔧 Development Tools

### Required Tools
- **pytest**: Test framework
- **black**: Code formatting
- **flake8**: Style checking
- **mypy**: Type checking
- **pip-tools**: Dependency management

### Optional Tools
- **pytest-cov**: Test coverage
- **pytest-xdist**: Parallel test execution
- **pre-commit**: Git hooks for quality checks
- **docker**: Containerized development

### IDE Configuration

#### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm
- Set interpreter to virtual environment
- Enable pytest as test runner
- Configure black as formatter
- Enable mypy and flake8 inspections

## 📋 Coding Standards

### Python Style
- **PEP 8** compliance via flake8
- **Black** formatting with line length 88
- **Type hints** for all functions and methods
- **Docstrings** for all public APIs

### Code Organization
- **Single Responsibility**: Each class/function has one clear purpose
- **Dependency Injection**: Use configuration objects
- **Error Handling**: Comprehensive exception handling
- **Logging**: Use structured logging with appropriate levels

### Example Code Style
```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """Example class showing coding standards.
    
    Args:
        config: Configuration object
        optional_param: Optional parameter with default
    """
    
    def __init__(
        self, 
        config: Config, 
        optional_param: Optional[str] = None
    ) -> None:
        self.config = config
        self.optional_param = optional_param
    
    def process_data(
        self, 
        input_data: List[Dict[str, str]]
    ) -> Dict[str, int]:
        """Process input data and return results.
        
        Args:
            input_data: List of data dictionaries to process
            
        Returns:
            Dictionary with processing results
            
        Raises:
            ValueError: If input data is invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        try:
            # Process data
            result = self._internal_processing(input_data)
            logger.info(f"Processed {len(input_data)} items successfully")
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def _internal_processing(
        self, 
        data: List[Dict[str, str]]
    ) -> Dict[str, int]:
        """Internal processing method (private)."""
        # Implementation details...
        return {"processed": len(data)}
```

## 🐛 Debugging

### Common Debug Scenarios

#### Neo4j Connection Issues
```python
# Test connection manually
from src.neo4j_config import Neo4jConfig

config = Neo4jConfig()
if config.verify_connectivity():
    print("✅ Connection OK")
else:
    print("❌ Connection failed")
```

#### LLM API Issues
```python
# Test LLM interface
from src.llm_interface import LLMInterface

llm = LLMInterface(api_key="test")
try:
    result = llm.extract_entities_relationships("test text")
    print("✅ LLM working")
except Exception as e:
    print(f"❌ LLM error: {e}")
```

#### Vector Search Issues
```python
# Test vector operations
from src.neo4j_vector_store import Neo4jKnowledgeGraphVectorStore

store = Neo4jKnowledgeGraphVectorStore()
stats = store.get_stats()
print(f"Vector store stats: {stats}")
```

### Debug Logging
```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run your code with detailed logs
```

## 🚀 Performance Monitoring

### Profiling Code
```python
import cProfile
import pstats

# Profile a function
def profile_function():
    # Your code here
    pass

cProfile.run('profile_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumtime')
stats.print_stats(20)
```

### Memory Usage
```python
import tracemalloc

tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

## 📊 Performance Benchmarks

### Expected Performance
- **Entity Extraction**: ~100-300ms per text input
- **Graph Operations**: ~1-10ms per operation
- **Vector Search**: ~20-200ms depending on dataset size
- **End-to-End Processing**: ~200-1000ms per input item

### Optimization Targets
- **Batch Processing**: >100 items/second
- **Search Queries**: <500ms response time
- **Memory Usage**: <100MB for 10k relationships
- **Neo4j Connections**: <10 concurrent connections

## 🤝 Contributing

See [Contributing Guide](./contributing.md) for:
- Code review process
- Issue reporting guidelines  
- Pull request templates
- Release procedures

## 📚 Additional Resources

- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [pytest Documentation](https://docs.pytest.org/)