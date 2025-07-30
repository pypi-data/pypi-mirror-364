#!/usr/bin/env python3
"""
KG Engine API Server - External FastAPI Application

This is a completely separate FastAPI project that uses the kg_engine package
as an external dependency. It demonstrates how to build applications on top
of the kg_engine package.
"""

from fastapi import FastAPI, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID, uuid4
from datetime import datetime
import os
import logging
import sys

# Import the kg_engine package as an external dependency
try:
    from kg_engine import (
        KnowledgeGraphEngineV2, InputItem, Neo4jConfig, SearchType,
        EdgeData, EdgeMetadata, RelationshipStatus, GraphDB, VectorStore,
        parse_date, setup_neo4j_schema, __version__ as kg_version
    )
except ImportError as e:
    print(f"❌ Failed to import kg_engine: {e}")
    print("💡 Make sure kg_engine is installed:")
    print("   pip install -e ../  # If running from kg_api_server directory")
    print("   pip install kg-engine-v2  # If installed from PyPI")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KG Engine API Server",
    description=f"""
    External REST API for KG Engine v{kg_version}
    
    This is a separate FastAPI application that demonstrates how to use
    the kg_engine package as an external dependency to build powerful
    knowledge graph applications.
    
    Features:
    - Complete CRUD operations for edges and nodes
    - Semantic search with hybrid graph/vector search
    - Natural language processing with LLM integration
    - Node merging with automatic and manual strategies
    - Real-time statistics and monitoring
    - Full Neo4j integration
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
engine: Optional[KnowledgeGraphEngineV2] = None
config: Optional[Neo4jConfig] = None

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    api_version: str
    kg_engine_version: str
    neo4j_connected: bool
    engine_initialized: bool
    uptime_seconds: Optional[float] = None

class ProcessTextRequest(BaseModel):
    """Request for processing natural language text"""
    texts: List[str] = Field(..., description="List of texts to process")
    user_id: Optional[UUID] = Field(None, description="User ID for data ownership")
    source: str = Field(default="api", description="Data source identifier")
    extract_temporal: bool = Field(default=True, description="Extract temporal information")
    
    class Config:
        schema_extra = {
            "example": {
                "texts": [
                    "Alice works as a software engineer at Google",
                    "Bob moved to San Francisco last year",
                    "Charlie studied computer science at MIT from 2018 to 2022"
                ],
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "source": "user_input",
                "extract_temporal": True
            }
        }

class ProcessTextResponse(BaseModel):
    """Response from text processing"""
    success: bool
    processed_texts: int
    relationships_created: int
    relationships_updated: int
    duplicates_ignored: int
    processing_time_ms: float
    errors: List[str] = Field(default_factory=list)
    extracted_relationships: List[Dict[str, Any]] = Field(default_factory=list)

class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., description="Natural language search query")
    search_type: Literal["graph", "vector", "hybrid"] = Field(
        default="hybrid", description="Type of search to perform"
    )
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    user_filter: Optional[UUID] = Field(None, description="Filter by user ID")
    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Who works in technology?",
                "search_type": "hybrid",
                "limit": 10,
                "confidence_threshold": 0.3
            }
        }

class SearchResponse(BaseModel):
    """Search response"""
    query: str
    search_type: str
    results_count: int
    processing_time_ms: float
    answer: Optional[str] = None
    results: List[Dict[str, Any]]

class CreateEdgeRequest(BaseModel):
    """Request to create an edge"""
    subject: str = Field(..., description="Subject entity")
    relationship: str = Field(..., description="Relationship type")
    object: str = Field(..., description="Object entity")
    summary: str = Field(..., description="Human-readable summary")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    user_id: Optional[UUID] = Field(None)
    source: str = Field(default="api")
    category: Optional[str] = Field(None)
    from_date: Optional[str] = Field(None, description="Start date (ISO format)")
    to_date: Optional[str] = Field(None, description="End date (ISO format)")

class NodeMergeRequest(BaseModel):
    """Request for node merging"""
    source_node: str = Field(..., description="First node to merge")
    target_node: str = Field(..., description="Second node to merge")
    merge_type: Literal["auto", "manual"] = Field(..., description="Merge strategy")
    new_name: Optional[str] = Field(None, description="New name (required for manual)")
    new_properties: Optional[Dict[str, Any]] = Field(None, description="New properties")

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_engine() -> KnowledgeGraphEngineV2:
    """Dependency to get the engine instance"""
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return engine

def get_config() -> Neo4jConfig:
    """Dependency to get the config instance"""
    if config is None:
        raise HTTPException(status_code=503, detail="Configuration not available")
    return config

# =============================================================================
# STARTUP/SHUTDOWN HANDLERS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the KG Engine on startup"""
    global engine, config
    
    logger.info("🚀 Starting KG Engine API Server...")
    logger.info(f"   Using KG Engine v{kg_version}")
    
    try:
        # Initialize Neo4j configuration
        config = Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        
        # Test Neo4j connectivity
        if config.verify_connectivity():
            logger.info("✅ Connected to Neo4j successfully")
            
            # Setup schema if needed
            try:
                schema_results = setup_neo4j_schema(config)
                logger.info(f"📊 Schema setup: {len(schema_results.get('constraints', []))} constraints, "
                           f"{len(schema_results.get('indexes', []))} indexes")
            except Exception as e:
                logger.warning(f"⚠️ Schema setup warning: {e}")
        else:
            logger.error("❌ Failed to connect to Neo4j")
            raise ConnectionError("Neo4j connection failed")
        
        # Initialize KG Engine
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️ No OpenAI API key provided - using placeholder")
            api_key = "placeholder"
        
        engine = KnowledgeGraphEngineV2(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            neo4j_config=config
        )
        
        logger.info("✅ KG Engine initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize KG Engine: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global engine
    logger.info("🔄 Shutting down KG Engine API Server...")
    if engine:
        try:
            # Cleanup if needed
            engine = None
            logger.info("✅ Engine cleaned up successfully")
        except Exception as e:
            logger.error(f"⚠️ Error during cleanup: {e}")

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "KG Engine API Server",
        "version": "1.0.0",
        "kg_engine_version": kg_version,
        "description": "External FastAPI application using kg_engine package",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    neo4j_connected = False
    
    try:
        if config:
            neo4j_connected = config.verify_connectivity()
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if engine is not None else "unhealthy",
        api_version="1.0.0",
        kg_engine_version=kg_version,
        neo4j_connected=neo4j_connected,
        engine_initialized=engine is not None
    )

@app.post("/process", response_model=ProcessTextResponse)
async def process_texts(
    request: ProcessTextRequest,
    kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)
):
    """Process natural language texts and extract relationships"""
    start_time = datetime.now()
    
    try:
        # Convert texts to InputItems
        input_items = []
        for text in request.texts:
            metadata = {
                "source": request.source,
                "timestamp": datetime.now().isoformat()
            }
            if request.user_id:
                metadata["user_id"] = str(request.user_id)
            
            input_items.append(InputItem(
                description=text,
                metadata=metadata
            ))
        
        # Process with KG Engine
        results = kg_engine.process_input(input_items)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ProcessTextResponse(
            success=True,
            processed_texts=len(request.texts),
            relationships_created=results.get("new_edges", 0),
            relationships_updated=results.get("updated_edges", 0),
            duplicates_ignored=results.get("duplicates_ignored", 0),
            processing_time_ms=processing_time,
            errors=results.get("errors", []),
            extracted_relationships=[
                {
                    "subject": er.get("extracted_info", {}).get("subject"),
                    "relationship": er.get("extracted_info", {}).get("relationship"),
                    "object": er.get("extracted_info", {}).get("object"),
                    "summary": er.get("extracted_info", {}).get("summary"),
                    "confidence": er.get("extracted_info", {}).get("confidence"),
                    "action": er.get("action")
                }
                for er in results.get("edge_results", [])
                if er.get("extracted_info")
            ]
        )
        
    except Exception as e:
        logger.error(f"Error processing texts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_graph(
    request: SearchRequest,
    kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)
):
    """Search the knowledge graph"""
    start_time = datetime.now()
    
    try:
        # Map search type
        search_type_map = {
            "graph": SearchType.DIRECT,
            "vector": SearchType.SEMANTIC,
            "hybrid": SearchType.BOTH
        }
        
        search_type = search_type_map.get(request.search_type, SearchType.BOTH)
        
        # Perform search
        response = kg_engine.search(
            query=request.query,
            search_type=search_type,
            k=request.limit
        )
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Format results
        formatted_results = []
        for result in response.results:
            if result.score >= request.confidence_threshold:
                formatted_results.append({
                    "subject": result.triplet.edge.get_subject_safe(),
                    "relationship": result.triplet.edge.get_relationship_safe(),
                    "object": result.triplet.edge.get_object_safe(),
                    "confidence": result.score,
                    "source": result.source,
                    "explanation": result.explanation,
                    "summary": result.triplet.edge.metadata.summary
                })
        
        return SearchResponse(
            query=request.query,
            search_type=request.search_type,
            results_count=len(formatted_results),
            processing_time_ms=processing_time,
            answer=response.answer,
            results=formatted_results
        )
        
    except Exception as e:
        logger.error(f"Error searching graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edges")
async def create_edge(
    request: CreateEdgeRequest,
    kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)
):
    """Create a new edge in the graph"""
    try:
        # Parse dates
        from_date = parse_date(request.from_date) if request.from_date else None
        to_date = parse_date(request.to_date) if request.to_date else None
        
        # Create edge metadata
        metadata = EdgeMetadata(
            summary=request.summary,
            confidence=request.confidence,
            source=request.source,
            user_id=str(request.user_id) if request.user_id else None,
            category=request.category,
            from_date=from_date,
            to_date=to_date,
            status=RelationshipStatus.ACTIVE
        )
        
        # Create edge data
        edge_data = EdgeData(
            subject=request.subject,
            relationship=request.relationship,
            object=request.object,
            metadata=metadata
        )
        
        # Add to graph
        success = kg_engine.graph_db.add_edge_data(edge_data)
        
        if success:
            return {
                "success": True,
                "message": "Edge created successfully",
                "edge": {
                    "subject": request.subject,
                    "relationship": request.relationship,
                    "object": request.object,
                    "summary": request.summary,
                    "confidence": request.confidence
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create edge")
            
    except Exception as e:
        logger.error(f"Error creating edge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nodes/{node_name}/relations")
async def get_node_relations(
    node_name: str,
    limit: int = Query(default=50, ge=1, le=200),
    kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)
):
    """Get all relations for a specific node"""
    try:
        relations = kg_engine.get_node_relations(
            node_name=node_name,
            max_depth=1,
            filter_obsolete=True
        )
        
        formatted_relations = []
        for relation in relations[:limit]:
            formatted_relations.append({
                "subject": relation.triplet.edge.get_subject_safe(),
                "relationship": relation.triplet.edge.get_relationship_safe(),
                "object": relation.triplet.edge.get_object_safe(),
                "confidence": relation.score,
                "summary": relation.triplet.edge.metadata.summary
            })
        
        return {
            "node_name": node_name,
            "relations_count": len(formatted_relations),
            "relations": formatted_relations
        }
        
    except Exception as e:
        logger.error(f"Error getting node relations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nodes/merge")
async def merge_nodes(
    request: NodeMergeRequest,
    kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)
):
    """Merge two nodes using automatic or manual strategy"""
    try:
        if request.merge_type == "auto":
            # Use automatic merging
            result = kg_engine.graph_db.merge_nodes_auto(
                source_node=request.source_node,
                target_node=request.target_node,
                merge_strategy="intelligent"
            )
        else:
            # Use manual merging
            if not request.new_name:
                raise HTTPException(status_code=400, detail="new_name required for manual merge")
            
            result = kg_engine.graph_db.merge_nodes_manual(
                source_node=request.source_node,
                target_node=request.target_node,
                new_name=request.new_name,
                new_metadata=request.new_properties or {}
            )
        
        return {
            "success": result.get("success", False),
            "merge_type": request.merge_type,
            "merged_node_name": result.get("merged_node_name"),
            "relationships_transferred": result.get("relationships_transferred", 0),
            "execution_time_ms": result.get("execution_time_ms"),
            "details": result.get("details", {})
        }
        
    except Exception as e:
        logger.error(f"Error merging nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics(kg_engine: KnowledgeGraphEngineV2 = Depends(get_engine)):
    """Get comprehensive system statistics"""
    try:
        stats = kg_engine.get_stats()
        
        return {
            "graph_statistics": stats.get("graph_stats", {}),
            "vector_statistics": stats.get("vector_stats", {}),
            "relationships_types": len(stats.get("relationships", [])),
            "entities_count": stats.get("entities", 0),
            "kg_engine_version": kg_version,
            "api_version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    
    print("🚀 Starting KG Engine API Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   KG Engine Version: {kg_version}")
    print("   Documentation: http://localhost:8080/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )