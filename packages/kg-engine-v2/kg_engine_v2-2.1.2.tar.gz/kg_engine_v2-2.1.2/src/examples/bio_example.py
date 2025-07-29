#!/usr/bin/env python3
"""
Example: Building Knowledge Graph from Personal Biographies

This example demonstrates how to extract relationships from biographical text
and build a comprehensive knowledge graph with overlapping facts.
"""
import os
from dotenv import load_dotenv
from src.kg_engine import KnowledgeGraphEngineV2, InputItem
from src.kg_engine.config import Neo4jConfig

# Load environment variables
load_dotenv()

# Biographical data with overlapping facts
BIOGRAPHIES = {
    "Emma_Johnson": """
Emma Johnson was born in Berlin, Germany in 1985. She studied computer science at 
Technical University of Berlin and worked as a software engineer for several tech 
companies. In 2018, Emma relocated from Berlin to Paris to join a French startup 
as their lead developer. She currently lives in Paris and loves dancing salsa in 
her free time. Emma also enjoys photography and often captures street scenes around 
Montmartre. She speaks fluent German, English, and is learning French.
""",

    "Marcus_Chen": """
Marcus Chen was born in San Francisco, California in 1990. He studied business 
administration at Stanford University and became an entrepreneur after graduation. 
Marcus founded two successful startups in Silicon Valley before moving to Paris 
in 2020 to expand his business internationally. He currently lives in Paris and 
is passionate about dancing - particularly ballroom and Latin styles. Marcus also 
enjoys wine tasting and frequently visits vineyards in the Loire Valley. He speaks 
English and has become fluent in French during his time in Europe.
""",

    "Sophia_Rodriguez": """
Sophia Rodriguez was born in Barcelona, Spain in 1988. She studied fine arts at 
University of Barcelona and worked as a graphic designer for various agencies. 
Sophia has always been passionate about photography, specializing in portrait and 
fashion photography. She moved to New York City in 2015 to pursue her career in 
the fashion industry. Currently, she works as a creative director for a major 
fashion magazine and lives in Manhattan. Sophia speaks Spanish, English, and some 
Catalan from her Barcelona roots.
""",

    "David_Laurent": """
David Laurent was born in Lyon, France in 1987. He studied mechanical engineering 
at École Centrale Lyon and worked in the automotive industry for several years. 
David has lived in Paris since 2012 where he works as a project manager for a 
renewable energy company. He is an avid photographer who focuses on architectural 
and urban landscapes throughout Paris. David loves dancing and regularly attends 
tango lessons at a local dance studio. He speaks French natively and has learned 
English through his international business dealings.
"""
}
def extract_relationships_from_bio():
    """Extract relationships from biographical data using the KG engine"""
    print("=== Biographical Knowledge Graph Example ===\n")
    
    # Initialize Neo4j config
    neo4j_config = Neo4jConfig()
    
    # Verify Neo4j connectivity
    if not neo4j_config.verify_connectivity():
        print("❌ Cannot connect to Neo4j. Please ensure Neo4j is running.")
        print(f"   Connection: {neo4j_config.uri}")
        return
    
    print("✅ Neo4j connection verified")
    
    # Initialize engine with Neo4j
    api_key = os.getenv("OPENAI_API_KEY", "test")
    engine = KnowledgeGraphEngineV2(
        api_key=api_key,
        vector_store_type="neo4j",
        neo4j_config=neo4j_config
    )
    
    # Clear any existing data
    # print("🧹 Clearing existing data...")
    # engine.clear_all_data()
    
    # Process each biography
    print("\n📖 Processing biographies and extracting relationships...\n")
    
    total_new_edges = 0
    total_updated_edges = 0
    
    for person, bio in BIOGRAPHIES.items():
        print(f"Processing {person.replace('_', ' ')}...")
        
        try:
            # Create input item with person context
            input_item = InputItem(
                description=bio,
                metadata={
                    "source": "biography",
                    "person": person,
                    "data_type": "biographical_text"
                }
            )
            
            # Process the biography
            result = engine.process_input([input_item])
            
            new_edges = result.get('new_edges', 0)
            updated_edges = result.get('updated_edges', 0)
            
            print(f"  ✅ Extracted {new_edges} new relationships")
            if updated_edges > 0:
                print(f"  🔄 Updated {updated_edges} existing relationships")
            
            total_new_edges += new_edges
            total_updated_edges += updated_edges
            
        except Exception as e:
            if "API" in str(e) or "authentication" in str(e).lower():
                print(f"  ⚠️ API error (expected with test key): Limited extraction")
                exit()
    
    print(f"\n📊 Summary:")
    print(f"  Total new relationships: {total_new_edges}")
    print(f"  Total updated relationships: {total_updated_edges}")
    
    return engine

def demonstrate_search_capabilities(engine):
    """Demonstrate search capabilities on the biographical knowledge graph"""
    print("\n🔍 Searching the Biographical Knowledge Graph...\n")
    
    # Define search queries that should find overlapping facts
    search_queries = [
        "Who lives in Paris?",
        "Who enjoys dancing?", 
        "Who works in technology?",
        "Tell me about photographers",
        "Who was born in Europe?",
        "What do people do for hobbies?",
        "Who relocated from one city to another?"
    ]
    
    for query in search_queries:
        print(f"🔎 Query: '{query}'")
        
        try:
            # Perform search
            result = engine.search(query, k=5)
            
            print(f"   📝 Answer: {result.answer}")
            
            if result.results:
                print(f"   📊 Found {len(result.results)} relevant relationships:")
                for i, search_result in enumerate(result.results[:3], 1):
                    triplet = search_result.triplet
                    score = search_result.score
                    edge = triplet.edge
                    print(f"     {i}. {edge.subject} {edge.relationship} {edge.object} (score: {score:.3f})")
            else:
                print("   📊 No relationships found")
                
        except Exception as e:
            if "API" in str(e) or "authentication" in str(e).lower():
                print(f"   ⚠️ Search requires valid OpenAI API key for answer generation")
                # Still try vector search
                try:
                    results = engine.vector_store.search(query, k=3)
                    if results:
                        print(f"   📊 Vector search found {len(results)} results:")
                        for result in results:
                            edge = result.triplet.edge
                            print(f"     - {edge.subject} {edge.relationship} {edge.object}")
                except Exception as ve:
                    print(f"   ❌ Vector search failed: {ve}")
            else:
                print(f"   ❌ Search error: {e}")
        
        print()  # Empty line between queries

def analyze_graph_structure(engine):
    """Analyze the structure of the created knowledge graph"""
    print("\n📈 Analyzing Graph Structure...\n")
    
    try:
        # Get all edges from the graph database
        all_edges = engine.graph_db.find_edges(filter_obsolete=True)
        
        print(f"📊 Total relationships in graph: {len(all_edges)}")
        
        # Count relationships by type
        relationship_counts = {}
        entity_counts = {}
        location_entities = set()
        person_entities = set()
        
        for triplet in all_edges:
            edge = triplet.edge
            rel_type = edge.relationship
            subject = edge.subject
            obj = edge.object
            
            # Count relationship types
            relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
            
            # Count entities
            entity_counts[subject] = entity_counts.get(subject, 0) + 1
            entity_counts[obj] = entity_counts.get(obj, 0) + 1
            
            # Classify entities
            if rel_type in ['lives_in', 'born_in', 'relocated_to']:
                if 'Johnson' in subject or 'Chen' in subject or 'Rodriguez' in subject or 'Laurent' in subject:
                    person_entities.add(subject)
                    location_entities.add(obj)
                else:
                    location_entities.add(subject)
                    person_entities.add(obj)
            elif rel_type in ['works_as', 'enjoys', 'speaks']:
                person_entities.add(subject)
        
        print(f"\n🔗 Relationship Types:")
        for rel_type, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {rel_type}: {count}")
        
        print(f"\n👥 People in graph: {len(person_entities)}")
        for person in sorted(person_entities):
            print(f"   - {person}")
        
        print(f"\n🌍 Locations in graph: {len(location_entities)}")
        for location in sorted(location_entities):
            print(f"   - {location}")
        
        # Find overlapping facts
        print(f"\n🔄 Overlapping Facts Analysis:")
        
        # People who live in same city
        location_residents = {}
        for triplet in all_edges:
            edge = triplet.edge
            if edge.relationship in ['lives_in']:
                location = edge.object
                person = edge.subject
                if location not in location_residents:
                    location_residents[location] = []
                location_residents[location].append(person)
        
        for location, residents in location_residents.items():
            if len(residents) > 1:
                print(f"   📍 {location}: {', '.join(residents)} (shared location)")
        
        # People with same hobbies
        hobby_enthusiasts = {}
        for triplet in all_edges:
            edge = triplet.edge
            if edge.relationship in ['enjoys']:
                hobby = edge.object
                person = edge.subject
                if hobby not in hobby_enthusiasts:
                    hobby_enthusiasts[hobby] = []
                hobby_enthusiasts[hobby].append(person)
        
        for hobby, people in hobby_enthusiasts.items():
            if len(people) > 1:
                print(f"   🕺 {hobby}: {', '.join(people)} (shared hobby)")
        
    except Exception as e:
        print(f"❌ Graph analysis error: {e}")

def main():
    """Run the biographical knowledge graph example"""
    
    print("🏗️ Knowledge Graph Engine v2 - Biographical Example")
    print("=" * 60)
    print()
    
    print("📚 Biographical Data:")
    print("-" * 30)
    for person, bio in BIOGRAPHIES.items():
        name = person.replace('_', ' ')
        print(f"\n👤 {name}:")
        # Show first 2 sentences of bio
        sentences = bio.split('. ')[:2]
        preview = '. '.join(sentences) + '...'
        print(f"   {preview}")
    
    print("\n" + "=" * 60)
    
    # Extract relationships from biographies
    engine = extract_relationships_from_bio()
    
    if engine:
        # Demonstrate search capabilities
        demonstrate_search_capabilities(engine)
        
        # Analyze graph structure
        analyze_graph_structure(engine)
        
        print("=" * 60)
        print("✅ Biographical Knowledge Graph Example Completed!")
        print("""
💡 Key Demonstrations:
   - Biographical text processing and relationship extraction
   - Overlapping facts detection (Paris residents, dance enthusiasts)
   - Multi-person knowledge graph construction
   - Semantic search across biographical data
   - Graph structure analysis and insights
        """)

if __name__ == "__main__":
    main()