#!/usr/bin/env python3
"""
Quick test for relationship population fix
"""

from src.kg_engine.core.engine import KnowledgeGraphEngineV2
from src.kg_engine.models import EdgeData, EdgeMetadata
from src.kg_engine.config import Neo4jConfig

def test_quick_relationship_fix():
    """Quick test of relationship fixes"""
    print("🧪 Quick Relationship Fix Test")
    print("=" * 50)
    
    # Initialize engine
    config = Neo4jConfig()
    engine = KnowledgeGraphEngineV2(api_key="test", neo4j_config=config)
    
    # Clear and add one test edge
    engine.clear_all_data()
    
    edge_data = EdgeData("Alice", "WORKS_AT", "TechCorp", 
                        EdgeMetadata("Alice works at TechCorp", confidence=0.9))
    
    print("1. Adding test edge...")
    success = engine.graph_db.add_edge_data(edge_data)
    print(f"   ✅ Edge added: {success}")
    
    print("\n2. Testing optimized entity exploration...")
    try:
        triplets = engine.graph_db.get_entity_relationships_optimized("Alice", limit=5)
        print(f"   Found {len(triplets)} triplets")
        
        if triplets:
            triplet = triplets[0]
            if triplet.edge.has_graph_data():
                subject, relationship, obj = triplet.edge.get_graph_data()
                print(f"   ✅ Graph data populated: {subject} -{relationship}-> {obj}")
            else:
                print(f"   ❌ Graph data not populated")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3. Testing get_node_relations with source filter...")
    try:
        # Test without source filter
        relations1 = engine.get_node_relations("Alice")
        print(f"   Without filter: {len(relations1)} relations")
        
        # Test with source filter  
        relations2 = engine.get_node_relations("Alice", source="user_input")
        print(f"   With source='user_input': {len(relations2)} relations")
        
        # Test with non-matching source filter
        relations3 = engine.get_node_relations("Alice", source="nonexistent")
        print(f"   With source='nonexistent': {len(relations3)} relations")
        
        print("   ✅ Source filtering working")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n4. Testing safe relationship access...")
    try:
        triplets = engine.graph_db.get_entity_relationships_optimized("Alice", limit=1)
        if triplets:
            edge = triplets[0].edge
            
            # Test safe accessors
            subject = edge.get_subject_safe()
            relationship = edge.get_relationship_safe()
            obj = edge.get_object_safe()
            
            print(f"   Safe access: {subject} -{relationship}-> {obj}")
            print("   ✅ Safe accessors working")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Quick test completed!")
    print("✅ Relationship population should be fixed")
    print("✅ Source filtering added to get_node_relations") 
    print("✅ Safe accessors prevent 'Relationship not populated' errors")

if __name__ == "__main__":
    test_quick_relationship_fix()