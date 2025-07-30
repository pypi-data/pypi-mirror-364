# Edge Classifier System

The Edge Classifier System provides intelligent categorization and normalization of relationships in the knowledge graph using vector similarity instead of LLM calls for improved performance.

## Overview

The edge classifier system automatically:
- Categorizes edges into semantic groups (business, location, interests, etc.)
- Normalizes similar edge names to standard forms
- Uses vector similarity with 85% threshold for matching
- Provides fast, deterministic classification without LLM overhead

## Architecture

### Components

1. **ClassifierMap** (`src/kg_engine/models/classifier_map.py`)
   - Manages edge categories stored in Neo4j
   - Provides CRUD operations for categories
   - Caches normalized embeddings for performance

2. **ClassifierDetector** (`src/kg_engine/utils/classifier_detector.py`)
   - Performs vector similarity matching
   - Normalizes edge names before comparison
   - Finds best matching category and edge name

## Usage

### Automatic Classification

When processing natural language input, edges are automatically classified:

```python
# Input: "Alice works at Google"
# Automatically classified as:
# - Category: "business"
# - Normalized edge: "WORKS_AT"

engine.process_input([
    InputItem(description="Alice works at Google"),
    InputItem(description="Bob is employed by Microsoft"),  # Also becomes WORKS_AT
    InputItem(description="Charlie works for Apple")        # Also becomes WORKS_AT
])
```

### Manual Classification

You can manually specify categories when creating edges:

```python
from kg_engine import EdgeData, EdgeMetadata

metadata = EdgeMetadata(
    summary="John leads the engineering team",
    category="business",  # Manually set category
    confidence=0.95
)

edge_data = EdgeData(
    subject="John",
    relationship="LEADS",
    object="Engineering Team",
    metadata=metadata
)
```

## Edge Name Normalization

The system normalizes edge names to improve similarity matching:

1. **Convert to lowercase**: `WORKS_AT` → `works at`
2. **Remove underscores**: `works_at` → `works at`
3. **Remove common prefixes**: `is_employed_by` → `employed by`
4. **Trim whitespace**: ` works at ` → `works at`

### Normalization Examples

| Original | Normalized | Category | Standard Edge |
|----------|-----------|----------|---------------|
| WORKS_AT | works at | business | WORKS_AT |
| is_employed_by | employed by | business | WORKS_AT |
| works_for | works for | business | WORKS_AT |
| LIVES_IN | lives in | location | LIVES_IN |
| resides_at | resides at | location | LIVES_IN |
| enjoys_hobby | enjoys hobby | interests | ENJOYS |

## Vector Similarity

The system uses sentence transformers for semantic similarity:

```python
# Configuration
MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model
SIMILARITY_THRESHOLD = 0.85  # 85% similarity required

# Process
1. Normalize edge name
2. Generate embedding
3. Compare with cached category embeddings
4. Return best match if similarity >= 85%
```

## Categories

Default categories include:

### Business
- Employment relationships (works_at, employed_by, works_for)
- Leadership (leads, manages, directs)
- Business partnerships

### Location
- Residence (lives_in, resides_at, located_in)
- Origin (from, born_in, native_of)
- Travel (visited, moved_to)

### Personal
- Family relationships (parent_of, married_to, sibling_of)
- Personal connections (knows, friends_with)

### Interests
- Hobbies (enjoys, likes, passionate_about)
- Skills (skilled_in, practices, studies)

### Temporal
- Time-based relationships (started_on, ended_on, during)

## Performance

Vector similarity provides significant performance improvements:

| Operation | LLM-based | Vector Similarity | Improvement |
|-----------|-----------|-------------------|-------------|
| Classification | 200-500ms | 5-15ms | 95%+ faster |
| Consistency | Variable | Deterministic | 100% consistent |
| Cost | API calls | Local computation | No API costs |
| Offline capability | Requires API | Fully offline | Always available |

## Customization

### Adding New Categories

```python
# Get classifier map
classifier_map = ClassifierMap(graph_db)

# Add new category with example edges
classifier_map.add_category(
    category="education",
    example_edges=["studied_at", "graduated_from", "teaches_at", "enrolled_in"]
)
```

### Adjusting Similarity Threshold

```python
# Create custom detector with different threshold
detector = ClassifierDetector(
    classifier_map=classifier_map,
    embedder=embedder,
    similarity_threshold=0.9  # Require 90% similarity
)
```

## Best Practices

1. **Use descriptive edge names**: More descriptive names improve classification accuracy
2. **Leverage categories**: Consistent categorization helps with graph queries
3. **Monitor classifications**: Review edge classifications periodically
4. **Update categories**: Add new categories as your domain evolves

## API Reference

### ClassifierDetector

```python
class ClassifierDetector:
    def __init__(self, classifier_map, embedder, similarity_threshold=0.85):
        """Initialize with classifier map and embedder"""
        
    def detect_category(self, edge_name: str) -> Optional[str]:
        """Detect category for an edge name"""
        
    def find_best_edge(self, edge_name: str, category: str) -> Optional[str]:
        """Find best matching edge in a category"""
```

### ClassifierMap

```python
class ClassifierMap:
    def __init__(self, graph_db):
        """Initialize with graph database connection"""
        
    def get_category_edges(self, category: str) -> List[str]:
        """Get all edges for a category"""
        
    def add_category(self, category: str, example_edges: List[str]):
        """Add new category with example edges"""
        
    def update_cache(self):
        """Update the normalized embedding cache"""
```

## Migration from LLM

If migrating from LLM-based classification:

1. **No code changes needed**: The API remains the same
2. **Improved performance**: 95%+ faster classification
3. **Reduced costs**: No LLM API calls for classification
4. **Better consistency**: Deterministic results

The system automatically uses vector similarity when available, providing a seamless upgrade path.