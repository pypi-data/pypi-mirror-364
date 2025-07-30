#!/usr/bin/env python3
"""
Example usage of the Node Merge API endpoints

This example demonstrates how to use both automatic and manual node merging
through the REST API endpoints.
"""
import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"

def create_sample_nodes():
    """Create sample nodes for merging demonstration"""
    print("📝 Creating sample nodes...")
    
    nodes = [
        {
            "name": "John Smith",
            "node_type": "Person",
            "properties": {
                "age": 35,
                "profession": "Data Scientist",
                "location": "New York",
                "company": "TechCorp"
            }
        },
        {
            "name": "J. Smith",
            "node_type": "Person",
            "properties": {
                "age": 35,
                "title": "Senior Data Scientist",
                "email": "j.smith@techcorp.com",
                "phone": "+1-555-0123"
            }
        }
    ]
    
    for node in nodes:
        response = requests.post(f"{BASE_URL}/nodes", json=node)
        if response.status_code == 201:
            print(f"✅ Created: {node['name']}")
        else:
            print(f"⚠️ Failed to create {node['name']}: {response.text}")
    
    return nodes

def demonstrate_manual_merge():
    """Demonstrate manual node merging with precise control"""
    print("\n🔧 Manual Node Merge Example")
    print("-" * 40)
    
    # Manual merge request
    merge_request = {
        "source_node": "John Smith",
        "target_node": "J. Smith", 
        "new_name": "John Smith",
        "new_properties": {
            "type": "Person",
            "age": 35,
            "profession": "Senior Data Scientist",
            "location": "New York",
            "company": "TechCorp",
            "email": "j.smith@techcorp.com",
            "phone": "+1-555-0123",
            "aliases": ["J. Smith"],
            "verified": True
        }
    }
    
    print("Request payload:")
    print(json.dumps(merge_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/nodes/merge-manual", json=merge_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Manual merge completed successfully!")
        print(f"   Merged node: {result['merged_node_name']}")
        print(f"   Success: {result['success']}")
        print(f"   Relationships transferred: {result['relationships_transferred']}")
        print(f"   Nodes deleted: {result['nodes_deleted']}")
        print(f"   Execution time: {result['execution_time_ms']:.2f}ms")
        
        if result.get('details'):
            print(f"   Details: {result['details']}")
            
    else:
        print(f"❌ Manual merge failed: {response.status_code}")
        print(f"Response: {response.text}")

def demonstrate_auto_merge():
    """Demonstrate automatic node merging using LLM intelligence"""
    print("\n🤖 Automatic Node Merge Example") 
    print("-" * 40)
    
    # First recreate nodes for auto merge
    create_sample_nodes()
    
    # Auto merge request
    merge_request = {
        "source_node": "John Smith",
        "target_node": "J. Smith",
        "merge_strategy": "intelligent"
    }
    
    print("Request payload:")
    print(json.dumps(merge_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/nodes/merge-auto", json=merge_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Auto merge completed successfully!")
        print(f"   Merged node: {result['merged_node_name']}")
        print(f"   Success: {result['success']}")
        print(f"   Relationships transferred: {result['relationships_transferred']}")
        print(f"   Nodes deleted: {result['nodes_deleted']}")
        print(f"   Execution time: {result['execution_time_ms']:.2f}ms")
        
        if result.get('details'):
            print(f"   Details: {result['details']}")
            
    else:
        print(f"❌ Auto merge failed: {response.status_code}")
        print(f"Response: {response.text}")

def check_api_health():
    """Check if the API server is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"   Neo4j Connected: {health['neo4j_connected']}")
            print(f"   Engine Initialized: {health['engine_initialized']}")
            print(f"   Version: {health['version']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print(f"   Make sure the server is running at {BASE_URL}")
        return False

def main():
    """Main example execution"""
    print("🚀 Node Merge API Examples")
    print("=" * 50)
    
    # Check API health
    if not check_api_health():
        print("\n💡 To start the API server:")
        print("   cd src/api && python main.py")
        return
    
    print("\n" + "=" * 50)
    
    # Create sample data
    create_sample_nodes()
    
    # Demonstrate manual merge
    demonstrate_manual_merge()
    
    # Demonstrate auto merge  
    demonstrate_auto_merge()
    
    print("\n" + "=" * 50)
    print("✅ Node merge examples completed!")
    print("\n📚 API Documentation available at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()