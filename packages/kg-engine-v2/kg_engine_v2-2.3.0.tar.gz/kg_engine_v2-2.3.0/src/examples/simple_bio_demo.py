#!/usr/bin/env python3
"""
Simple Biographical Knowledge Graph Demo

4 people with overlapping facts:
- Emma (Berlin → Paris, software engineer, dancing, photography)  
- Marcus (San Francisco → Paris, entrepreneur, dancing, wine)
- Sophia (Barcelona → NYC, graphic designer, photography, fashion)
- David (Lyon → Paris, engineer, photography, dancing)

Overlaps: Paris (Emma, Marcus, David), Dancing (Emma, Marcus, David), Photography (Emma, Sophia, David)
"""
import os
from datetime import datetime

# Biographical facts as structured data
PEOPLE_FACTS = {
    "Emma Johnson": [
        ("born_in", "Berlin"),
        ("studied_at", "Technical University Berlin"), 
        ("works_as", "software engineer"),
        ("relocated_from", "Berlin"),
        ("lives_in", "Paris"),
        ("enjoys", "dancing"),
        ("enjoys", "photography"),
        ("speaks", "German"),
        ("speaks", "English"),
        ("learning", "French")
    ],
    
    "Marcus Chen": [
        ("born_in", "San Francisco"),
        ("studied_at", "Stanford University"),
        ("works_as", "entrepreneur"),
        ("lives_in", "Paris"), 
        ("enjoys", "dancing"),
        ("enjoys", "wine tasting"),
        ("speaks", "English"),
        ("speaks", "French")
    ],
    
    "Sophia Rodriguez": [
        ("born_in", "Barcelona"),
        ("studied_at", "University of Barcelona"),
        ("works_as", "graphic designer"),
        ("works_as", "creative director"),
        ("lives_in", "New York City"),
        ("enjoys", "photography"),
        ("specializes_in", "fashion photography"),
        ("speaks", "Spanish"),
        ("speaks", "English"),
        ("speaks", "Catalan")
    ],
    
    "David Laurent": [
        ("born_in", "Lyon"),
        ("studied_at", "École Centrale Lyon"),
        ("works_as", "project manager"),
        ("lives_in", "Paris"),
        ("enjoys", "photography"),
        ("enjoys", "dancing"),
        ("specializes_in", "architectural photography"),
        ("speaks", "French"),
        ("speaks", "English")
    ]
}

def demo_with_manual_data():
    """Demo using manual relationship data (works without API key)"""
    print("🏗️ Biographical Knowledge Graph Demo")
    print("=" * 50)
    
    # Import required modules
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from src.kg_engine import KnowledgeGraphEngineV2
        from src.kg_engine.config import Neo4jConfig
        from src.kg_engine.models import GraphTriplet, GraphEdge, EdgeMetadata, RelationshipStatus
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return
    
    # Initialize Neo4j
    neo4j_config = Neo4jConfig()
    if not neo4j_config.verify_connectivity():
        print("❌ Cannot connect to Neo4j")
        print("Please start Neo4j: docker run --name neo4j -p7474:7474 -p7687:7687 -d -e NEO4J_AUTH=neo4j/password neo4j:latest")
        return
    
    print("✅ Neo4j connection verified")
    
    # Initialize engine (works with test API key for manual data)
    engine = KnowledgeGraphEngineV2(
        api_key="test",
        vector_store_type="neo4j", 
        neo4j_config=neo4j_config
    )
    
    print("🧹 Clearing existing data...")
    engine.clear_all_data()
    
    # Convert facts to triplets
    print("📊 Creating knowledge graph from biographical facts...")
    all_triplets = []
    
    for person, facts in PEOPLE_FACTS.items():
        print(f"\n👤 {person}:")
        for relationship, obj in facts:
            # Create triplet
            triplet = GraphTriplet(
                edge=GraphEdge(
                    subject=person,
                    relationship=relationship,
                    object=obj,
                    metadata=EdgeMetadata(
                        summary=f"{person} {relationship} {obj}",
                        confidence=0.95,
                        status=RelationshipStatus.ACTIVE,
                        obsolete=False,
                        created_at=datetime.now(),
                        source="biographical_facts"
                    )
                )
            )
            all_triplets.append(triplet)
            print(f"   {person} {relationship} {obj}")
    
    # Add to knowledge graph
    print(f"\n🔗 Adding {len(all_triplets)} relationships to Neo4j...")
    ids = engine.vector_store.add_triplets(all_triplets)
    print(f"✅ Successfully added {len(ids)} triplets")
    
    # Analyze overlapping facts
    print("\n🔍 Analyzing Overlapping Facts:")
    print("-" * 30)
    
    # Find people who live in same cities
    locations = {}
    for person, facts in PEOPLE_FACTS.items():
        for rel, obj in facts:
            if rel == "lives_in":
                if obj not in locations:
                    locations[obj] = []
                locations[obj].append(person)
    
    print("📍 Shared Locations:")
    for location, people in locations.items():
        if len(people) > 1:
            print(f"   {location}: {', '.join(people)}")
        else:
            print(f"   {location}: {people[0]}")
    
    # Find shared hobbies
    hobbies = {}
    for person, facts in PEOPLE_FACTS.items():
        for rel, obj in facts:
            if rel == "enjoys":
                if obj not in hobbies:
                    hobbies[obj] = []
                hobbies[obj].append(person)
    
    print("\n🎨 Shared Interests:")
    for hobby, people in hobbies.items():
        if len(people) > 1:
            print(f"   {hobby}: {', '.join(people)} ⭐")
        else:
            print(f"   {hobby}: {people[0]}")
    
    # Test semantic search
    print("\n🔎 Testing Semantic Search:")
    print("-" * 25)
    
    search_queries = [
        "Who lives in Paris?",
        "Who enjoys photography?", 
        "Who works in technology?",
        "Who speaks multiple languages?"
    ]
    
    for query in search_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = engine.vector_store.search(query, k=5)
            if results:
                print(f"Found {len(results)} results:")
                for result in results[:3]:
                    edge = result.triplet.edge
                    print(f"  - {edge.subject} {edge.relationship} {edge.object} (score: {result.score:.3f})")
            else:
                print("  No results found")
        except Exception as e:
            print(f"  Search error: {e}")
    
    # Get statistics
    print(f"\n📈 Knowledge Graph Statistics:")
    stats = engine.vector_store.get_stats()
    print(f"   Total triplets: {stats.get('total_triplets', 'unknown')}")
    print(f"   Store type: {stats.get('store_type', 'unknown')}")
    print(f"   Model: {stats.get('model_name', 'unknown')}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    
    return engine

if __name__ == "__main__":
    demo_with_manual_data()