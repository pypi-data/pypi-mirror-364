#!/usr/bin/env python3
"""
Example of using kg-engine-v2 as an external package.

This demonstrates how to import and use the knowledge graph engine
after installing it via pip install.
"""

# After installing: pip install kg-engine-v2
# You can import the engine like this:
from kg_engine import KnowledgeGraphEngineV2, InputItem

def main():
    """Example usage of KG Engine as external package"""
    
    # Initialize the engine (requires Neo4j setup and API keys)
    engine = KnowledgeGraphEngineV2()
    
    # Process some information
    items = [
        InputItem(
            content="Alice works at OpenAI as a researcher",
            source="external_app_example"
        ),
        InputItem(
            content="Bob lives in San Francisco and loves hiking",
            source="external_app_example"
        )
    ]
    
    # Process the items
    for item in items:
        result = engine.process_input(item)
        print(f"Processed: {result.message}")
    
    # Search for information
    search_results = engine.search("Who works at OpenAI?")
    for result in search_results.results:
        print(f"Found: {result.content} (score: {result.score:.3f})")

if __name__ == "__main__":
    main()