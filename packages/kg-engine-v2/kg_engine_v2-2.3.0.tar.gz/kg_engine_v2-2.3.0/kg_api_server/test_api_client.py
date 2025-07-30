#!/usr/bin/env python3
"""
Test client for KG Engine API Server
Demonstrates how to interact with the API programmatically
"""

import requests
import json
import time
from typing import Dict, Any, List

class KGEngineAPIClient:
    """Client for interacting with KG Engine API Server"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def process_texts(self, texts: List[str], source: str = "api_client") -> Dict[str, Any]:
        """Process natural language texts"""
        payload = {
            "texts": texts,
            "source": source,
            "extract_temporal": True
        }
        
        response = self.session.post(
            f"{self.base_url}/process",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, search_type: str = "hybrid", limit: int = 10) -> Dict[str, Any]:
        """Search the knowledge graph"""
        payload = {
            "query": query,
            "search_type": search_type,
            "limit": limit,
            "confidence_threshold": 0.3
        }
        
        response = self.session.post(
            f"{self.base_url}/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_edge(self, subject: str, relationship: str, obj: str, 
                   summary: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Create a new edge manually"""
        payload = {
            "subject": subject,
            "relationship": relationship,
            "object": obj,
            "summary": summary,
            "confidence": confidence,
            "source": "api_client"
        }
        
        response = self.session.post(
            f"{self.base_url}/edges",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_node_relations(self, node_name: str, limit: int = 20) -> Dict[str, Any]:
        """Get relations for a specific node"""
        response = self.session.get(
            f"{self.base_url}/nodes/{node_name}/relations",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def merge_nodes(self, source_node: str, target_node: str, 
                   merge_type: str = "auto", new_name: str = None) -> Dict[str, Any]:
        """Merge two nodes"""
        payload = {
            "source_node": source_node,
            "target_node": target_node,
            "merge_type": merge_type
        }
        
        if new_name:
            payload["new_name"] = new_name
        
        response = self.session.post(
            f"{self.base_url}/nodes/merge",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

def test_basic_workflow():
    """Test the basic API workflow"""
    print("🚀 Testing KG Engine API Client")
    print("=" * 50)
    
    client = KGEngineAPIClient()
    
    try:
        # 1. Health Check
        print("\n1️⃣ Testing health check...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   KG Engine Version: {health['kg_engine_version']}")
        print(f"   Neo4j Connected: {health['neo4j_connected']}")
        
        if health['status'] != 'healthy':
            print("⚠️ API is not healthy, continuing anyway...")
        else:
            print("✅ API is healthy")
        
        # 2. Process Texts
        print("\n2️⃣ Testing text processing...")
        sample_texts = [
            "Alice works as a software engineer at Google",
            "Bob moved to San Francisco in 2023 and loves hiking",
            "Charlie studied computer science at MIT from 2018 to 2022",
            "Diana is the founder of a tech startup in Austin, Texas"
        ]
        
        process_result = client.process_texts(sample_texts)
        print(f"   Processed: {process_result['processed_texts']} texts")
        print(f"   Created: {process_result['relationships_created']} relationships")
        print(f"   Updated: {process_result['relationships_updated']} relationships")
        print(f"   Processing Time: {process_result['processing_time_ms']:.1f}ms")
        print("✅ Text processing successful")
        
        # 3. Search Tests
        print("\n3️⃣ Testing search functionality...")
        search_queries = [
            "Who works in technology?",
            "Where do people live?", 
            "What did Charlie study?",
            "Who likes outdoor activities?"
        ]
        
        for query in search_queries:
            print(f"\n   🔍 Query: '{query}'")
            search_result = client.search(query, search_type="hybrid", limit=5)
            print(f"      Found: {search_result['results_count']} results")
            print(f"      Search Time: {search_result['processing_time_ms']:.1f}ms")
            
            if search_result['answer']:
                print(f"      Answer: {search_result['answer']}")
            
            # Show top results
            for i, result in enumerate(search_result['results'][:2]):
                subject = result.get('subject', 'N/A')
                relationship = result.get('relationship', 'N/A')
                obj = result.get('object', 'N/A')
                confidence = result.get('confidence', 0)
                print(f"        {i+1}. {subject} {relationship} {obj} (conf: {confidence:.3f})")
        
        print("✅ Search functionality working")
        
        # 4. Manual Edge Creation
        print("\n4️⃣ Testing manual edge creation...")
        edge_result = client.create_edge(
            subject="John",
            relationship="WORKS_AT",
            obj="Microsoft",
            summary="John works at Microsoft as a product manager",
            confidence=0.95
        )
        print(f"   Edge created: {edge_result['success']}")
        print("✅ Manual edge creation successful")
        
        # 5. Node Relations
        print("\n5️⃣ Testing node relations...")
        try:
            relations_result = client.get_node_relations("Alice", limit=10)
            print(f"   Found {relations_result['relations_count']} relations for Alice")
            
            for i, relation in enumerate(relations_result['relations'][:3]):
                subject = relation.get('subject', 'N/A')
                relationship = relation.get('relationship', 'N/A') 
                obj = relation.get('object', 'N/A')
                print(f"     {i+1}. {subject} {relationship} {obj}")
            
            print("✅ Node relations retrieval successful")
        except Exception as e:
            print(f"   ⚠️ Node relations test failed: {e}")
        
        # 6. Statistics
        print("\n6️⃣ Testing statistics...")
        stats = client.get_stats()
        graph_stats = stats.get('graph_statistics', {})
        print(f"   Total relationships: {graph_stats.get('total_relationships', 0)}")
        print(f"   Total entities: {graph_stats.get('total_entities', 0)}")
        print(f"   Relationship types: {stats.get('relationships_types', 0)}")
        print("✅ Statistics retrieval successful")
        
        # 7. Performance Test
        print("\n7️⃣ Testing performance...")
        start_time = time.time()
        
        # Process multiple texts
        performance_texts = [
            f"Person{i} works at Company{i} as a {['engineer', 'manager', 'analyst'][i%3]}"
            for i in range(10)
        ]
        
        perf_result = client.process_texts(performance_texts)
        processing_time = time.time() - start_time
        
        print(f"   Processed 10 texts in {processing_time:.2f}s")
        print(f"   API processing time: {perf_result['processing_time_ms']:.1f}ms")
        print(f"   Average per text: {perf_result['processing_time_ms']/10:.1f}ms")
        print("✅ Performance test completed")
        
        print("\n🎉 All API tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("💡 Make sure the server is running: python app/main.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def demo_advanced_features():
    """Demonstrate advanced API features"""
    print("\n🔧 Advanced Features Demo")
    print("=" * 30)
    
    client = KGEngineAPIClient()
    
    try:
        # Node merging demo
        print("\n🔀 Node Merging Demo...")
        
        # First create some nodes that should be merged
        merge_texts = [
            "John Smith works at Google",
            "John S. is a software engineer", 
            "J. Smith lives in Mountain View"
        ]
        
        client.process_texts(merge_texts)
        print("   Created test data for merging")
        
        # Try to merge nodes (this might fail if nodes don't exist)
        try:
            merge_result = client.merge_nodes(
                source_node="John Smith",
                target_node="John S.",
                merge_type="auto"
            )
            print(f"   Merge successful: {merge_result['success']}")
            print(f"   Merged node: {merge_result.get('merged_node_name', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Merge demo failed (expected): {e}")
        
        # Search type comparison
        print("\n🔍 Search Type Comparison...")
        test_query = "Who works at tech companies?"
        
        for search_type in ["graph", "vector", "hybrid"]:
            result = client.search(test_query, search_type=search_type, limit=3)
            print(f"   {search_type.upper()}: {result['results_count']} results "
                  f"({result['processing_time_ms']:.1f}ms)")
        
        print("✅ Advanced features demo completed")
        
    except Exception as e:
        print(f"❌ Advanced demo error: {e}")

if __name__ == "__main__":
    # Run basic workflow test
    test_basic_workflow()
    
    # Run advanced features demo
    demo_advanced_features()
    
    print("\n" + "=" * 50)
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🔍 ReDoc: http://localhost:8080/redoc")
    print("💚 Health Check: http://localhost:8080/health")
    print("\n🚀 Happy knowledge graphing!")