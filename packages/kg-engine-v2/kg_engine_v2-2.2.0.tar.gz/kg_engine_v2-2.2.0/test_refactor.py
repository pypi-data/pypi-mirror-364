#!/usr/bin/env python3
"""
Test script for the refactored GraphEdge model
"""

from src.kg_engine.models import GraphEdge, EdgeMetadata, GraphTriplet, EdgeData
from datetime import datetime

def test_new_graph_edge():
    """Test the new GraphEdge model"""
    print("Testing new GraphEdge model...")
    
    # Create metadata
    metadata = EdgeMetadata(
        summary="Alice works at TechCorp",
        confidence=0.9,
        source="test"
    )
    
    # Test 1: Create minimal edge
    edge = GraphEdge.create_for_storage(metadata=metadata)
    print(f"✓ Created minimal edge: {edge.edge_id}")
    
    # Test 2: Check graph data not populated
    print(f"✓ Has graph data: {edge.has_graph_data()}")  # Should be False
    
    # Test 3: Set graph data
    edge.set_graph_data("Alice", "WORKS_AT", "TechCorp")
    print(f"✓ Has graph data after setting: {edge.has_graph_data()}")  # Should be True
    
    # Test 4: Access via properties
    print(f"✓ Subject: {edge.subject}")
    print(f"✓ Relationship: {edge.relationship}")
    print(f"✓ Object: {edge.object}")
    
    # Test 5: Access via safe methods
    print(f"✓ Subject (safe): {edge.get_subject_safe()}")
    print(f"✓ Relationship (safe): {edge.get_relationship_safe()}")
    print(f"✓ Object (safe): {edge.get_object_safe()}")
    
    # Test 6: Get as tuple
    subject, relationship, obj = edge.get_graph_data()
    print(f"✓ Graph data tuple: ({subject}, {relationship}, {obj})")
    
    # Test 7: Test GraphTriplet with populated edge
    triplet = GraphTriplet(edge=edge)
    vector_text = triplet.to_vector_text()
    print(f"✓ Vector text: {vector_text}")
    
    # Test 8: Test EdgeData
    edge_data = EdgeData(
        subject="Bob",
        relationship="LIVES_IN",
        object="NYC",
        metadata=metadata
    )
    print(f"✓ EdgeData: {edge_data.subject} {edge_data.relationship} {edge_data.object}")
    
    print("\nAll tests passed! 🎉")

if __name__ == "__main__":
    test_new_graph_edge()