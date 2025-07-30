#!/usr/bin/env python3
"""Debug why vector store shows 0 triplets"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kg_engine.storage.graph_db import GraphDB
from kg_engine.config import Neo4jConfig

load_dotenv()

# Initialize GraphDB directly
config = Neo4jConfig(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password"),
    database=os.getenv("NEO4J_DATABASE", "neo4j")
)

graph_db = GraphDB(config)

# Get stats directly
stats = graph_db.get_stats()
print("GraphDB stats:", stats)

# Check what's actually in graph_stats
graph_stats = stats.get("graph_stats", {})
print("\ngraph_stats content:", graph_stats)

# Check for triplets
print("\nLooking for triplet counts:")
print(f"- total_triplets: {graph_stats.get('total_triplets', 'NOT FOUND')}")
print(f"- total_relationships: {graph_stats.get('total_relationships', 'NOT FOUND')}")
print(f"- total: {graph_stats.get('total', 'NOT FOUND')}")