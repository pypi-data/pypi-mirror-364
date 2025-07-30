#!/usr/bin/env python3
"""
KG Engine MCP Server

A Model Context Protocol (MCP) server that provides access to the Knowledge Graph Engine
through a simplified interface designed for AI assistants like Claude.

This server uses FastMCP with SSE transport for efficient communication.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Annotated
from datetime import datetime
from pydantic import Field

# Add parent directory to path to import kg_engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kg_engine import (
        KnowledgeGraphEngineV2,
        InputItem,
        Neo4jConfig,
        SearchType,
        EdgeData,
        EdgeMetadata,
        RelationshipStatus,
        parse_date,
        __version__ as kg_version
    )
except ImportError as e:
    print(f"❌ Failed to import kg_engine: {e}")
    print("💡 Make sure kg_engine is installed: pip install -e ..")
    sys.exit(1)

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("kg-engine-mcp", version="1.0.0")
mcp.description = f"Knowledge Graph Engine MCP Server (KG Engine v{kg_version})"

# Global engine instance
engine: Optional[KnowledgeGraphEngineV2] = None


def get_engine() -> KnowledgeGraphEngineV2:
    """Get or create the KG Engine instance"""
    global engine

    if engine is None:
        # Load configuration from environment
        config = Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )

        # Verify connectivity
        if not config.verify_connectivity():
            raise ConnectionError("Failed to connect to Neo4j")

        # Initialize engine with LLM configuration
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_BEARER_KEY", "placeholder")
        base_url = os.getenv("LLM_BASE_URL")

        engine_kwargs = {
            "api_key": api_key,
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "neo4j_config": config
        }

        # Add base_url if using custom LLM endpoint
        if base_url:
            engine_kwargs["base_url"] = base_url

        engine = KnowledgeGraphEngineV2(**engine_kwargs)

        logger.info("✅ KG Engine initialized successfully")

    return engine


# Initialize engine
# get_engine()


# =============================================================================
# KNOWLEDGE PROCESSING TOOLS
# =============================================================================

@mcp.tool(description="Process natural language text to extract and store knowledge in the graph. Analyzes text using AI to extract entities (people, places, organizations) and their relationships. Handles duplicates, conflicts, and temporal tracking.")
def process_text(
    text: Annotated[str, Field(description="Natural language text containing entity relationships. Examples: 'Alice works at Google', 'Bob knows Alice', 'Alice no longer works at TechCorp'")],
    source: Annotated[str, Field(description="Source identifier for data provenance tracking")] = "mcp"
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Create input item
        input_item = InputItem(
            description=text,
            metadata={
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
        )

        # Process
        result = kg_engine.process_input([input_item])

        return {
            "success": True,
            "relationships_created": result.get("new_edges", 0),
            "relationships_updated": result.get("updated_edges", 0),
            "duplicates_ignored": result.get("duplicates_ignored", 0),
            "message": f"Processed text and created {result.get('new_edges', 0)} new relationships"
        }

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Search the knowledge graph using natural language. Combines graph traversal with semantic vector search for intelligent results with AI-generated answers.")
def search(
    query: Annotated[str, Field(description="Natural language search query. Examples: 'Who works at Google?', 'People who know Alice', 'Software engineers in California', 'Who works in tech?'")],
    limit: Annotated[int, Field(description="Maximum results to return (1-100)", ge=1, le=100)] = 10,
    search_type: Annotated[str, Field(description="Search method: 'direct' (graph only), 'semantic' (vectors only), 'hybrid' (both)")] = "hybrid"
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Map search type
        search_type_map = {
            "direct": SearchType.DIRECT,
            "semantic": SearchType.SEMANTIC,
            "hybrid": SearchType.BOTH
        }

        search_enum = search_type_map.get(search_type, SearchType.BOTH)

        # Perform search
        response = kg_engine.search(query=query, search_type=search_enum, k=limit)

        # Format results
        results = []
        for result in response.results:
            edge = result.triplet.edge
            results.append({
                "subject": edge.get_subject_safe(),
                "relationship": edge.get_relationship_safe(),
                "object": edge.get_object_safe(),
                "confidence": result.score,
                "summary": edge.metadata.summary if edge.metadata else None
            })

        return {
            "success": True,
            "answer": response.answer,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        logger.error(f"Error searching: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# NODE OPERATIONS
# =============================================================================

@mcp.tool(description="Retrieve all relationships connected to a specific entity. Explores the graph from a node and returns relationships within specified depth.")
def get_node(
    node_name: Annotated[str, Field(description="Entity name to explore (case-sensitive). Examples: 'Alice', 'Google', 'Project X'")],
    depth: Annotated[int, Field(description="Graph traversal depth. 1=direct only, 2=include connected nodes, 3+=further (use cautiously)", ge=1, le=5)] = 1
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Get relationships
        relations = kg_engine.get_node_relations(
            node_name=node_name,
            max_depth=depth,
            filter_obsolete=True
        )

        # Format results
        relationships = []
        for relation in relations:
            edge = relation.triplet.edge
            relationships.append({
                "subject": edge.get_subject_safe(),
                "relationship": edge.get_relationship_safe(),
                "object": edge.get_object_safe(),
                "confidence": relation.score,
                "summary": edge.metadata.summary if edge.metadata else None
            })

        return {
            "success": True,
            "node": node_name,
            "relationships": relationships,
            "count": len(relationships)
        }

    except Exception as e:
        logger.error(f"Error getting node: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Update properties of an existing node. Add or modify custom metadata like type, description, category, or domain-specific attributes.")
def update_node(
    node_name: Annotated[str, Field(description="Name of node to update (must exist, case-sensitive)")],
    properties: Annotated[Dict[str, Any], Field(description="Properties to set/update. Values can be strings, numbers, booleans, or lists. Special: 'type' (Person/Organization), 'description', 'category', 'tags'")]
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Update node
        kg_engine.graph_db.update_node(node_name, properties)

        return {
            "success": True,
            "node": node_name,
            "properties_updated": list(properties.keys()),
            "message": f"Updated {len(properties)} properties for node '{node_name}'"
        }

    except Exception as e:
        logger.error(f"Error updating node: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Delete a node from the graph. PERMANENT operation - consider marking relationships obsolete instead. Use cascade=True to delete all relationships. WARNING: Deletion is PERMANENT and cannot be undone. Cascade deletes ALL relationships (incoming and outgoing). Consider update_edge to mark relationships obsolete instead.")
def delete_node(
    node_name: Annotated[str, Field(description="Name of node to delete (case-sensitive)")],
    cascade: Annotated[bool, Field(description="False: fail if has relationships (safe). True: delete node AND all relationships")] = False
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Delete node
        kg_engine.graph_db.delete_node(node_name, cascade=cascade)

        return {
            "success": True,
            "node": node_name,
            "cascade": cascade,
            "message": f"Deleted node '{node_name}'" + (" and all relationships" if cascade else "")
        }

    except Exception as e:
        logger.error(f"Error deleting node: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="AI-powered merge of duplicate entities. Analyzes nodes, combines relationships, resolves conflicts. Source node deleted after merge. Process: 1) AI analyzes if nodes represent same entity, 2) Selects best name for merged entity, 3) Transfers all relationships, 4) Resolves duplicates intelligently, 5) Preserves temporal info and confidence, 6) Combines properties by AI precedence.")
def merge_nodes(
    source_node: Annotated[str, Field(description="Node to merge FROM (will be deleted)")],
    target_node: Annotated[str, Field(description="Node to merge INTO (will be retained with combined data)")]
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Perform auto merge
        result = kg_engine.graph_db.merge_nodes_auto(
            source_node=source_node,
            target_node=target_node,
            merge_strategy="intelligent"
        )

        return {
            "success": result.get("success", False),
            "merged_node": result.get("merged_node_name"),
            "relationships_transferred": result.get("relationships_transferred", 0),
            "message": f"Merged '{source_node}' and '{target_node}' into '{result.get('merged_node_name')}'"
        }

    except Exception as e:
        logger.error(f"Error merging nodes: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# EDGE OPERATIONS
# =============================================================================

@mcp.tool(description="Create a relationship between entities. Nodes created automatically if needed. For manual relationships when process_text isn't suitable.")
def create_edge(
    subject: Annotated[str, Field(description="Source entity name (created if doesn't exist). Examples: 'Alice', 'Google', 'Project X'")],
    predicate: Annotated[str, Field(description="Relationship type (normalized to UPPERCASE_WITH_UNDERSCORES). Examples: 'works_at', 'knows', 'located_in', 'owns'")],
    object: Annotated[str, Field(description="Target entity name (created if doesn't exist). Examples: 'TechCorp', 'San Francisco', 'Bob'")],
    confidence: Annotated[float, Field(description="Confidence score (0.0-1.0, higher=more certain)", ge=0.0, le=1.0)] = 0.8
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Create metadata
        metadata = EdgeMetadata(
            summary=f"{subject} {predicate} {object}",
            confidence=confidence,
            source="mcp",
            status=RelationshipStatus.ACTIVE
        )

        # Create edge
        edge_data = EdgeData(
            subject=subject,
            relationship=predicate.upper().replace(" ", "_"),
            object=object,
            metadata=metadata
        )

        # Add to graph
        success = kg_engine.graph_db.add_edge_data(edge_data)

        return {
            "success": success,
            "edge": {
                "subject": subject,
                "predicate": predicate,
                "object": object,
                "confidence": confidence
            },
            "message": f"Created edge: {subject} {predicate} {object}"
        }

    except Exception as e:
        logger.error(f"Error creating edge: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Get all relationships for a node. Returns edge IDs needed for updates/deletion. Shows both incoming and outgoing connections.")
def get_edges(
    node_name: Annotated[str, Field(description="Node to get edges for (case-sensitive)")],
    relationship_type: Annotated[Optional[str], Field(description="Filter by relationship type (normalized to uppercase). Examples: 'works_at', 'KNOWS', 'located_in'")] = None
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Get edges
        edges = kg_engine.graph_db.get_node_edges(
            node_name=node_name,
            relationship_type=relationship_type.upper() if relationship_type else None,
            include_inactive=False
        )

        # Format results
        edge_list = []
        for edge in edges:
            edge_list.append({
                "edge_id": edge.edge_id,
                "subject": edge.get_subject_safe(),
                "relationship": edge.get_relationship_safe(),
                "object": edge.get_object_safe(),
                "summary": edge.metadata.summary if edge.metadata else None,
                "confidence": edge.metadata.confidence if edge.metadata else None,
                "status": edge.metadata.status.value if edge.metadata else None
            })

        return {
            "success": True,
            "node": node_name,
            "edges": edge_list,
            "count": len(edge_list)
        }

    except Exception as e:
        logger.error(f"Error getting edges: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Update edge properties: description, status, dates. Common: mark obsolete, add time bounds. Get edge_id from get_edges first. Use cases: Mark relationships obsolete when they end, Add time bounds to temporary relationships, Update descriptions with more detail, Track relationship evolution.")
def update_edge(
    edge_id: Annotated[str, Field(description="Edge ID from get_edges results. Example: 'edge_123abc'")],
    summary: Annotated[Optional[str], Field(description="New description. Example: 'Alice was promoted to Principal Engineer'")] = None,
    status: Annotated[Optional[str], Field(description="Relationship status: 'active' or 'obsolete'")] = None,
    from_date: Annotated[Optional[str], Field(description="Start date (ISO: '2023-01-15', natural: 'January 15, 2023', relative: 'last month')")] = None,
    to_date: Annotated[Optional[str], Field(description="End date (same formats as from_date)")] = None,
    obsolete: Annotated[bool, Field(description="Shorthand to mark obsolete (sets status='obsolete' and to_date=now)")] = False
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()
        updates = {}

        # Handle obsolete flag
        if obsolete or (status and status.lower() == "obsolete"):
            kg_engine.graph_db.update_edge_status(
                edge_id=edge_id,
                status=RelationshipStatus.OBSOLETE,
                to_date=datetime.now()
            )
            updates["status"] = "obsolete"
        elif status and status.lower() == "active":
            kg_engine.graph_db.update_edge_status(
                edge_id=edge_id,
                status=RelationshipStatus.ACTIVE
            )
            updates["status"] = "active"

        # Update other properties
        if summary or from_date or to_date:
            # Parse dates
            parsed_from = parse_date(from_date) if from_date else None
            parsed_to = parse_date(to_date) if to_date else None

            # Update via direct query
            with kg_engine.graph_db.driver.session(database=kg_engine.graph_db.config.database) as session:
                query_parts = []
                params = {"edge_id": edge_id}

                if summary:
                    query_parts.append("r.summary = $summary")
                    params["summary"] = summary
                    updates["summary"] = summary

                if parsed_from:
                    query_parts.append("r.from_date = $from_date")
                    params["from_date"] = parsed_from.isoformat()
                    updates["from_date"] = from_date

                if parsed_to:
                    query_parts.append("r.to_date = $to_date")
                    params["to_date"] = parsed_to.isoformat()
                    updates["to_date"] = to_date

                if query_parts:
                    query = f"""
                    MATCH ()-[r]->()
                    WHERE r.edge_id = $edge_id
                    SET {', '.join(query_parts)}
                    RETURN r
                    """
                    session.run(query, params)

        return {
            "success": True,
            "edge_id": edge_id,
            "updates": updates,
            "message": f"Updated edge {edge_id} with {len(updates)} changes"
        }

    except Exception as e:
        logger.error(f"Error updating edge: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool(description="Permanently delete a relationship. CAUTION: Cannot undo. Consider update_edge(obsolete=True) to preserve history instead. WARNING: Deletion is PERMANENT - cannot be undone. No history or audit trail preserved. Prefer update_edge(edge_id, obsolete=True) for soft delete. Alternatives: 1) Soft delete (recommended): update_edge(edge_id, obsolete=True) - Preserves history, tracks when ended, audit trail. 2) Update with end date: update_edge(edge_id, to_date='2024-01-15', status='obsolete') - Temporal context, better for compliance.")
def delete_edge(
    edge_id: Annotated[str, Field(description="Edge ID from get_edges results. Example: 'edge_123abc'")]
) -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Delete edge
        kg_engine.graph_db.delete_edge(edge_id)

        return {
            "success": True,
            "edge_id": edge_id,
            "message": f"Deleted edge {edge_id}"
        }

    except Exception as e:
        logger.error(f"Error deleting edge: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# SYSTEM TOOLS
# =============================================================================

@mcp.tool(description="Get graph statistics: entities, relationships, types. Real-time metrics for monitoring, health checks, and capacity planning. Use cases: Monitor graph growth over time, Check system health and connectivity, Verify bulk import operations, Capacity planning and optimization, Debug connectivity issues. Metrics: total_relationships (All edges including obsolete), total_entities (Unique nodes regardless of connections), relationship_types (Distinct types like WORKS_AT, KNOWS), engine_version (Current KG Engine version). Performance: Real-time computation, optimized for large graphs (sub-second).")
def get_stats() -> Dict[str, Any]:
    try:
        kg_engine = get_engine()

        # Get stats
        stats = kg_engine.get_stats()

        return {
            "success": True,
            "graph": {
                "total_relationships": stats.get("total_edges", 0),
                "total_entities": stats.get("total_entities", 0),
                "relationship_types": len(stats.get("relationships", []))
            },
            "engine_version": kg_version
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    logger.info(f"🚀 Starting KG Engine MCP Server v1.0.0")
    logger.info(f"   KG Engine Version: {kg_version}")
    logger.info(f"   Transport: SSE")
    logger.info(f"   Server URL: http://localhost:3000/sse")

    # Run the server
    mcp.run(transport="sse", host="0.0.0.0", port=3000)