#!/usr/bin/env python3
"""
Examples showing how to use KG Engine v2
"""
import os
from dotenv import load_dotenv
from src.kg_engine import KnowledgeGraphEngineV2, InputItem
from src.kg_engine.config import Neo4jConfig

# Load environment variables
load_dotenv()

def example_semantic_relationships():
    """Example showing semantic relationship handling"""
    print("=== Example: Semantic Relationship Handling ===\n")
    
    # Initialize Neo4j config
    neo4j_config = Neo4jConfig()
    
    # Initialize engine with Neo4j
    engine = KnowledgeGraphEngineV2(
        api_key=os.getenv("OPENAI_API_KEY", "test"),
        vector_store_type="neo4j",
        neo4j_config=neo4j_config
    )
    
    # Clear any existing data
    print("Clearing existing data...")
    engine.clear_all_data()
    
    try:
        # Add initial relationship
        print("1. Adding: John Smith teaches at MIT")
        result1 = engine.process_input([
            InputItem(description="John Smith teaches at MIT")
        ])
        print(f"   Result: {result1['new_edges']} new edge(s) created")
        
        # Add negation with different relationship type
        print("\n2. Adding negation: John Smith no longer works at MIT")
        result2 = engine.process_input([
            InputItem(description="John Smith no longer works at MIT")
        ])
        print(f"   Result: {result2['obsoleted_edges']} edge(s) obsoleted")
        
        # Search to verify
        search_result = engine.search("John Smith MIT")
        print(f"\n3. Search results: {len(search_result.results)} active relationships found")
        
        # Show all edges including obsolete
        all_triplets = engine.graph_db.find_edges(subject="John Smith", filter_obsolete=False)
        print("\n4. All edges in graph:")
        for triplet in all_triplets:
            edge = triplet.edge
            status = "OBSOLETE" if edge.metadata.obsolete else "ACTIVE"
            print(f"   - {edge.subject} {edge.relationship} {edge.object} [{status}]")
        
    except Exception as e:
        if "API" in str(e) or "authentication" in str(e).lower():
            print(f"⚠️ LLM operation failed (expected with test API key): {e}")
            print("   This example requires a valid OpenAI API key for relationship extraction")
        else:
            raise e

def example_conflict_detection():
    """Example showing conflict detection"""
    print("\n=== Example: Conflict Detection ===\n")
    
    # Initialize Neo4j config
    neo4j_config = Neo4jConfig()
    
    # Initialize engine with Neo4j
    engine = KnowledgeGraphEngineV2(
        api_key=os.getenv("OPENAI_API_KEY", "test"),
        vector_store_type="neo4j",
        neo4j_config=neo4j_config
    )
    
    # Clear any existing data
    print("Clearing existing data...")
    engine.clear_all_data()
    
    try:
        # Add initial location
        print("1. Adding: Alice lives in New York")
        result1 = engine.process_input([
            InputItem(description="Alice lives in New York")
        ])
        
        # Add conflicting location
        print("2. Adding: Alice resides in Boston")
        result2 = engine.process_input([
            InputItem(description="Alice resides in Boston")
        ])
        print(f"   Conflicts resolved: {result2.get('updated_edges', 0)}")
        
        # Show final state
        alice_triplets = engine.graph_db.find_edges(subject="Alice", filter_obsolete=False)
        print("\n3. Alice's location history:")
        for triplet in alice_triplets:
            edge = triplet.edge
            status = "OBSOLETE" if edge.metadata.obsolete else "ACTIVE"
            print(f"   - {edge.subject} {edge.relationship} {edge.object} [{status}]")
            
    except Exception as e:
        if "API" in str(e) or "authentication" in str(e).lower():
            print(f"⚠️ LLM operation failed (expected with test API key): {e}")
            print("   This example requires a valid OpenAI API key for relationship extraction")
        else:
            raise e

def example_search_capabilities():
    """Example showing search capabilities"""
    print("\n=== Example: Search Capabilities ===\n")
    
    # Initialize Neo4j config
    neo4j_config = Neo4jConfig()
    
    # Initialize engine with Neo4j
    engine = KnowledgeGraphEngineV2(
        api_key=os.getenv("OPENAI_API_KEY", "test"),
        vector_store_type="neo4j",
        neo4j_config=neo4j_config
    )
    
    # Clear any existing data
    print("Clearing existing data...")
    engine.clear_all_data()
    
    try:
        # Add some relationships
        relationships = [
            "Emma Watson works for Google",
            "Tom Hanks acts in movies",
            "Marie Curie researched radioactivity",
            "Einstein developed relativity theory"
        ]
        
        print("Adding relationships:")
        for desc in relationships:
            engine.process_input([InputItem(description=desc)])
            print(f"  - {desc}")
        
        # Perform different types of searches
        queries = [
            "Who works in technology?",
            "Tell me about scientists",
            "What do actors do?"
        ]
        
        print("\nSearch results:")
        for query in queries:
            result = engine.search(query, k=3)
            print(f"\nQuery: '{query}'")
            print(f"Answer: {result.answer}")
            print(f"Found {len(result.results)} relevant relationships")
            
    except Exception as e:
        if "API" in str(e) or "authentication" in str(e).lower():
            print(f"⚠️ LLM operation failed (expected with test API key): {e}")
            print("   This example requires a valid OpenAI API key for relationship extraction and answer generation")
        else:
            raise e

def example_neo4j_basic_operations():
    """Example showing basic Neo4j operations without LLM"""
    print("\n=== Example: Neo4j Basic Operations (No LLM) ===\n")
    
    # Initialize Neo4j config
    neo4j_config = Neo4jConfig()
    
    # Initialize engine with Neo4j
    engine = KnowledgeGraphEngineV2(
        api_key="test",  # Test key, won't be used
        vector_store_type="neo4j",
        neo4j_config=neo4j_config
    )
    
    print("Clearing existing data...")
    engine.clear_all_data()
    
    # Test vector store operations directly
    from src.kg_engine.models import GraphTriplet, RelationshipStatus
    from datetime import datetime
    
    # Create test triplets
    from src.kg_engine.models import GraphEdge, EdgeMetadata
    
    test_triplets = [
        GraphTriplet(
            edge=GraphEdge(
                subject="Alice",
                relationship="works_for", 
                object="Google",
                metadata=EdgeMetadata(
                    summary="Alice works for Google as a software engineer",
                    confidence=0.95,
                    status=RelationshipStatus.ACTIVE,
                    obsolete=False,
                    created_at=datetime.now(),
                    source="manual_test"
                )
            )
        ),
        GraphTriplet(
            edge=GraphEdge(
                subject="Bob",
                relationship="lives_in",
                object="San Francisco",
                metadata=EdgeMetadata(
                    summary="Bob lives in San Francisco",
                    confidence=0.88,
                    status=RelationshipStatus.ACTIVE,
                    obsolete=False,
                    created_at=datetime.now(),
                    source="manual_test"
                )
            )
        )
    ]
    
    print("1. Adding test triplets directly to Neo4j...")
    ids = engine.vector_store.add_triplets(test_triplets)
    print(f"   Added {len(ids)} triplets with IDs: {ids[:2]}...")
    
    print("\n2. Getting vector store statistics...")
    stats = engine.vector_store.get_stats()
    print(f"   Total triplets: {stats.get('total_triplets', 'unknown')}")
    print(f"   Store type: {stats.get('store_type', 'unknown')}")
    
    print("\n3. Testing semantic search...")
    try:
        results = engine.vector_store.search("software engineer Google", k=5)
        print(f"   Found {len(results)} results for 'software engineer Google'")
        for result in results:
            print(f"     - {result.triplet.edge.subject} {result.triplet.edge.relationship} {result.triplet.edge.object} (score: {result.score:.3f})")
    except Exception as e:
        print(f"   Search failed: {e}")
    
    print("\n4. Testing entity search...")
    try:
        results = engine.vector_store.search_by_entity("Alice", k=5)
        print(f"   Found {len(results)} results for entity 'Alice'")
        for result in results:
            print(f"     - {result.triplet.edge.subject} {result.triplet.edge.relationship} {result.triplet.edge.object}")
    except Exception as e:
        print(f"   Entity search failed: {e}")

def main():
    """Run all examples"""
    # Check Neo4j connectivity first
    neo4j_config = Neo4jConfig()
    if not neo4j_config.verify_connectivity():
        print("❌ Cannot connect to Neo4j. Please ensure Neo4j is running and configured properly.")
        print(f"   Trying to connect to: {neo4j_config.uri}")
        print(f"   Username: {neo4j_config.username}")
        print("   Check NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD environment variables")
        return
    
    print("✅ Neo4j connection verified")
    
    # Set up Neo4j schema
    from src.neo4j_schema import setup_neo4j_schema
    print("Setting up Neo4j schema...")
    try:
        schema_results = setup_neo4j_schema(neo4j_config)
        print(f"✅ Schema setup complete: {len(schema_results.get('constraints', []))} constraints, {len(schema_results.get('vector_indexes', []))} vector indexes")
    except Exception as e:
        print(f"⚠️ Schema setup warning: {e}")
        print("   Continuing with examples...")
    
    print("KG Engine v2 - Examples (Neo4j)\n" + "="*50)
    
    try:
        # Run basic Neo4j operations first (works without LLM)
        example_neo4j_basic_operations()
        
        # Run LLM-based examples (will show warnings if no API key)
        example_semantic_relationships()
        example_conflict_detection()
        example_search_capabilities()
        
        print("\n" + "="*50)
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")

if __name__ == "__main__":
    main()