#!/usr/bin/env python3
"""Check Neo4j database contents"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")
database = os.getenv("NEO4J_DATABASE", "neo4j")

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session(database=database) as session:
        # Count all nodes
        result = session.run("MATCH (n) RETURN count(n) as node_count")
        node_count = result.single()["node_count"]
        print(f"Total nodes: {node_count}")
        
        # Count all relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
        rel_count = result.single()["rel_count"]
        print(f"Total relationships: {rel_count}")
        
        # Count relationships with edge_id
        result = session.run("MATCH ()-[r]->() WHERE r.edge_id IS NOT NULL RETURN count(r) as edge_count")
        edge_count = result.single()["edge_count"]
        print(f"Relationships with edge_id: {edge_count}")
        
        # Check for embeddings
        result = session.run("MATCH ()-[r]->() WHERE r.embedding IS NOT NULL RETURN count(r) as embed_count")
        embed_count = result.single()["embed_count"]
        print(f"Relationships with embeddings: {embed_count}")
        
        # Sample some relationships
        print("\nSample relationships:")
        result = session.run("MATCH (s)-[r]->(o) RETURN s.name as subject, type(r) as rel_type, o.name as object, r.edge_id as edge_id LIMIT 5")
        for record in result:
            print(f"  {record['subject']} -{record['rel_type']}-> {record['object']} (edge_id: {record['edge_id']})")
            
        # Check for vector index
        print("\nVector indexes:")
        result = session.run("SHOW INDEXES WHERE type = 'VECTOR'")
        for record in result:
            print(f"  Index: {record['name']} on {record['labelsOrTypes']} property {record['properties']}")
            
finally:
    driver.close()