#!/usr/bin/env python3
"""Generate embeddings for existing relationships"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
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

if not config.verify_connectivity():
    print("❌ Failed to connect to Neo4j")
    sys.exit(1)

# Create engine
engine = KnowledgeGraphEngineV2(
    api_key=os.getenv("OPENAI_API_KEY") or "placeholder",
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    neo4j_config=config,
    base_url=os.getenv("LLM_BASE_URL")
)

print("🔧 Generating embeddings for existing relationships...")

# Get all relationships without embeddings
with engine.graph_db.driver.session(database=config.database) as session:
    result = session.run("""
        MATCH (s)-[r]->(o)
        WHERE r.edge_id IS NOT NULL AND r.embedding IS NULL
        RETURN r.edge_id as edge_id, s.name as subject, type(r) as rel_type, o.name as object
    """)
    
    relationships = list(result)
    print(f"Found {len(relationships)} relationships without embeddings")

# Generate embeddings for each relationship
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

for i, rel in enumerate(relationships):
    text = f"{rel['subject']} {rel['rel_type'].lower().replace('_', ' ')} {rel['object']}"
    embedding = embedding_model.encode(text).tolist()
    
    # Update the relationship with embedding
    with engine.graph_db.driver.session(database=config.database) as session:
        session.run("""
            MATCH ()-[r]->()
            WHERE r.edge_id = $edge_id
            SET r.embedding = $embedding
        """, edge_id=rel['edge_id'], embedding=embedding)
    
    print(f"✓ {i+1}/{len(relationships)}: {text}")

print("\n✅ Embeddings generated successfully!")

# Verify
with engine.graph_db.driver.session(database=config.database) as session:
    result = session.run("MATCH ()-[r]->() WHERE r.embedding IS NOT NULL RETURN count(r) as count")
    count = result.single()["count"]
    print(f"Total relationships with embeddings: {count}")