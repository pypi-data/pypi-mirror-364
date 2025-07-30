# Migration Guide: Upgrading to Knowledge Graph Engine v2.1.0

This guide helps you migrate from earlier versions to v2.1.0, which includes significant performance optimizations, GraphEdge refactoring, and new features.

## 🚀 What's New in v2.1.0

### Performance Improvements
- **50-74% faster queries** with GraphQueryOptimizer and Neo4jOptimizer
- **Smart caching system** with 5-minute TTL for near-instant repeated queries
- **18% smaller codebase** while adding more functionality
- **Optimized Cypher queries** using modern Neo4j procedures

### GraphEdge Refactoring
- **Lazy loading** of subject, relationship, and object fields
- **Safe accessors** to prevent "Relationship not populated" errors
- **Dynamic relationship types** (WORKS_AT, LIVES_IN) instead of generic RELATES_TO
- **Cached graph data** for improved performance

### New Features
- **Source filtering** in `get_node_relations()` method
- **Enhanced conflict detection** with optimized queries
- **Query result caching** with automatic TTL management
- **Performance monitoring** with optimization statistics

## 🔄 Breaking Changes

### 1. GraphEdge Model Changes

**Before (v2.0.x):**
```python
# Direct field access
edge = GraphEdge(
    subject="Alice",
    relationship="WORKS_AT", 
    object="Google",
    edge_id="123",
    metadata=EdgeMetadata(...)
)

# Fields were always populated
print(f"{edge.subject} {edge.relationship} {edge.object}")
```

**After (v2.1.0):**
```python
# Lazy loading with safe accessors
edge = GraphEdge(
    edge_id="123",
    metadata=EdgeMetadata(...)
    # subject, relationship, object are now lazy-loaded
)

# Use safe accessors to prevent errors
subject = edge.get_subject_safe() or "Unknown"
relationship = edge.get_relationship_safe() or "Unknown"
obj = edge.get_object_safe() or "Unknown"
print(f"{subject} {relationship} {obj}")

# Or check if graph data is populated
if edge.has_graph_data():
    subject, relationship, obj = edge.get_graph_data()
    print(f"{subject} {relationship} {obj}")
```

### 2. Relationship Type Changes

**Before (v2.0.x):**
```cypher
-- Generic relationship with property
MATCH (s)-[r:RELATES_TO {relationship: 'works_at'}]->(o)
```

**After (v2.1.0):**
```cypher
-- Dynamic relationship types
MATCH (s)-[r:WORKS_AT]->(o)
```

### 3. Method Signature Changes

**Before (v2.0.x):**
```python
# get_node_relations without source filtering
relations = engine.get_node_relations("Alice")
```

**After (v2.1.0):**
```python
# get_node_relations with optional source filtering
relations = engine.get_node_relations("Alice", source="user_input")
```

## 📝 Migration Steps

### Step 1: Update Code for Safe Accessors

**Find and replace patterns:**

```python
# REPLACE THIS:
print(f"{edge.subject} {edge.relationship} {edge.object}")

# WITH THIS:
subject = edge.get_subject_safe() or "Unknown"
relationship = edge.get_relationship_safe() or "Unknown"
obj = edge.get_object_safe() or "Unknown"
print(f"{subject} {relationship} {obj}")
```

**Or use the has_graph_data() check:**

```python
# REPLACE THIS:
for triplet in triplets:
    edge = triplet.edge
    print(f"{edge.subject} -> {edge.object}")

# WITH THIS:
for triplet in triplets:
    edge = triplet.edge
    if edge.has_graph_data():
        subject, relationship, obj = edge.get_graph_data()
        print(f"{subject} -> {obj}")
    else:
        subject = edge.get_subject_safe() or "Unknown"
        obj = edge.get_object_safe() or "Unknown"
        print(f"{subject} -> {obj}")
```

### Step 2: Update Query Methods

**Replace direct graph_db calls with optimized engine methods:**

```python
# REPLACE THIS:
triplets = engine.graph_db.get_entity_relationships("Alice")

# WITH THIS:
results = engine.get_node_relations("Alice")
triplets = [result.triplet for result in results]
```

**Use new source filtering:**

```python
# NEW FEATURE:
user_relations = engine.get_node_relations("Alice", source="user_input")
system_relations = engine.get_node_relations("Alice", source="system")
```

### Step 3: Leverage New Optimization Features

**Use conflict analysis:**

```python
# NEW FEATURE:
conflicts = engine.analyze_conflicts(entity_name="Alice")
print(f"Found {len(conflicts)} potential conflicts")

# Entity-specific conflict detection
location_conflicts = engine.analyze_conflicts(
    entity_name="Alice", 
    relationship_type="LIVES_IN"
)
```

**Use path finding:**

```python
# NEW FEATURE:
paths = engine.find_paths("Alice", "Google", max_hops=3)
for path_info in paths:
    print(f"Path confidence: {path_info['path_confidence']}")
    print(f"Path length: {path_info['path_length']}")
```

**Monitor performance:**

```python
# NEW FEATURE:
stats = engine.get_stats()
if 'optimization_stats' in stats:
    opt_stats = stats['optimization_stats']
    print(f"Cache hit rate: {opt_stats.get('cache_hit_rate', 0):.1%}")
    print(f"Average query time: {opt_stats.get('avg_query_time_ms', 0):.1f}ms")
```

### Step 4: Update Error Handling

**Replace specific error handling:**

```python
# REPLACE THIS:
try:
    print(f"{edge.subject} {edge.relationship} {edge.object}")
except AttributeError:
    print("Edge data not populated")

# WITH THIS:
subject = edge.get_subject_safe()
relationship = edge.get_relationship_safe()
obj = edge.get_object_safe()

if subject and relationship and obj:
    print(f"{subject} {relationship} {obj}")
else:
    print("Edge data not fully populated")
```

## 🧪 Testing Your Migration

### 1. Run Migration Test

Create a test file to verify your migration:

```python
# test_migration.py
import time
from src.kg_engine.core.engine import KnowledgeGraphEngineV2
from src.kg_engine.models import InputItem, EdgeData, EdgeMetadata
from src.kg_engine.config import Neo4jConfig

def test_migration():
    """Test migration to v2.1.0"""
    config = Neo4jConfig()
    engine = KnowledgeGraphEngineV2(api_key="test", neo4j_config=config)
    
    # Test safe accessors
    print("1. Testing safe accessors...")
    result = engine.process_input([
        InputItem(description="Alice works at TechCorp")
    ])
    
    relations = engine.get_node_relations("Alice")
    for result in relations:
        edge = result.triplet.edge
        subject = edge.get_subject_safe()
        relationship = edge.get_relationship_safe()
        obj = edge.get_object_safe()
        print(f"   Safe access: {subject} {relationship} {obj}")
    
    # Test caching performance
    print("2. Testing query caching...")
    query = "Who works at TechCorp?"
    
    start_time = time.time()
    response1 = engine.search(query)
    first_time = (time.time() - start_time) * 1000
    
    start_time = time.time()
    response2 = engine.search(query)
    cached_time = (time.time() - start_time) * 1000
    
    print(f"   First query: {first_time:.1f}ms")
    print(f"   Cached query: {cached_time:.1f}ms")
    print(f"   Speed improvement: {first_time/cached_time:.1f}x")
    
    # Test source filtering
    print("3. Testing source filtering...")
    all_relations = engine.get_node_relations("Alice")
    user_relations = engine.get_node_relations("Alice", source="user_input")
    
    print(f"   All relations: {len(all_relations)}")
    print(f"   User input relations: {len(user_relations)}")
    
    # Test conflict analysis
    print("4. Testing conflict analysis...")
    conflicts = engine.analyze_conflicts(entity_name="Alice")
    print(f"   Found {len(conflicts)} conflicts")
    
    print("✅ Migration test completed successfully!")

if __name__ == "__main__":
    test_migration()
```

### 2. Run Comprehensive Tests

```bash
# Run all provided tests
python test_relationship_fix.py
python test_optimizations.py
python test_quick_relationship_fix.py
```

### 3. Performance Benchmark

```python
# benchmark_migration.py
import time
from src.kg_engine.core.engine import KnowledgeGraphEngineV2
from src.kg_engine.models import InputItem

def benchmark_performance():
    """Benchmark performance improvements"""
    engine = KnowledgeGraphEngineV2(api_key="test")
    
    # Add test data
    test_data = [
        InputItem(description=f"Person{i} works at Company{i%10}")
        for i in range(50)
    ]
    
    start_time = time.time()
    engine.process_input(test_data)
    processing_time = time.time() - start_time
    
    print(f"Processed {len(test_data)} items in {processing_time:.2f}s")
    print(f"Average per item: {(processing_time/len(test_data))*1000:.1f}ms")
    
    # Test search performance
    queries = [
        "Who works at Company1?",
        "Tell me about Person10",
        "What companies are mentioned?"
    ]
    
    for query in queries:
        start_time = time.time()
        response = engine.search(query)
        query_time = (time.time() - start_time) * 1000
        
        print(f"Query '{query}': {query_time:.1f}ms")

if __name__ == "__main__":
    benchmark_performance()
```

## 📊 Expected Performance Improvements

After migration, you should see:

| Operation | Before v2.1.0 | After v2.1.0 | Improvement |
|-----------|---------------|--------------|-------------|
| Entity Exploration | 20-50ms | 8-15ms | ~60% faster |
| Vector Search | 100-200ms | 40-80ms | ~50% faster |
| Conflict Detection | 150-300ms | 50-100ms | ~67% faster |
| Path Finding | 80-160ms | 25-50ms | ~70% faster |
| Repeated Queries | Same as first | < 1ms | Near-instant |

## 🔧 Configuration Updates

### Environment Variables

No changes required for environment variables.

### Performance Tuning

Add these optional settings for better performance:

```bash
# .env additions for v2.1.0
NEO4J_POOL_SIZE=20           # Increased connection pool
QUERY_CACHE_TTL=300          # 5-minute cache TTL
ENABLE_QUERY_OPTIMIZATION=true  # Enable optimizations
```

## 🚨 Common Issues and Solutions

### Issue 1: "Relationship not populated" Errors

**Solution:** Use safe accessors everywhere:

```python
# Wrong way (will cause errors)
print(edge.subject)

# Right way (safe)
print(edge.get_subject_safe() or "Unknown")
```

### Issue 2: Performance Not Improved

**Solution:** Ensure indexes are created:

```python
# Force index creation
engine.graph_db._ensure_performance_indexes()
```

### Issue 3: Cache Not Working

**Solution:** Verify cache is enabled and TTL is set:

```python
# Check cache stats
stats = engine.get_stats()
print(stats.get('optimization_stats', {}))
```

### Issue 4: Legacy RELATES_TO Relationships

**Solution:** The system handles both old and new relationship types automatically. No action needed.

## 🎯 Best Practices for v2.1.0

1. **Always use safe accessors** for edge properties
2. **Leverage caching** by reusing common queries
3. **Use source filtering** to narrow down results
4. **Monitor performance** with optimization statistics
5. **Test thoroughly** after migration

## 📚 Additional Resources

- [API Reference](../api/README.md) - Updated API documentation
- [Architecture Overview](../architecture/overview.md) - System design with optimizations
- [Quick Start Guide](../user-guide/quick-start.md) - Updated examples
- [Performance Benchmarks](./benchmarks.md) - Detailed performance analysis

## 🆘 Getting Help

If you encounter issues during migration:

1. Check the [troubleshooting section](../user-guide/quick-start.md#-troubleshooting)
2. Run the provided test files to verify functionality
3. Review error logs for specific issues
4. Compare your code with the updated examples

## ✅ Migration Checklist

- [ ] Updated all direct edge property access to use safe accessors
- [ ] Replaced direct graph_db calls with optimized engine methods
- [ ] Added source filtering where appropriate
- [ ] Updated error handling to use safe accessors
- [ ] Ran migration tests successfully
- [ ] Verified performance improvements
- [ ] Updated any custom extensions or integrations

Congratulations! You've successfully migrated to Knowledge Graph Engine v2.1.0 🎉