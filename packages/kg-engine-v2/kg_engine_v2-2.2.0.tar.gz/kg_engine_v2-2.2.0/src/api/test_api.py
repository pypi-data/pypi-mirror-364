#!/usr/bin/env python3
"""
Test script for Knowledge Graph Engine API
"""

import requests
import json
from uuid import uuid4
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data['engine_initialized']

def test_process_input(user_id):
    """Test processing natural language input"""
    print_section("Testing Process Input")
    
    # Biographical data
    descriptions = [
        "Emma Johnson works as a software engineer at Google",
        "Emma lives in Mountain View, California",
        "Emma graduated from Stanford University in 2018",
        "Marcus Chen is an entrepreneur and founder of TechStartup Inc",
        "Marcus lives in San Francisco",
        "Emma and Marcus met at a tech conference in 2020",
        "Sarah Williams works as a data scientist at Microsoft",
        "Sarah enjoys hiking and photography in her free time"
    ]
    
    request_data = {
        "user_id": str(user_id),
        "descriptions": descriptions,
        "metadata": {
            "source": "test_script",
            "test_run": datetime.now().isoformat()
        }
    }
    
    print(f"User ID: {user_id}")
    print(f"Processing {len(descriptions)} descriptions...")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/process",
        json=request_data
    )
    elapsed = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"  Processed items: {data['processed_items']}")
        print(f"  New edges: {data['new_edges']}")
        print(f"  Updated edges: {data['updated_edges']}")
        print(f"  Processing time: {data['processing_time_ms']:.1f}ms")
        print(f"  API round trip: {elapsed:.1f}ms")
        
        if data['errors']:
            print(f"  ⚠️ Errors: {data['errors']}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

def test_search(user_id=None):
    """Test search functionality"""
    print_section("Testing Search")
    
    test_queries = [
        {
            "query": "Who works at Google?",
            "search_type": "both",
            "user_id": str(user_id) if user_id else None
        },
        {
            "query": "Who works in technology?",
            "search_type": "vector",
            "user_id": str(user_id) if user_id else None
        },
        {
            "query": "Tell me about Emma Johnson",
            "search_type": "both",
            "user_id": str(user_id) if user_id else None
        },
        {
            "query": "Who lives in California?",
            "search_type": "both",
            "user_id": str(user_id) if user_id else None,
            "k": 5
        }
    ]
    
    for query_data in test_queries:
        print(f"\n🔍 Query: '{query_data['query']}'")
        print(f"   Type: {query_data['search_type']}")
        if query_data.get('user_id'):
            print(f"   User filter: {query_data['user_id'][:8]}...")
        
        response = requests.post(
            f"{BASE_URL}/search",
            json=query_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📝 Answer: {data['answer']}")
            print(f"   📊 Results: {data['total_results']}")
            
            if data['results']:
                print("   Top matches:")
                for i, result in enumerate(data['results'][:3], 1):
                    print(f"     {i}. {result['subject']} {result['relationship']} {result['object']}")
                    print(f"        Confidence: {result['confidence']:.3f}")
        else:
            print(f"   ❌ Error: {response.status_code}")

def test_stats(user_id=None):
    """Test statistics endpoint"""
    print_section("Testing Statistics")
    
    params = {}
    if user_id:
        params['user_id'] = str(user_id)
        print(f"Filtering by user: {user_id}")
    
    response = requests.get(f"{BASE_URL}/stats", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 System Statistics:")
        
        if 'graph_stats' in data:
            print(f"   Graph Database:")
            for key, value in data['graph_stats'].items():
                print(f"     - {key}: {value}")
        
        if 'vector_stats' in data:
            print(f"   Vector Store:")
            for key, value in data['vector_stats'].items():
                print(f"     - {key}: {value}")
        
        if 'filter_applied' in data:
            print(f"   Filter: {data['filter_applied']}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_concurrent_users():
    """Test multi-tenant functionality with different users"""
    print_section("Testing Multi-Tenant Support")
    
    # Create two different users
    user1_id = uuid4()
    user2_id = uuid4()
    
    print(f"User 1: {user1_id}")
    print(f"User 2: {user2_id}")
    
    # Add data for user 1
    print("\n📝 Adding data for User 1...")
    response = requests.post(f"{BASE_URL}/process", json={
        "user_id": str(user1_id),
        "descriptions": [
            "Alice works at Company A",
            "Alice specializes in machine learning"
        ]
    })
    print(f"   Status: {response.status_code}")
    
    # Add data for user 2
    print("\n📝 Adding data for User 2...")
    response = requests.post(f"{BASE_URL}/process", json={
        "user_id": str(user2_id),
        "descriptions": [
            "Bob works at Company B",
            "Bob specializes in web development"
        ]
    })
    print(f"   Status: {response.status_code}")
    
    # Search as user 1 (should only see Alice)
    print("\n🔍 Searching as User 1...")
    response = requests.post(f"{BASE_URL}/search", json={
        "query": "Who works at a company?",
        "search_type": "both",
        "user_id": str(user1_id)
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Results: {len(data['results'])}")
        for result in data['results']:
            print(f"   - {result['subject']} {result['relationship']} {result['object']}")

def main():
    """Run all API tests"""
    print("🧪 Knowledge Graph Engine API Test Suite")
    print(f"📍 Testing against: {BASE_URL}")
    
    # Check if API is running
    try:
        if not test_health():
            print("\n❌ API is not properly initialized. Please check the server.")
            return
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {BASE_URL}")
        print("Please make sure the API is running: python src/api/run_api.py")
        return
    
    # Create a test user
    test_user_id = uuid4()
    
    # Run tests
    test_process_input(test_user_id)
    time.sleep(1)  # Give the system time to process
    
    test_search(test_user_id)
    test_stats(test_user_id)
    test_concurrent_users()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()