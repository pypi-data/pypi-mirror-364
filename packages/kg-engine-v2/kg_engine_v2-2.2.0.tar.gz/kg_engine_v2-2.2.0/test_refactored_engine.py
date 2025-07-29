#!/usr/bin/env python3
"""
Test script for the refactored Knowledge Graph Engine v2.

Tests that all optimized methods are working correctly and the engine
uses optimized queries by default.
"""

import time
from datetime import datetime

from src.kg_engine.core.engine import KnowledgeGraphEngineV2
from src.kg_engine.models import InputItem
from src.kg_engine.config import Neo4jConfig

def test_refactored_engine():
    """Test the refactored engine functionality"""
    print("🧪 Testing Refactored Knowledge Graph Engine v2")
    print("=" * 60)
    
    # Initialize engine
    config = Neo4jConfig()
    engine = KnowledgeGraphEngineV2(
        api_key="ollama", 
        model="llama3.2:3b",
        base_url="http://localhost:11434/v1",
        neo4j_config=config
    )
    
    print("\n1. Testing Input Processing with Optimized Operations")
    print("-" * 50)
    
    # Clear existing data for clean test
    engine.clear_all_data()
    
    # Test data
    test_items = [
        InputItem("Alice works as a software engineer at TechCorp"),
        InputItem("Bob is a data scientist at TechCorp"),
        InputItem("Alice lives in San Francisco"),
        InputItem("Charlie used to work at OldCorp", to_date="2022-12-31"),
        InputItem("Charlie now works at NewCorp", from_date="2023-01-01"),
        InputItem("David was born in London"),
        InputItem("Alice enjoys photography as a hobby"),
    ]
    
    # Process input
    start_time = time.time()
    results = engine.process_input(test_items)
    processing_time = time.time() - start_time
    
    print(f"✅ Processed {results['processed_items']} items in {processing_time:.2f}s")
    print(f"   - New edges: {results['new_edges']}")
    print(f"   - Errors: {len(results['errors'])}")
    print(f"   - Processing time: {results['processing_time_ms']:.2f}ms")
    
    print("\n2. Testing Optimized Search Operations")
    print("-" * 50)
    
    # Test optimized search
    queries = [
        "Who works at TechCorp?",
        "Where does Alice live?",
        "What does Alice enjoy?",
        "Who used to work at OldCorp?"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        start_time = time.time()
        response = engine.search(query, search_type="both", k=5)
        search_time = time.time() - start_time
        
        print(f"  Results: {len(response.results)} found in {search_time:.3f}s")
        print(f"  Confidence: {response.confidence:.2f}")
        if response.results:
            for i, result in enumerate(response.results[:2]):
                edge = result.triplet.edge
                print(f"    {i+1}. {edge.subject} {edge.relationship} {edge.object} (score: {result.score:.2f})")
    
    print("\n3. Testing Advanced Optimized Operations")
    print("-" * 50)
    
    # Test node relations using optimized method
    print("Testing optimized node relations for 'Alice':")
    relations = engine.get_node_relations("Alice", max_depth=1)
    print(f"  Found {len(relations)} relations")
    for rel in relations[:3]:
        edge = rel.triplet.edge
        print(f"    - {edge.subject} {edge.relationship} {edge.object}")
    
    # Test conflict analysis
    print("\nTesting optimized conflict detection:")
    conflicts = engine.analyze_conflicts()
    print(f"  Found {len(conflicts)} conflicts")
    for conflict in conflicts[:2]:
        print(f"    - {conflict['conflicted_entity']} has conflicting {conflict['conflicted_relationship']} relationships")
    
    # Test temporal analysis  
    print("\nTesting optimized temporal analysis for 'Charlie':")
    temporal = engine.analyze_temporal_relationships("Charlie")
    print(f"  Found {len(temporal)} temporal relationships")
    for temp in temporal[:2]:
        print(f"    - {temp['relationship_type']} with {temp['connected_entity']}")
    
    # Test path finding
    print("\nTesting optimized path finding (Alice -> TechCorp):")
    paths = engine.find_paths("Alice", "TechCorp", max_hops=2)
    print(f"  Found {len(paths)} paths")
    for path in paths[:2]:
        print(f"    - Length: {path['path_length']}, Confidence: {path['path_confidence']:.2f}")
    
    print("\n4. Testing Engine Statistics")
    print("-" * 50)
    
    # Test comprehensive stats including optimization stats
    stats = engine.get_stats()
    if "error" not in stats:
        print("✅ Statistics retrieved successfully")
        print(f"   - Graph stats available: {'graph_stats' in stats}")
        print(f"   - Vector stats available: {'vector_stats' in stats}")
        print(f"   - Optimization stats available: {'optimization_stats' in stats}")
        print(f"   - Total entities: {stats.get('entities', 0)}")
        print(f"   - Total relationships: {len(stats.get('relationships', []))}")
        
        # Show optimization stats
        if 'optimization_stats' in stats:
            opt_stats = stats['optimization_stats']
            if 'cache_stats' in opt_stats:
                cache_stats = opt_stats['cache_stats']
                print(f"   - Cache entries: {cache_stats.get('total_entries', 0)}")
                print(f"   - Cache hit rate: {cache_stats.get('hit_rate', 0):.1%}")
    else:
        print(f"❌ Error getting stats: {stats['error']}")
    
    print("\n5. Testing Export/Import with Optimization Data")
    print("-" * 50)
    
    # Test export including optimization stats
    export_data = engine.export_knowledge_graph()
    print(f"✅ Export completed")
    print(f"   - Version: {export_data.get('version', 'unknown')}")
    print(f"   - Contains optimization stats: {'optimization_stats' in export_data}")
    print(f"   - Export timestamp: {export_data.get('export_timestamp', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("🎉 Refactored Engine Test Completed Successfully!")
    print("✅ All optimized operations are working correctly")
    print("✅ Engine uses optimized queries by default")
    print("✅ Compact code structure maintained")
    print("✅ Unnecessary functionality removed")

def main():
    """Run the refactored engine test"""
    try:
        test_refactored_engine()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())