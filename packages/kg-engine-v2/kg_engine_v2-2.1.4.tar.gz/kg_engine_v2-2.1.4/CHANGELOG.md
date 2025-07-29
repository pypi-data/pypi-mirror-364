# Changelog

## Version 2.1.1 - Intransitive Verb Fix (2025)

### 🐛 **Bug Fixes**
- **Fixed None object values** - Intransitive verbs like "was founded" now properly create relationships
- **Improved relationship modeling** - Uses HAS_STATUS relationship for state changes
- **Enhanced LLM prompts** - Better examples for handling implicit objects
- **Updated fallback extraction** - Handles common intransitive patterns

### 🔧 **Technical Details**
- Modified extraction prompt to handle sentences without explicit objects
- Changed relationship structure from `Company A FOUNDED None` to `Company A HAS_STATUS founded`
- Added support for: founded, established, began, occurred, ended, closed
- Maintains backward compatibility with transitive verbs

## Version 2.1.0 - Enhanced Date Parsing (2024)

### 🚀 **Enhanced Temporal Capabilities**
- **Integrated dateparser library** - Robust natural language date parsing
- **Advanced date format support** - Handles relative dates like "yesterday", "next month", "2 weeks ago"
- **Improved temporal extraction** - Better detection of dates in natural text
- **Date range parsing** - Support for "from X to Y" and "between X and Y" patterns
- **Enhanced temporal conflict resolution** - More accurate temporal relationship management

### 🔧 **Technical Improvements**
- **DateParser class rewrite** - Now uses dateparser library instead of regex patterns
- **Extended temporal indicators** - More comprehensive pattern matching
- **Better error handling** - Graceful fallback for unparseable dates
- **Natural language support** - Understands complex relative expressions
- **ChromaDB metadata fix** - Proper handling of None values in metadata
- **Vector store compatibility** - Ensures all metadata fields are ChromaDB-compatible

### 📝 **Documentation Updates**
- **Temporal capabilities section** - Comprehensive examples of date parsing
- **Updated code examples** - Show temporal relationship usage
- **Enhanced README** - Better documentation of features

## Version 2.0.0 - Major Refactor (2024)

### 🎯 **Project Structure Refactor**
- **Removed all unrelated code** - Cleaned up legacy LlamaIndex/Neo4j demo code
- **Focused on KG Engine v2** - Now contains only the advanced knowledge graph engine
- **Simplified imports** - Direct imports from `src` package
- **Updated dependencies** - Minimal, focused dependency list

### 🚀 **Key Features Maintained**
- **Semantic relationship handling** - TEACH_IN ≈ WORKS_AT detection
- **Conflict detection** - Automatic obsoleting of conflicting relationships
- **Temporal tracking** - Date-aware relationship management
- **Vector search** - ChromaDB with sentence transformers
- **LLM integration** - OpenAI GPT-4 for entity extraction

### 🔧 **Technical Improvements**
- **In-memory storage option** - For testing and lightweight usage
- **Better error handling** - Fixed "Number of requested results 0" error
- **Proper counting** - Accurate obsolete edge counts
- **Optimized search** - Reduced timeout issues

### 📦 **Package Structure**
```
kg-engine-v2/
├── src/                    # Core engine code
│   ├── __init__.py        # Main exports
│   ├── engine.py          # Main orchestration
│   ├── models.py          # Data structures
│   ├── llm_interface.py   # OpenAI integration
│   ├── vector_store.py    # ChromaDB integration
│   ├── graph_db.py        # NetworkX graph storage
│   └── date_parser.py     # Temporal parsing
├── examples.py            # Usage examples
├── test_kg_engine.py      # Basic tests
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python config
└── README.md             # Documentation
```

### 📋 **Ready for Next Steps**
- Clean, focused codebase
- Well-defined API surface
- Comprehensive examples
- Proper Python packaging
- Ready for extensions/integrations