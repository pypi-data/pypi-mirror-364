#!/usr/bin/env python3
"""Test vector store initialization"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kg_engine import KnowledgeGraphEngineV2, Neo4jConfig

load_dotenv()

# Initialize engine
config = Neo4jConfig(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    username=os.getenv("NEO4J_USERNAME", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password"),
    database=os.getenv("NEO4J_DATABASE", "neo4j")
)

# Create engine - this should now show existing triplets
engine = KnowledgeGraphEngineV2(
    api_key=os.getenv("OPENAI_API_KEY") or "placeholder",
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    neo4j_config=config,
    base_url=os.getenv("LLM_BASE_URL")
)

print("\n✅ Vector store should now recognize existing data!")