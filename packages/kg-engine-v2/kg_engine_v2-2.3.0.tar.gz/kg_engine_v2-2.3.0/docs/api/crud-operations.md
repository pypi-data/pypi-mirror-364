# CRUD Operations API

Complete Create, Read, Update, and Delete operations for edges and nodes in the Knowledge Graph Engine.

## Overview

The KG Engine provides comprehensive CRUD operations through both programmatic API and REST endpoints. All operations are designed to work seamlessly with the Neo4j backend while maintaining data integrity and relationships.

## Edge Operations

### Create Edge

#### Programmatic API

```python
from kg_engine import EdgeData, EdgeMetadata, RelationshipStatus

# Create edge metadata
metadata = EdgeMetadata(
    summary="Alice works as a senior engineer at Google",
    confidence=0.95,
    source="manual_entry",
    category="business",
    from_date=parse_date("2023-01-15"),
    status=RelationshipStatus.ACTIVE
)

# Create edge data
edge_data = EdgeData(
    subject="Alice",
    relationship="WORKS_AT",
    object="Google",
    metadata=metadata
)

# Add to graph
success = engine.graph_db.add_edge_data(edge_data)
```

#### REST API

```bash
curl -X POST "http://localhost:8080/edges" \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "Alice",
       "relationship": "WORKS_AT",
       "object": "Google",
       "summary": "Alice works as a senior engineer at Google",
       "confidence": 0.95,
       "category": "business",
       "from_date": "2023-01-15"
     }'
```

### Read Edges

#### Get All Edges for a Node

```python
# Programmatic API
edges = engine.graph_db.get_node_edges(
    node_name="Alice",
    relationship_type="WORKS_AT",  # Optional filter
    include_inactive=False          # Exclude obsolete edges
)

for edge in edges:
    print(f"{edge.subject} {edge.relationship} {edge.object}")
```

#### REST API

```bash
# Get all relations for a node
curl "http://localhost:8080/nodes/Alice/relations?limit=20"

# Response includes all edges where Alice is subject or object
```

### Update Edge

#### Mark Edge as Obsolete

```python
# Find and update edge status
edge_id = "edge_123"  # Get from search or creation
engine.graph_db.update_edge_status(
    edge_id=edge_id,
    status=RelationshipStatus.OBSOLETE,
    to_date=datetime.now()
)
```

#### Update Edge Confidence

```python
engine.graph_db.update_edge_confidence(
    edge_id=edge_id,
    confidence=0.85
)
```

### Delete Edge

```python
# Soft delete (mark as obsolete)
engine.graph_db.mark_edge_obsolete(edge_id)

# Hard delete (remove from database)
engine.graph_db.delete_edge(edge_id)  # Use with caution
```

## Node Operations

### Create Node

Nodes are automatically created when edges reference them. You can also create standalone nodes:

```python
# Nodes are created implicitly when adding edges
edge_data = EdgeData(
    subject="New Person",  # Node created if doesn't exist
    relationship="WORKS_AT",
    object="New Company",  # Node created if doesn't exist
    metadata=metadata
)
```

### Read Nodes

#### Get Node Information

```python
# Get all relationships for a node
relations = engine.get_node_relations(
    node_name="Alice",
    max_depth=2,  # Include second-degree connections
    filter_obsolete=True
)

# Get node statistics
stats = engine.graph_db.get_node_stats("Alice")
print(f"Node has {stats['edge_count']} edges")
```

#### Search Nodes

```python
# Find nodes by pattern
nodes = engine.graph_db.search_nodes(
    pattern="Ali*",  # Wildcard search
    limit=10
)
```

### Update Nodes

#### Rename Node

```python
# Update all references to a node
engine.graph_db.rename_node(
    old_name="Bob Smith",
    new_name="Robert Smith"
)
```

#### Update Node Properties

```python
# Add or update node properties
engine.graph_db.update_node_properties(
    node_name="Alice",
    properties={
        "email": "alice@example.com",
        "department": "Engineering"
    }
)
```

### Delete Node

```python
# Delete node and all its relationships
engine.graph_db.delete_node(
    node_name="Test Node",
    cascade=True  # Also delete all edges
)
```

## Merge Operations

### Automatic Node Merging

Uses LLM to intelligently merge two nodes:

```python
# Programmatic API
result = engine.graph_db.merge_nodes_auto(
    source_node="John Smith",
    target_node="J. Smith",
    merge_strategy="intelligent"  # Uses LLM for decisions
)

print(f"Merged into: {result['merged_node_name']}")
print(f"Transferred {result['relationships_transferred']} relationships")
```

#### REST API

```bash
curl -X POST "http://localhost:8080/nodes/merge" \
     -H "Content-Type: application/json" \
     -d '{
       "source_node": "John Smith",
       "target_node": "J. Smith",
       "merge_type": "auto"
     }'
```

### Manual Node Merging

Merge nodes with explicit control:

```python
# Programmatic API
result = engine.graph_db.merge_nodes_manual(
    source_node="John",
    target_node="Jonathan",
    new_name="John Smith",
    new_metadata={
        "full_name": "John Smith",
        "aliases": ["John", "Jonathan", "J. Smith"]
    }
)
```

#### REST API

```bash
curl -X POST "http://localhost:8080/nodes/merge" \
     -H "Content-Type: application/json" \
     -d '{
       "source_node": "John",
       "target_node": "Jonathan",
       "merge_type": "manual",
       "new_name": "John Smith",
       "new_properties": {
         "full_name": "John Smith",
         "aliases": ["John", "Jonathan"]
       }
     }'
```

## Batch Operations

### Batch Edge Creation

```python
# Create multiple edges efficiently
edges = [
    EdgeData(subject="Alice", relationship="KNOWS", object="Bob", metadata=meta1),
    EdgeData(subject="Bob", relationship="KNOWS", object="Charlie", metadata=meta2),
    EdgeData(subject="Charlie", relationship="KNOWS", object="Alice", metadata=meta3)
]

results = engine.graph_db.add_edges_batch(edges)
print(f"Created {results['created']} edges, {results['skipped']} duplicates")
```

### Batch Node Updates

```python
# Update multiple nodes
updates = [
    {"node": "Alice", "properties": {"role": "Senior Engineer"}},
    {"node": "Bob", "properties": {"role": "Manager"}},
    {"node": "Charlie", "properties": {"role": "Designer"}}
]

engine.graph_db.update_nodes_batch(updates)
```

## Query Operations

### Complex Graph Queries

```python
# Find all people who work at companies in Silicon Valley
query = """
MATCH (person)-[r:WORKS_AT]->(company)
WHERE company.location = 'Silicon Valley'
RETURN person.name, r.summary, company.name
"""

results = engine.graph_db.execute_query(query)
```

### Aggregation Queries

```python
# Count relationships by type
stats = engine.graph_db.get_relationship_stats()
for rel_type, count in stats.items():
    print(f"{rel_type}: {count} edges")
```

## Transaction Support

All CRUD operations support transactions:

```python
# Use transaction for atomic updates
with engine.graph_db.transaction() as tx:
    # All operations in transaction
    tx.add_edge_data(edge1)
    tx.add_edge_data(edge2)
    tx.update_node_properties("Alice", {"status": "active"})
    # Automatically commits on success, rolls back on error
```

## Error Handling

All CRUD operations include comprehensive error handling:

```python
try:
    result = engine.graph_db.add_edge_data(edge_data)
except DuplicateEdgeError:
    print("Edge already exists")
except InvalidNodeError:
    print("Invalid node name")
except Neo4jError as e:
    print(f"Database error: {e}")
```

## Best Practices

1. **Use Soft Deletes**: Mark edges as obsolete instead of deleting
2. **Batch Operations**: Use batch methods for multiple operations
3. **Transaction Scope**: Keep transactions small and focused
4. **Index Usage**: Ensure proper indexes for frequently queried properties
5. **Error Recovery**: Always handle potential errors gracefully

## Performance Tips

1. **Batch Processing**: Process multiple items together
2. **Lazy Loading**: Use GraphEdge safe accessors
3. **Query Optimization**: Use the query optimizers for complex queries
4. **Connection Pooling**: Reuse database connections
5. **Caching**: Leverage the built-in query cache

## REST API Reference

See the [API Server documentation](../../kg_api_server/README.md) for complete REST API details including:

- Request/response schemas
- Authentication (if configured)
- Rate limiting
- Error responses
- WebSocket support (planned)