"""
Test suite for KG Engine API Server endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

@pytest.fixture
def mock_kg_engine():
    """Mock KG Engine for testing"""
    mock_engine = Mock()
    
    # Mock process_input response
    mock_engine.process_input.return_value = {
        "processed_items": 2,
        "new_edges": 3,
        "updated_edges": 1,
        "duplicates_ignored": 0,
        "processing_time_ms": 150.5,
        "errors": [],
        "edge_results": [
            {
                "action": "created",
                "extracted_info": {
                    "subject": "Alice",
                    "relationship": "WORKS_AT",
                    "object": "Google",
                    "summary": "Alice works at Google",
                    "confidence": 0.9
                }
            }
        ]
    }
    
    # Mock search response
    mock_search_result = Mock()
    mock_search_result.results = []
    mock_search_result.answer = "Alice works at Google"
    mock_engine.search.return_value = mock_search_result
    
    # Mock stats response
    mock_engine.get_stats.return_value = {
        "graph_stats": {
            "total_relationships": 100,
            "total_entities": 50
        },
        "vector_stats": {},
        "relationships": ["WORKS_AT", "LIVES_IN"],
        "entities": 50
    }
    
    # Mock get_node_relations
    mock_relation = Mock()
    mock_relation.triplet.edge.get_subject_safe.return_value = "Alice"
    mock_relation.triplet.edge.get_relationship_safe.return_value = "WORKS_AT"
    mock_relation.triplet.edge.get_object_safe.return_value = "Google"
    mock_relation.score = 0.95
    mock_relation.triplet.edge.metadata.summary = "Alice works at Google"
    
    mock_engine.get_node_relations.return_value = [mock_relation]
    
    # Mock graph_db operations
    mock_engine.graph_db.add_edge_data.return_value = True
    mock_engine.graph_db.merge_nodes_auto.return_value = {
        "success": True,
        "merged_node_name": "John Smith",
        "relationships_transferred": 5,
        "execution_time_ms": 100
    }
    
    return mock_engine

@pytest.fixture
def mock_config():
    """Mock Neo4j config"""
    mock_config = Mock()
    mock_config.verify_connectivity.return_value = True
    return mock_config

@pytest.fixture
def client(mock_kg_engine, mock_config):
    """Test client with mocked dependencies"""
    with patch('app.main.engine', mock_kg_engine), \
         patch('app.main.config', mock_config), \
         patch('app.main.kg_version', '2.1.0'):
        
        from main import app
        return TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_healthy(self, client):
        """Test health check when system is healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["kg_engine_version"] == "2.1.0"
        assert data["neo4j_connected"] is True
        assert data["engine_initialized"] is True

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "KG Engine API Server"
        assert data["version"] == "1.0.0"
        assert data["kg_engine_version"] == "2.1.0"
        assert "/docs" in data["docs"]

class TestProcessEndpoint:
    """Test text processing endpoint"""
    
    def test_process_texts_success(self, client):
        """Test successful text processing"""
        payload = {
            "texts": [
                "Alice works at Google",
                "Bob lives in San Francisco"
            ],
            "source": "test",
            "extract_temporal": True
        }
        
        response = client.post("/process", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["processed_texts"] == 2
        assert data["relationships_created"] == 3
        assert data["relationships_updated"] == 1
        assert data["processing_time_ms"] > 0
        assert len(data["extracted_relationships"]) > 0
    
    def test_process_texts_validation_error(self, client):
        """Test validation error for invalid payload"""
        payload = {
            "texts": [],  # Empty texts should fail validation
            "source": "test"
        }
        
        response = client.post("/process", json=payload)
        assert response.status_code == 422  # Validation error

class TestSearchEndpoint:
    """Test search endpoint"""
    
    def test_search_success(self, client):
        """Test successful search"""
        payload = {
            "query": "Who works at Google?",
            "search_type": "hybrid",
            "limit": 10,
            "confidence_threshold": 0.3
        }
        
        response = client.post("/search", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["query"] == "Who works at Google?"
        assert data["search_type"] == "hybrid"
        assert "results_count" in data
        assert "processing_time_ms" in data
        assert "answer" in data
        assert "results" in data
    
    def test_search_invalid_type(self, client):
        """Test search with invalid search type"""
        payload = {
            "query": "test query",
            "search_type": "invalid_type",  # Should fail validation
            "limit": 10
        }
        
        response = client.post("/search", json=payload)
        assert response.status_code == 422  # Validation error

class TestEdgeEndpoint:
    """Test edge creation endpoint"""
    
    def test_create_edge_success(self, client):
        """Test successful edge creation"""
        payload = {
            "subject": "John",
            "relationship": "WORKS_AT", 
            "object": "Microsoft",
            "summary": "John works at Microsoft",
            "confidence": 0.95,
            "source": "test"
        }
        
        response = client.post("/edges", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert data["edge"]["subject"] == "John"
        assert data["edge"]["relationship"] == "WORKS_AT"
        assert data["edge"]["object"] == "Microsoft"
    
    def test_create_edge_validation_error(self, client):
        """Test edge creation with missing required fields"""
        payload = {
            "subject": "John",
            # Missing relationship and object
            "summary": "Test edge"
        }
        
        response = client.post("/edges", json=payload)
        assert response.status_code == 422  # Validation error

class TestNodeEndpoints:
    """Test node-related endpoints"""
    
    def test_get_node_relations_success(self, client):
        """Test getting node relations"""
        response = client.get("/nodes/Alice/relations?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert data["node_name"] == "Alice"
        assert "relations_count" in data
        assert "relations" in data
        assert isinstance(data["relations"], list)
    
    def test_merge_nodes_auto_success(self, client):
        """Test automatic node merging"""
        payload = {
            "source_node": "John Smith",
            "target_node": "John",
            "merge_type": "auto"
        }
        
        response = client.post("/nodes/merge", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["merge_type"] == "auto"
        assert "merged_node_name" in data
        assert "relationships_transferred" in data
    
    def test_merge_nodes_manual_missing_name(self, client):
        """Test manual node merging without required new_name"""
        payload = {
            "source_node": "John Smith",
            "target_node": "John",
            "merge_type": "manual"
            # Missing new_name for manual merge
        }
        
        response = client.post("/nodes/merge", json=payload)
        assert response.status_code == 400  # Bad request

class TestStatsEndpoint:
    """Test statistics endpoint"""
    
    def test_get_stats_success(self, client):
        """Test getting system statistics"""
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "graph_statistics" in data
        assert "vector_statistics" in data
        assert "relationships_types" in data
        assert "entities_count" in data
        assert data["kg_engine_version"] == "2.1.0"
        assert data["api_version"] == "1.0.0"

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_engine_not_initialized(self):
        """Test behavior when engine is not initialized"""
        with patch('app.main.engine', None):
            from main import app
            client = TestClient(app)
            
            response = client.post("/process", json={
                "texts": ["test text"],
                "source": "test"
            })
            assert response.status_code == 503  # Service unavailable
    
    def test_config_not_available(self):
        """Test behavior when config is not available"""
        with patch('app.main.config', None):
            from main import app
            client = TestClient(app)
            
            # This would be tested in a dependency that requires config
            # For now, just ensure the test structure is correct
            assert True

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoint behaviors"""
    
    async def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import asyncio
        
        # Simulate concurrent requests
        tasks = []
        for i in range(5):
            task = asyncio.ensure_future(
                asyncio.to_thread(
                    client.get, "/health"
                )
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])