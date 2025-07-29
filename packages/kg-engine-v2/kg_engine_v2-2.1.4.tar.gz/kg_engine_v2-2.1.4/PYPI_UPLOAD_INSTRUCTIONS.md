# PyPI Upload Instructions

## Package Summary

The `kg-engine-v2` package has been prepared for PyPI distribution with the following structure:

- **Package Name**: `kg-engine-v2` (will install as `kg_engine_v2`)
- **Version**: 2.1.0
- **Main Module**: `kg_engine`
- **Distribution Files**: `dist/kg_engine_v2-2.1.0.tar.gz` and `dist/kg_engine_v2-2.1.0-py3-none-any.whl`

## Files Created/Updated

1. **setup.py** - Updated with proper PyPI metadata
2. **pyproject.toml** - Modern Python packaging configuration with Neo4j dependencies
3. **MANIFEST.in** - Controls which files are included in the package
4. **src/kg_engine/__init__.py** - Main package exports
5. **dist/** - Built distribution files ready for PyPI

## Upload to PyPI

### 1. Test Upload (PyPI Test Server)
```bash
# Upload to test PyPI first
twine upload --repository testpypi dist/*

# Test installation from test PyPI
pip install --index-url https://test.pypi.org/simple/ kg-engine-v2
```

### 2. Production Upload
```bash
# Upload to production PyPI
twine upload dist/*

# Verify installation
pip install kg-engine-v2
```

### 3. Authentication
You'll need PyPI API token:
- Create account at https://pypi.org
- Generate API token in account settings
- Configure twine: `twine configure` or set environment variables

## Usage After Installation

After installing via `pip install kg-engine-v2`, users can import and use the package:

```python
from kg_engine import KnowledgeGraphEngineV2, InputItem

# Initialize engine
engine = KnowledgeGraphEngineV2()

# Use the knowledge graph
item = InputItem(content="Alice works at OpenAI", source="my_app")
result = engine.process_input(item)
```

## Dependencies

The package includes all necessary dependencies:
- Neo4j 5.0+ for graph database
- OpenAI API for LLM processing
- Sentence Transformers for embeddings
- LlamaIndex for vector operations

## Requirements

Users need:
1. Neo4j database (local or cloud)
2. OpenAI API key (optional, has fallback)
3. Python 3.8+

See the main README.md for detailed setup instructions.