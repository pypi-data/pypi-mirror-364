#!/usr/bin/env python3
"""
Example of using KG Engine v2 as an external package

This example demonstrates how to use all the exported types and classes
from the kg_engine package for building external applications.
"""

def demonstrate_core_api():
    """Demonstrate core API usage - the essentials for basic usage"""
    print("🔧 Core API Usage")
    print("-" * 40)
    
    # Import core components
    from kg_engine import (
        KnowledgeGraphEngineV2, InputItem, Neo4jConfig,
        SearchType, RelationshipStatus, EdgeMetadata, EdgeData
    )
    
    try:
        # Initialize configuration
        config = Neo4jConfig()
        
        # Initialize engine
        engine = KnowledgeGraphEngineV2(
            api_key="your-api-key",
            model="gpt-4o-mini",
            neo4j_config=config
        )
        
        # Create input items
        inputs = [
            InputItem("Alice works at Google as a software engineer"),
            InputItem("Bob lives in San Francisco"),
            InputItem("Charlie enjoys playing tennis")
        ]
        
        # Process inputs
        results = engine.process_input(inputs)
        print(f"✅ Processed {results['processed_items']} items")
        print(f"   New edges: {results['new_edges']}")
        
        # Search the knowledge graph
        search_response = engine.search(
            query="Who works in technology?",
            search_type=SearchType.BOTH,
            k=10
        )
        print(f"✅ Found {len(search_response.results)} search results")
        
        return True
        
    except Exception as e:
        print(f"❌ Core API demo failed: {e}")
        return False

def demonstrate_data_models():
    """Demonstrate working with data models and types"""
    print("\n📊 Data Models Usage")
    print("-" * 40)
    
    from kg_engine import (
        EdgeMetadata, EdgeData, GraphEdge, RelationshipStatus,
        InputItem, parse_date
    )
    from datetime import datetime
    
    try:
        # Create edge metadata
        metadata = EdgeMetadata(
            summary="Alice works at Google",
            confidence=0.95,
            source="external_api",
            from_date=parse_date("2022-01-01"),
            to_date=None,
            status=RelationshipStatus.ACTIVE,
            category="employment"
        )
        
        # Create edge data
        edge_data = EdgeData(
            subject="Alice",
            relationship="WORKS_AT", 
            object="Google",
            metadata=metadata
        )
        
        print(f"✅ Created EdgeData: {edge_data.subject} -> {edge_data.relationship} -> {edge_data.object}")
        print(f"   Confidence: {edge_data.metadata.confidence}")
        print(f"   Category: {edge_data.metadata.category}")
        
        # Create input item with metadata
        input_item = InputItem(
            description="Bob moved to Seattle last year",
            metadata={
                "source": "external_system",
                "timestamp": datetime.now().isoformat(),
                "user_id": "ext_user_123"
            }
        )
        
        print(f"✅ Created InputItem with metadata: {len(input_item.metadata)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Data models demo failed: {e}")
        return False

def demonstrate_advanced_storage():
    """Demonstrate advanced storage operations"""
    print("\n🗄️ Advanced Storage Usage") 
    print("-" * 40)
    
    from kg_engine import GraphDB, VectorStore, Neo4jConfig
    
    try:
        # Initialize storage components
        config = Neo4jConfig()
        graph_db = GraphDB(config)
        vector_store = VectorStore("external_collection", neo4j_config=config)
        
        # Get statistics
        graph_stats = graph_db.get_stats()
        vector_stats = vector_store.get_stats()
        
        print(f"✅ Graph DB Stats: {graph_stats.get('total_relationships', 0)} relationships")
        print(f"✅ Vector Store Stats: {vector_stats.get('total_triplets', 0)} triplets")
        
        # List entities and relationships
        entities = graph_db.get_entities()
        relationships = graph_db.get_relationships()
        
        print(f"✅ Found {len(entities)} entities and {len(relationships)} relationship types")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage demo failed: {e}")
        return False

def demonstrate_schema_management():
    """Demonstrate Neo4j schema management"""
    print("\n🏗️ Schema Management Usage")
    print("-" * 40)
    
    from kg_engine import Neo4jSchemaManager, setup_neo4j_schema, Neo4jConfig
    
    try:
        config = Neo4jConfig()
        
        # Use the convenience function
        schema_results = setup_neo4j_schema(config)
        print(f"✅ Schema setup completed:")
        print(f"   Constraints: {len(schema_results.get('constraints', []))}")
        print(f"   Indexes: {len(schema_results.get('indexes', []))}")
        print(f"   Vector indexes: {len(schema_results.get('vector_indexes', []))}")
        
        # Use the schema manager directly
        schema_manager = Neo4jSchemaManager(config)
        schema_info = schema_manager.get_schema_info()
        
        print(f"✅ Current schema info retrieved:")
        print(f"   Active constraints: {len(schema_info.get('constraints', []))}")
        print(f"   Active indexes: {len(schema_info.get('indexes', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema management demo failed: {e}")
        return False

def demonstrate_utilities():
    """Demonstrate utility functions"""
    print("\n🛠️ Utilities Usage")
    print("-" * 40)
    
    from kg_engine import (
        parse_date, GraphQueryOptimizer, Neo4jOptimizer, 
        QueryType, Neo4jConfig
    )
    
    try:
        # Date parsing
        dates = [
            "2024-01-15",
            "January 15, 2024", 
            "last week",
            "invalid date"
        ]
        
        print("Date parsing results:")
        for date_str in dates:
            parsed = parse_date(date_str)
            print(f"  '{date_str}' -> {parsed}")
        
        # Query optimization
        config = Neo4jConfig()
        optimizer = GraphQueryOptimizer(config)
        
        # Show available query types
        query_types = [qt for qt in QueryType]
        print(f"✅ Available query types: {[qt.value for qt in query_types]}")
        
        # Neo4j optimization
        neo4j_optimizer = Neo4jOptimizer(config)
        print("✅ Neo4j optimizer initialized for performance analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities demo failed: {e}")
        return False

def demonstrate_llm_interface():
    """Demonstrate LLM interface usage"""
    print("\n🤖 LLM Interface Usage")
    print("-" * 40)
    
    from kg_engine import LLMInterface, ClassifierMap, Neo4jConfig, GraphDB
    
    try:
        # Initialize components needed for LLM interface
        config = Neo4jConfig()
        graph_db = GraphDB(config)
        classifier_map = ClassifierMap(graph_db)
        
        # Initialize LLM interface (would need real API key in practice)
        llm = LLMInterface(
            api_key="test-key",
            model="gpt-4o-mini",
            classifier_map=classifier_map
        )
        
        print("✅ LLM Interface initialized")
        print(f"   Model: {llm.model}")
        print("   Ready for entity/relationship extraction")
        
        # Note: In a real application, you would use:
        # extracted = llm.extract_entities_relationships("Your text here")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM interface demo failed: {e}")
        return False

def show_api_categories():
    """Show all available API categories"""
    print("\n📚 Available API Categories")
    print("=" * 50)
    
    from kg_engine import (
        __core_api__, __config_api__, __storage_api__, 
        __llm_api__, __utils_api__, __all__
    )
    
    categories = {
        "Core API (Essential)": __core_api__,
        "Configuration API": __config_api__, 
        "Storage API (Advanced)": __storage_api__,
        "LLM API (Advanced)": __llm_api__,
        "Utilities API": __utils_api__
    }
    
    for category, items in categories.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")
    
    print(f"\nTotal exported items: {len(__all__)}")

def main():
    """Run all demonstrations"""
    print("🚀 KG Engine v2 - External API Usage Examples")
    print("=" * 60)
    
    # Show available APIs
    show_api_categories()
    
    # Run demonstrations
    demos = [
        ("Core API", demonstrate_core_api),
        ("Data Models", demonstrate_data_models), 
        ("Advanced Storage", demonstrate_advanced_storage),
        ("Schema Management", demonstrate_schema_management),
        ("Utilities", demonstrate_utilities),
        ("LLM Interface", demonstrate_llm_interface)
    ]
    
    passed = 0
    total = len(demos)
    
    for name, demo_func in demos:
        try:
            if demo_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} demo failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} demos completed successfully")
    
    if passed == total:
        print("✅ All API exports are working correctly!")
    else:
        print("⚠️ Some demos had issues - check error messages above")
    
    print("\n💡 Usage Tips:")
    print("- Import only what you need: from kg_engine import KnowledgeGraphEngineV2, InputItem")
    print("- Use __core_api__ exports for basic usage")
    print("- Use advanced APIs (__storage_api__, __llm_api__) for custom implementations")
    print("- All types are properly typed for IDE support")

if __name__ == "__main__":
    main()