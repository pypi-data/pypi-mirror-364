#!/usr/bin/env python3
"""
FastAPI REST API for Knowledge Graph Engine v2

Provides endpoints for:
- Processing natural language input with user tracking
- Searching the knowledge graph (graph/vector/both)
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID, uuid4
from datetime import datetime
import os
import logging

from src.kg_engine import KnowledgeGraphEngineV2, InputItem
from src.kg_engine.config import Neo4jConfig
from src.kg_engine.models import SearchType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Graph Engine API",
    description="REST API for processing natural language and searching knowledge graphs",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance (initialized on startup)
engine: Optional[KnowledgeGraphEngineV2] = None


# Pydantic models for API
class ProcessInputRequest(BaseModel):
    """Request model for processing natural language input"""
    user_id: UUID = Field(..., description="User ID (GUID) for tracking ownership")
    descriptions: List[str] = Field(..., description="List of natural language descriptions to process")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Ensure user_id is a valid UUID"""
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError("user_id must be a valid UUID")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "descriptions": [
                    "Alice works as a software engineer at Google",
                    "Bob lives in San Francisco"
                ],
                "metadata": {
                    "source": "web_form",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
        }


class ProcessInputResponse(BaseModel):
    """Response model for input processing"""
    status: str
    user_id: UUID
    processed_items: int
    new_edges: int
    updated_edges: int
    obsoleted_edges: int
    processing_time_ms: float
    errors: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Request model for searching the knowledge graph"""
    query: str = Field(..., description="Natural language search query")
    search_type: Literal["graph", "vector", "both"] = Field(
        default="both",
        description="Type of search to perform"
    )
    user_id: Optional[UUID] = Field(
        None,
        description="Optional: Filter results by user ID"
    )
    k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results to return"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Who works in technology?",
                "search_type": "both",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "k": 10
            }
        }


class SearchResult(BaseModel):
    """Individual search result"""
    subject: str
    relationship: str
    object: str
    confidence: float
    user_id: Optional[UUID]
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Response model for search queries"""
    query: str
    search_type: str
    answer: Optional[str]
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float
    user_filter_applied: bool


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    neo4j_connected: bool
    engine_initialized: bool
    version: str


@app.on_event("startup")
async def startup_event():
    """Initialize the Knowledge Graph Engine on startup"""
    global engine
    
    try:
        logger.info("Initializing Knowledge Graph Engine...")
        
        # Initialize Neo4j configuration
        neo4j_config = Neo4jConfig()
        
        # Verify Neo4j connectivity
        if not neo4j_config.verify_connectivity():
            logger.error("Failed to connect to Neo4j")
            raise ConnectionError("Neo4j connection failed")
        
        # Initialize engine
        api_key = os.getenv("OPENAI_API_KEY", "test")
        engine = KnowledgeGraphEngineV2(
            api_key=api_key,
            vector_store_type="neo4j",
            neo4j_config=neo4j_config
        )
        
        logger.info("✅ Knowledge Graph Engine initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and database health"""
    neo4j_connected = False
    
    try:
        neo4j_config = Neo4jConfig()
        neo4j_connected = neo4j_config.verify_connectivity()
    except:
        pass
    
    return HealthResponse(
        status="healthy" if engine is not None else "unhealthy",
        neo4j_connected=neo4j_connected,
        engine_initialized=engine is not None,
        version="2.1.0"
    )


@app.post("/process", response_model=ProcessInputResponse)
async def process_input(request: ProcessInputRequest):
    """
    Process natural language input and extract relationships
    
    - **user_id**: Required GUID for tracking data ownership
    - **descriptions**: List of natural language texts to process
    - **metadata**: Optional additional metadata
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    start_time = datetime.now()
    errors = []
    
    try:
        # Convert descriptions to InputItems with user_id in metadata
        input_items = []
        for desc in request.descriptions:
            # Merge user metadata with user_id
            item_metadata = request.metadata.copy() if request.metadata else {}
            item_metadata["user_id"] = str(request.user_id)
            
            input_items.append(InputItem(
                description=desc,
                metadata=item_metadata
            ))
        
        # Process the input
        result = engine.process_input(input_items)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ProcessInputResponse(
            status="success",
            user_id=request.user_id,
            processed_items=len(input_items),
            new_edges=result.get("new_edges", 0),
            updated_edges=result.get("updated_edges", 0),
            obsoleted_edges=result.get("obsoleted_edges", 0),
            processing_time_ms=processing_time,
            errors=result.get("errors", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_knowledge_graph(request: SearchRequest):
    """
    Search the knowledge graph using natural language
    
    - **query**: Natural language search query
    - **search_type**: Type of search (graph/vector/both)
    - **user_id**: Optional filter by user ID
    - **k**: Number of results to return
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    start_time = datetime.now()
    
    try:
        # Map search type string to enum
        search_type_map = {
            "graph": SearchType.DIRECT,
            "vector": SearchType.SEMANTIC,
            "both": SearchType.BOTH
        }
        search_type_enum = search_type_map.get(request.search_type, SearchType.BOTH)
        
        # Perform search
        response = engine.search(
            query=request.query,
            k=request.k,
            search_type=search_type_enum
        )
        
        # Filter results by user_id if provided
        filtered_results = []
        user_filter_applied = bool(request.user_id)
        
        for result in response.results:
            # Extract user_id from metadata
            metadata = result.triplet.edge.metadata
            result_user_id = metadata.user_id if hasattr(metadata, 'user_id') and metadata.user_id else None
            
            # Apply user filter if requested
            if request.user_id and result_user_id:
                if str(request.user_id) != str(result_user_id):
                    continue  # Skip results from other users
            
            search_result = SearchResult(
                subject=result.triplet.edge.subject,
                relationship=result.triplet.edge.relationship,
                object=result.triplet.edge.object,
                confidence=result.score,
                user_id=result_user_id,
                metadata={
                    "summary": result.triplet.edge.metadata.summary,
                    "status": result.triplet.edge.metadata.status.value,
                    "source": result.triplet.edge.metadata.source,
                    "user_id": result_user_id
                }
            )
            
            filtered_results.append(search_result)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return SearchResponse(
            query=request.query,
            search_type=request.search_type,
            answer=response.answer,
            results=filtered_results,
            total_results=len(filtered_results),
            processing_time_ms=processing_time,
            user_filter_applied=user_filter_applied
        )
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics(user_id: Optional[UUID] = Query(None, description="Filter stats by user ID")):
    """Get system statistics, optionally filtered by user"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    
    try:
        stats = engine.get_stats()
        
        # Add user filtering info
        if user_id:
            stats["filter_applied"] = {
                "user_id": str(user_id),
                "note": "User-specific filtering requires metadata query implementation"
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Run the API
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )