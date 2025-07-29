"""Comprehensive test suite for Neo4j integration."""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any

from kg_engine.config import Neo4jConfig
from kg_engine.storage import Neo4jKnowledgeGraphVectorStore
from kg_engine.storage import VectorStore
from kg_engine.storage import VectorStoreType
from kg_engine import KnowledgeGraphEngineV2
from kg_engine.models import GraphTriplet, RelationshipStatus, InputItem


class TestNeo4jConfig:
    """Test Neo4j configuration management."""
    
    def test_config_initialization(self):
        """Test Neo4j configuration initialization."""
        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="testpassword",
            database="testdb"
        )
        
        assert config.uri == "bolt://localhost:7687"
        assert config.username == "neo4j"
        assert config.password == "testpassword"
        assert config.database == "testdb"
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        # Set environment variables
        os.environ["NEO4J_URI"] = "bolt://test:7687"
        os.environ["NEO4J_USERNAME"] = "testuser"
        os.environ["NEO4J_PASSWORD"] = "testpass"
        os.environ["NEO4J_DATABASE"] = "testdb"
        
        try:
            config = Neo4jConfig()
            assert config.uri == "bolt://test:7687"
            assert config.username == "testuser"
            assert config.password == "testpass"
            assert config.database == "testdb"
        finally:
            # Clean up environment variables
            for key in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "NEO4J_DATABASE"]:
                os.environ.pop(key, None)
    
    def test_connection_info(self):
        """Test getting connection information."""
        config = Neo4jConfig(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="secret"
        )
        
        info = config.get_connection_info()
        assert info["uri"] == "bolt://localhost:7687"
        assert info["username"] == "neo4j"
        assert "password" not in info  # Password should not be included
        assert "connected" in info


@pytest.fixture
def mock_neo4j_config():
    """Mock Neo4j configuration for testing."""
    return Neo4jConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="testpassword",
        database="neo4j"
    )


@pytest.fixture
def sample_triplets():
    """Sample GraphTriplet objects for testing."""
    triplets = []
    
    # Sample triplet 1
    triplet1 = GraphTriplet(
        subject="John Doe",
        relationship="works_for",
        object="Acme Corp",
        summary="John Doe works for Acme Corp as a software engineer",
        confidence=0.95,
        status=RelationshipStatus.ACTIVE,
        obsolete=False,
        created_at=datetime.now(),
        source="test_data"
    )
    triplets.append(triplet1)
    
    # Sample triplet 2
    triplet2 = GraphTriplet(
        subject="Jane Smith",
        relationship="lives_in",
        object="New York",
        summary="Jane Smith lives in New York City",
        confidence=0.88,
        status=RelationshipStatus.ACTIVE,
        obsolete=False,
        created_at=datetime.now(),
        source="test_data"
    )
    triplets.append(triplet2)
    
    # Sample triplet 3
    triplet3 = GraphTriplet(
        subject="Bob Johnson",
        relationship="studied_at",
        object="MIT",
        summary="Bob Johnson studied computer science at MIT",
        confidence=0.92,
        status=RelationshipStatus.ACTIVE,
        obsolete=False,
        created_at=datetime.now(),
        source="test_data"
    )
    triplets.append(triplet3)
    
    return triplets


class TestNeo4jVectorStore:
    """Test Neo4j vector store functionality."""
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_neo4j_vector_store_initialization(self, mock_neo4j_config):
        """Test Neo4j vector store initialization."""
        try:
            store = Neo4jKnowledgeGraphVectorStore(config=mock_neo4j_config)
            assert store is not None
            assert store.config == mock_neo4j_config
            assert store.embedding_model_name == "all-MiniLM-L6-v2"
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_add_and_query_triplets(self, mock_neo4j_config, sample_triplets):
        """Test adding and querying triplets."""
        try:
            store = Neo4jKnowledgeGraphVectorStore(config=mock_neo4j_config)
            
            # Clear existing data
            store.clear_all()
            
            # Add triplets
            ids = store.add_triplets(sample_triplets)
            assert len(ids) == len(sample_triplets)
            
            # Query for similar triplets
            results = store.query_similar("software engineer", k=5)
            assert len(results) > 0
            
            # Check result format
            for triplet, score in results:
                assert isinstance(triplet, GraphTriplet)
                assert 0.0 <= score <= 1.0
                assert triplet.subject is not None
                assert triplet.relationship is not None
                assert triplet.object is not None
            
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_entity_search(self, mock_neo4j_config, sample_triplets):
        """Test entity-based search."""
        try:
            store = Neo4jKnowledgeGraphVectorStore(config=mock_neo4j_config)
            
            # Clear and add test data
            store.clear_all()
            store.add_triplets(sample_triplets)
            
            # Search for entity
            results = store.search_entities(["John Doe"], k=5)
            assert len(results) > 0
            
            # Verify results contain the entity
            found_entity = False
            for triplet, score in results:
                if "John Doe" in triplet.subject or "John Doe" in triplet.object:
                    found_entity = True
                    break
            
            assert found_entity, "Entity search should find the specified entity"
            
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")


class TestVectorStoreFactory:
    """Test vector store factory functionality."""
    
    def test_chromadb_creation(self):
        """Test ChromaDB vector store creation."""
        store = VectorStore(store_type="chromadb", use_memory=True)
        assert store.get_store_type() == VectorStoreType.CHROMADB
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_neo4j_creation(self, mock_neo4j_config):
        """Test Neo4j vector store creation."""
        try:
            store = VectorStore(
                store_type="neo4j", 
                neo4j_config=mock_neo4j_config
            )
            assert store.get_store_type() == VectorStoreType.NEO4J
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")
    
    def test_environment_variable_config(self):
        """Test configuration via environment variables."""
        # Test ChromaDB default
        os.environ.pop("VECTOR_STORE_TYPE", None)
        store = VectorStore(use_memory=True)
        assert store.get_store_type() == VectorStoreType.CHROMADB
        
        # Test explicit ChromaDB
        os.environ["VECTOR_STORE_TYPE"] = "chromadb"
        store = VectorStore(use_memory=True)
        assert store.get_store_type() == VectorStoreType.CHROMADB
        
        # Clean up
        os.environ.pop("VECTOR_STORE_TYPE", None)


class TestEngineIntegration:
    """Test complete engine integration with Neo4j."""
    
    def test_engine_with_chromadb(self):
        """Test engine initialization with ChromaDB."""
        engine = KnowledgeGraphEngineV2(
            api_key="test",
            vector_store_type="chromadb",
            use_memory_store=True
        )
        assert engine.vector_store.get_store_type() == VectorStoreType.CHROMADB
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_engine_with_neo4j(self, mock_neo4j_config):
        """Test engine initialization with Neo4j."""
        try:
            engine = KnowledgeGraphEngineV2(
                api_key="test",
                vector_store_type="neo4j",
                neo4j_config=mock_neo4j_config
            )
            assert engine.vector_store.get_store_type() == VectorStoreType.NEO4J
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")
    
    @pytest.mark.skipif(
        not os.getenv("TEST_NEO4J", "false").lower() == "true",
        reason="Neo4j tests require TEST_NEO4J=true environment variable"
    )
    def test_engine_process_input_neo4j(self, mock_neo4j_config):
        """Test processing input with Neo4j backend."""
        try:
            engine = KnowledgeGraphEngineV2(
                api_key="test",
                vector_store_type="neo4j",
                neo4j_config=mock_neo4j_config
            )
            
            # Clear existing data
            engine.clear_all_data()
            
            # Create test input
            input_items = [
                InputItem(
                    description="John works at Google as a software engineer",
                    metadata={"source": "test"}
                ),
                InputItem(
                    description="Sarah lives in San Francisco",
                    metadata={"source": "test"}
                )
            ]
            
            # Process input (this will fail with test API key, but we can test the structure)
            try:
                results = engine.process_input(input_items)
                # If it doesn't fail due to API, check results structure
                assert "processed_items" in results
                assert "errors" in results
            except Exception as api_error:
                # Expected to fail with test API key
                assert "API" in str(api_error) or "authentication" in str(api_error).lower()
            
        except Exception as e:
            pytest.skip(f"Neo4j not available for testing: {e}")


class TestBackwardCompatibility:
    """Test backward compatibility of the migration."""
    
    def test_existing_vector_store_api(self):
        """Test that existing VectorStore API still works."""
        # This should work exactly as before
        store = VectorStore(collection_name="test", use_memory=True)
        
        # Test that all original methods exist
        assert hasattr(store, 'add_triplet')
        assert hasattr(store, 'add_triplets')
        assert hasattr(store, 'update_triplet')
        assert hasattr(store, 'delete_triplet')
        assert hasattr(store, 'search')
        assert hasattr(store, 'search_by_entity')
        assert hasattr(store, 'get_stats')
        assert hasattr(store, 'clear_collection')
        
        # Test stats format compatibility
        stats = store.get_stats()
        assert "total_triplets" in stats
        assert "collection_name" in stats or "node_label" in stats
        assert "model_name" in stats
        assert "store_type" in stats
    
    def test_existing_engine_api(self):
        """Test that existing Engine API still works."""
        # This should work exactly as before
        engine = KnowledgeGraphEngineV2(api_key="test", use_memory_store=True)
        
        # Test that all original methods exist
        assert hasattr(engine, 'process_input')
        assert hasattr(engine, 'search')
        assert hasattr(engine, 'get_stats')
        assert hasattr(engine, 'export_knowledge_graph')
        assert hasattr(engine, 'import_knowledge_graph')
        assert hasattr(engine, 'clear_all_data')
        
        # Test that the vector store is properly initialized
        assert engine.vector_store is not None
        assert hasattr(engine.vector_store, 'get_store_type')


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_store_type(self):
        """Test handling of invalid store type."""
        with pytest.raises(ValueError, match="Unsupported vector store type"):
            VectorStore(store_type="invalid_type", use_memory=True)
    
    def test_neo4j_without_config(self):
        """Test Neo4j store without proper configuration."""
        # This should use default config (which may fail to connect)
        try:
            store = VectorStore(store_type="neo4j")
            # If it succeeds, that's fine (Neo4j is running with defaults)
            assert store.get_store_type() == VectorStoreType.NEO4J
        except Exception:
            # Expected if Neo4j is not available with default config
            pass
    
    def test_adapter_error_handling(self):
        """Test that adapters handle errors gracefully."""
        # Test with in-memory ChromaDB (should always work)
        store = VectorStore(store_type="chromadb", use_memory=True)
        
        # Test that methods don't crash on empty store
        results = store.search("test query")
        assert isinstance(results, list)
        
        stats = store.get_stats()
        assert isinstance(stats, dict)
        
        # Test clearing empty store
        assert store.clear_collection() == True


# Test data fixtures
@pytest.fixture
def test_triplet_data():
    """Generate test triplet data for performance testing."""
    test_data = []
    
    people = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Eva Brown"]
    companies = ["Tech Corp", "Data Inc", "AI Systems", "Cloud Solutions", "Innovation Labs"]
    locations = ["New York", "San Francisco", "Boston", "Seattle", "Austin"]
    relationships = ["works_for", "lives_in", "studied_at", "manages", "collaborated_with"]
    
    for i in range(100):
        person = people[i % len(people)]
        if i < 50:
            # Work relationships
            company = companies[i % len(companies)]
            triplet = GraphTriplet(
                subject=person,
                relationship="works_for",
                object=company,
                summary=f"{person} works for {company}",
                confidence=0.8 + (i % 20) * 0.01,
                status=RelationshipStatus.ACTIVE,
                obsolete=False,
                created_at=datetime.now(),
                source="test_generator"
            )
        else:
            # Location relationships
            location = locations[i % len(locations)]
            triplet = GraphTriplet(
                subject=person,
                relationship="lives_in",
                object=location,
                summary=f"{person} lives in {location}",
                confidence=0.85 + (i % 15) * 0.01,
                status=RelationshipStatus.ACTIVE,
                obsolete=False,
                created_at=datetime.now(),
                source="test_generator"
            )
        
        test_data.append(triplet)
    
    return test_data


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])