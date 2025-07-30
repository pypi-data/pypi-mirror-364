#!/usr/bin/env python3
"""
GraphDB Feature Examples - Using 'Tor' as Main Node

This script demonstrates all major GraphDB features with practical examples
centered around 'Tor' as the primary entity.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.kg_engine.storage.graph_db import GraphDB
from src.kg_engine.models import EdgeData, EdgeMetadata, RelationshipStatus, GraphTriplet
from src.kg_engine.config import Neo4jConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphDBExamples:
    """Comprehensive examples of GraphDB features using 'Tor' as main entity"""
    
    def __init__(self):
        """Initialize GraphDB with Neo4j configuration"""
        self.config = Neo4jConfig()
        self.graph_db = GraphDB(self.config)
        
        print("🚀 GraphDB Examples - Knowledge Graph Engine v2")
        print(f"   Connected to: {self.config.uri}")
        print(f"   Database: {self.config.database}")
        print("-" * 60)
    
    def clear_and_setup(self):
        """Clear existing data and set up example dataset"""
        print("\n🧹 Setting up example dataset...")
        
        # Clear existing data
        # self.graph_db.clear_graph()
        
        # Create sample relationships for Tor
        sample_data = [
            # Work relationships
            EdgeData(
                subject="Tor",
                relationship="WORKS_AS",
                object="software engineer",
                metadata=EdgeMetadata(
                    summary="Tor works as a software engineer",
                    confidence=0.95,
                    status=RelationshipStatus.ACTIVE,
                    from_date=datetime(2020, 1, 1),
                    source="linkedin_profile"
                )
            ),
            EdgeData(
                subject="Tor",
                relationship="WORKS_AT",
                object="Anthropic",
                metadata=EdgeMetadata(
                    summary="Tor works at Anthropic",
                    confidence=0.90,
                    status=RelationshipStatus.ACTIVE,
                    from_date=datetime(2023, 3, 1),
                    source="company_directory"
                )
            ),
            
            # Previous work (obsolete relationship)
            EdgeData(
                subject="Tor",
                relationship="WORKS_AT",
                object="Google",
                metadata=EdgeMetadata(
                    summary="Tor previously worked at Google",
                    confidence=0.85,
                    status=RelationshipStatus.OBSOLETE,
                    from_date=datetime(2018, 6, 1),
                    to_date=datetime(2023, 2, 28),
                    obsolete=True,
                    source="resume"
                )
            ),
            
            # Location relationships
            EdgeData(
                subject="Tor",
                relationship="LIVES_IN",
                object="San Francisco",
                metadata=EdgeMetadata(
                    summary="Tor lives in San Francisco",
                    confidence=0.90,
                    status=RelationshipStatus.ACTIVE,
                    from_date=datetime(2022, 1, 1),
                    source="address_book"
                )
            ),
            EdgeData(
                subject="Tor",
                relationship="BORN_IN",
                object="Berlin",
                metadata=EdgeMetadata(
                    summary="Tor was born in Berlin",
                    confidence=1.0,
                    status=RelationshipStatus.ACTIVE,
                    source="birth_certificate"
                )
            ),
            
            # Hobby/interest relationships
            EdgeData(
                subject="Tor",
                relationship="ENJOYS",
                object="photography",
                metadata=EdgeMetadata(
                    summary="Tor enjoys photography as a hobby",
                    confidence=0.80,
                    status=RelationshipStatus.ACTIVE,
                    source="social_media"
                )
            ),
            EdgeData(
                subject="Tor",
                relationship="ENJOYS",
                object="hiking",
                metadata=EdgeMetadata(
                    summary="Tor enjoys hiking in nature",
                    confidence=0.75,
                    status=RelationshipStatus.ACTIVE,
                    source="fitness_app"
                )
            ),
            
            # Skill relationships
            EdgeData(
                subject="Tor",
                relationship="SKILLED_IN",
                object="Python programming",
                metadata=EdgeMetadata(
                    summary="Tor is skilled in Python programming",
                    confidence=0.95,
                    status=RelationshipStatus.ACTIVE,
                    source="github_profile"
                )
            ),
            EdgeData(
                subject="Tor",
                relationship="SKILLED_IN",
                object="machine learning",
                metadata=EdgeMetadata(
                    summary="Tor has expertise in machine learning",
                    confidence=0.90,
                    status=RelationshipStatus.ACTIVE,
                    source="project_portfolio"
                )
            ),
            
            # Education
            EdgeData(
                subject="Tor",
                relationship="STUDIED_AT",
                object="MIT",
                metadata=EdgeMetadata(
                    summary="Tor studied computer science at MIT",
                    confidence=0.98,
                    status=RelationshipStatus.ACTIVE,
                    from_date=datetime(2014, 9, 1),
                    to_date=datetime(2018, 5, 31),
                    source="academic_transcript"
                )
            ),
            
            # Collaborative relationships
            EdgeData(
                subject="Tor",
                relationship="COLLABORATES_WITH",
                object="Alice",
                metadata=EdgeMetadata(
                    summary="Tor collaborates with Alice on ML projects",
                    confidence=0.85,
                    status=RelationshipStatus.ACTIVE,
                    source="project_records"
                )
            ),
            EdgeData(
                subject="Alice",
                relationship="WORKS_AS",
                object="data scientist",
                metadata=EdgeMetadata(
                    summary="Alice works as a data scientist",
                    confidence=0.90,
                    status=RelationshipStatus.ACTIVE,
                    source="team_directory"
                )
            ),
            
            # Additional entities for path finding
            EdgeData(
                subject="Alice",
                relationship="MENTORED_BY",
                object="Dr. Smith",
                metadata=EdgeMetadata(
                    summary="Alice was mentored by Dr. Smith during PhD",
                    confidence=0.95,
                    status=RelationshipStatus.ACTIVE,
                    source="academic_records"
                )
            ),
            EdgeData(
                subject="Dr. Smith",
                relationship="WORKS_AT",
                object="Stanford",
                metadata=EdgeMetadata(
                    summary="Dr. Smith is a professor at Stanford",
                    confidence=0.98,
                    status=RelationshipStatus.ACTIVE,
                    source="faculty_directory"
                )
            ),
        ]
        
        # Add all sample data
        for edge_data in sample_data:
            success = self.graph_db.add_edge_data(edge_data)
            if success:
                print(f"✅ Added: {edge_data.subject} -{edge_data.relationship}-> {edge_data.object}")
            else:
                print(f"❌ Failed: {edge_data.subject} -{edge_data.relationship}-> {edge_data.object}")
        
        print(f"\n📊 Setup complete! Added {len(sample_data)} relationships.")
    
    def example_1_basic_operations(self):
        """Example 1: Basic CRUD Operations"""
        print("\n" + "="*60)
        print("📝 Example 1: Basic CRUD Operations")
        print("="*60)
        
        # 1.1 Find edges by criteria
        print("\n1.1 Find all relationships for 'Tor':")
        Tor_edges = self.graph_db.find_edges(subject="Tor")
        for triplet in Tor_edges[:5]:  # Show first 5
            edge = triplet.edge
            rel = edge.get_relationship_safe() or "UNKNOWN"
            obj = edge.get_object_safe() or "UNKNOWN"
            print(f"   • Tor -{rel}-> {obj} (confidence: {edge.metadata.confidence:.2f})")
        
        # 1.2 Find specific relationship type
        print(f"\n1.2 Find work relationships for 'Tor':")
        work_edges = self.graph_db.find_edges(subject="Tor", relationship="WORKS_AT")
        for triplet in work_edges:
            edge = triplet.edge
            obj = edge.get_object_safe() or "UNKNOWN"
            status = "obsolete" if edge.metadata.obsolete else "active"
            print(f"   • Tor WORKS_AT {obj} ({status})")
        
        # 1.3 Update edge metadata
        print(f"\n1.3 Update relationship confidence:")
        # Find photography edge and update confidence
        photo_edges = self.graph_db.find_edges(subject="Tor", relationship="ENJOYS", obj="photography")
        if photo_edges:
            edge = photo_edges[0].edge
            old_confidence = edge.metadata.confidence
            edge.metadata.confidence = 0.95  # Increase confidence
            edge.metadata.source = "updated_via_example"
            
            success = self.graph_db.update_edge_metadata(edge.edge_id, edge.metadata)
            if success:
                print(f"   ✅ Updated photography confidence: {old_confidence:.2f} -> {edge.metadata.confidence:.2f}")
        
        # 1.4 Get edge by ID
        print(f"\n1.4 Retrieve edge by ID:")
        if photo_edges:
            edge_id = photo_edges[0].edge.edge_id
            retrieved_edge = self.graph_db.get_edge_by_id(edge_id)
            if retrieved_edge:
                rel = retrieved_edge.get_relationship_safe()
                obj = retrieved_edge.get_object_safe()
                print(f"   📋 Retrieved: {retrieved_edge.get_subject_safe()} -{rel}-> {obj}")
                print(f"      Confidence: {retrieved_edge.metadata.confidence:.2f}")
                print(f"      Source: {retrieved_edge.metadata.source}")
    
    def example_2_optimized_entity_exploration(self):
        """Example 2: Optimized Entity Relationship Exploration"""
        print("\n" + "="*60)
        print("🔍 Example 2: Optimized Entity Exploration")
        print("="*60)
        
        # 2.1 Single-hop exploration (optimized)
        print("\n2.1 Single-hop exploration for 'Tor' (optimized):")
        start_time = datetime.now()
        
        triplets = self.graph_db.get_entity_relationships_optimized(
            entity="Tor",
            filter_obsolete=True,
            max_depth=1,
            limit=10
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        print(f"   ⚡ Query completed in {duration:.2f}ms")
        print(f"   📊 Found {len(triplets)} active relationships:")
        
        for triplet in triplets:
            edge = triplet.edge
            subj = edge.get_subject_safe() or "UNKNOWN"
            rel = edge.get_relationship_safe() or "UNKNOWN"
            obj = edge.get_object_safe() or "UNKNOWN"
            print(f"      • {subj} -{rel}-> {obj}")
        
        # 2.2 Repeat query (fast due to indexing)
        print(f"\n2.2 Same query again (fast due to indexing):")
        start_time = datetime.now()
        
        repeat_triplets = self.graph_db.get_entity_relationships_optimized(
            entity="Tor",
            filter_obsolete=True,
            max_depth=1,
            limit=10
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        print(f"   ⚡ Repeat query completed in {duration:.2f}ms")
        print(f"   📊 Found {len(repeat_triplets)} relationships")
        
        # 2.3 Filter by relationship types
        print(f"\n2.3 Exploration filtered by relationship types:")
        work_triplets = self.graph_db.get_entity_relationships_optimized(
            entity="Tor",
            filter_obsolete=True,
            relationship_types=["WORKS_AS", "WORKS_AT", "SKILLED_IN"],
            limit=10
        )
        
        print(f"   💼 Professional relationships ({len(work_triplets)}):")
        for triplet in work_triplets:
            edge = triplet.edge
            rel = edge.get_relationship_safe() or "UNKNOWN"
            obj = edge.get_object_safe() or "UNKNOWN"
            print(f"      • Tor -{rel}-> {obj}")
        
        # 2.4 Multi-hop exploration
        print(f"\n2.4 Multi-hop exploration (depth=2):")
        multi_hop_triplets = self.graph_db.get_entity_relationships_optimized(
            entity="Tor",
            filter_obsolete=True,
            max_depth=2,
            limit=15
        )
        
        print(f"   🔗 Multi-hop relationships ({len(multi_hop_triplets)}):")
        for triplet in multi_hop_triplets[:8]:  # Show first 8
            edge = triplet.edge
            subj = edge.get_subject_safe() or "UNKNOWN"
            rel = edge.get_relationship_safe() or "UNKNOWN"
            obj = edge.get_object_safe() or "UNKNOWN"
            print(f"      • {subj} -{rel}-> {obj}")
    
    def example_3_conflict_detection(self):
        """Example 3: Advanced Conflict Detection"""
        print("\n" + "="*60)
        print("⚠️  Example 3: Advanced Conflict Detection")
        print("="*60)
        
        # 3.1 Add conflicting work relationship
        print("\n3.1 Adding conflicting work relationship...")
        conflicting_edge = EdgeData(
            subject="Tor",
            relationship="WORKS_AT",
            object="OpenAI",
            metadata=EdgeMetadata(
                summary="Tor works at OpenAI (potential conflict)",
                confidence=0.70,
                status=RelationshipStatus.ACTIVE,
                from_date=datetime(2023, 6, 1),
                source="conflicting_source"
            )
        )
        
        success = self.graph_db.add_edge_data(conflicting_edge)
        if success:
            print("   ✅ Added conflicting relationship: Tor WORKS_AT OpenAI")
        
        # 3.2 Detect conflicts for specific entity
        print(f"\n3.2 Detecting conflicts for 'Tor':")
        conflicts = self.graph_db.detect_relationship_conflicts_optimized(
            entity_name="Tor",
            confidence_threshold=0.5,
            limit=10
        )
        
        print(f"   🔍 Found {len(conflicts)} conflicts:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"\n   Conflict #{i}:")
            print(f"      Entity: {conflict['conflicted_entity']}")
            print(f"      Relationship: {conflict['conflicted_relationship']}")
            print(f"      Conflicting objects: {conflict['conflicting_objects']}")
            print(f"      Confidence difference: {conflict['confidence_diff']:.3f}")
            
            # Show the conflicting edges
            higher_edge = conflict['higher_confidence_edge']
            lower_edge = conflict['lower_confidence_edge']
            
            print(f"      Higher confidence: {higher_edge.get_object_safe()} (conf: {higher_edge.metadata.confidence:.2f})")
            print(f"      Lower confidence: {lower_edge.get_object_safe()} (conf: {lower_edge.metadata.confidence:.2f})")
        
        # 3.3 Detect conflicts by relationship type
        print(f"\n3.3 Detecting WORKS_AT conflicts across all entities:")
        work_conflicts = self.graph_db.detect_relationship_conflicts_optimized(
            relationship_type="WORKS_AT",
            confidence_threshold=0.3,
            limit=5
        )
        
        for conflict in work_conflicts:
            entity = conflict['conflicted_entity']
            objects = conflict['conflicting_objects']
            print(f"   ⚠️  {entity} has conflicting WORKS_AT: {objects}")
    
    def example_4_temporal_analysis(self):
        """Example 4: Temporal Relationship Analysis"""
        print("\n" + "="*60)
        print("⏰ Example 4: Temporal Relationship Analysis")
        print("="*60)
        
        # 4.1 Show relationship evolution over time
        print("\n4.1 Relationship evolution for 'Tor':")
        temporal_data = self.graph_db.analyze_entity_temporal_relationships(
            entity_name="Tor",
            show_evolution=True,
            limit=20
        )
        
        print(f"   📈 Temporal evolution ({len(temporal_data)} relationships):")
        for data in temporal_data:
            entity = data['entity']
            connected = data['connected_entity']
            rel_type = data['relationship_type']
            status = data.get('status', 'unknown')
            start_time = data.get('start_time')
            
            time_str = start_time.strftime("%Y-%m") if start_time else "unknown"
            print(f"      • {time_str}: {entity} -{rel_type}-> {connected} [{status}]")
        
        # 4.2 Analyze relationships in specific time period
        print(f"\n4.2 Active relationships in 2023:")
        recent_data = self.graph_db.analyze_entity_temporal_relationships(
            entity_name="Tor",
            start_date="2023-01-01T00:00:00",
            end_date="2023-12-31T23:59:59",
            show_evolution=False,
            limit=10
        )
        
        print(f"   📅 2023 active relationships ({len(recent_data)}):")
        for data in recent_data:
            connected = data['connected_entity']
            rel_type = data['relationship_type']
            confidence = data.get('confidence', 0.0)
            print(f"      • Tor -{rel_type}-> {connected} (conf: {confidence:.2f})")
        
        # 4.3 Show work history evolution
        print(f"\n4.3 Work history evolution:")
        work_history = []
        for data in temporal_data:
            if data['relationship_type'] == 'WORKS_AT':
                work_history.append(data)
        
        # Sort by start time
        work_history.sort(key=lambda x: x.get('start_time') or datetime.min)
        
        print("   💼 Career progression:")
        for work in work_history:
            company = work['connected_entity']
            status = work.get('status', 'unknown')
            start_time = work.get('start_time')
            time_str = start_time.strftime("%Y-%m") if start_time else "unknown"
            
            status_emoji = "✅" if status == "active" else "📜" if status == "ended" else "⏰"
            print(f"      {status_emoji} {time_str}: {company} ({status})")
    
    def example_5_path_finding(self):
        """Example 5: Relationship Path Finding"""
        print("\n" + "="*60)
        print("🛤️  Example 5: Relationship Path Finding")
        print("="*60)
        
        try:
            # 5.1 Find paths between Tor and Dr. Smith
            print("\n5.1 Finding paths from 'Tor' to 'Dr. Smith':")
            paths = self.graph_db.find_relationship_paths(
                start_entity="Tor",
                end_entity="Dr. Smith",
                max_hops=4,
                avoid_obsolete=True,
                limit=5
            )
            
            print(f"   🔍 Found {len(paths)} paths:")
            for i, path_info in enumerate(paths, 1):
                print(f"\n   Path #{i}:")
                print(f"      Length: {path_info.get('path_length', 0)} hops")
                print(f"      Confidence: {path_info.get('path_confidence', 0.0):.3f}")
                
                # Safe join for entities - filter out None values and handle missing keys
                entities_raw = path_info.get('entities_in_path', [])
                entities = [str(e) for e in entities_raw if e is not None and e != '']
                if entities:
                    print(f"      Entities: {' -> '.join(entities)}")
                else:
                    print(f"      Entities: No valid entities found")
                
                # Safe join for relationships - filter out None values and handle missing keys
                relationships_raw = path_info.get('relationship_chain', [])
                relationships = [str(r) for r in relationships_raw if r is not None and r != '']
                if relationships:
                    print(f"      Relationships: {' -> '.join(relationships)}")
                else:
                    print(f"      Relationships: No valid relationships found")
            
            # 5.2 Find paths to MIT (educational connection)
            print(f"\n5.2 Finding paths from 'Tor' to 'MIT':")
            mit_paths = self.graph_db.find_relationship_paths(
                start_entity="Tor",
                end_entity="MIT",
                max_hops=3,
                avoid_obsolete=True,
                limit=3
            )
            
            for i, path_info in enumerate(mit_paths, 1):
                # Safe handling of entities and relationships
                entities_raw = path_info.get('entities_in_path', [])
                relationships_raw = path_info.get('relationship_chain', [])
                
                entities = [str(e) for e in entities_raw if e is not None and e != '']
                relationships = [str(r) for r in relationships_raw if r is not None and r != '']
                
                if entities:
                    print(f"   🎓 Path #{i}: {' -> '.join(entities)}")
                else:
                    print(f"   🎓 Path #{i}: No valid entities")
                    
                if relationships:
                    print(f"      Via: {' -> '.join(relationships)}")
                else:
                    print(f"      Via: No valid relationships")
            
            # 5.3 Find shortest paths to any location
            print(f"\n5.3 Finding paths from 'Tor' to geographical locations:")
            for location in ["San Francisco", "Berlin"]:
                location_paths = self.graph_db.find_relationship_paths(
                    start_entity="Tor",
                    end_entity=location,
                    max_hops=2,
                    avoid_obsolete=True,
                    limit=2
                )
                
                if location_paths:
                    path = location_paths[0]  # Shortest path
                    # Safe handling for location paths
                    entities_raw = path.get('entities_in_path', [])
                    relationships_raw = path.get('relationship_chain', [])
                    
                    entities = [str(e) for e in entities_raw if e is not None and e != '']
                    relationships = [str(r) for r in relationships_raw if r is not None and r != '']
                    
                    if entities:
                        print(f"   🌍 To {location}: {' -> '.join(entities)}")
                    else:
                        print(f"   🌍 To {location}: No valid path found")
                        
                    if relationships:
                        print(f"      Via: {' -> '.join(relationships)}")
                    else:
                        print(f"      Via: No valid relationships")
                        
        except Exception as e:
            print(f"   ❌ Error in path finding: {e}")
            logger.error(f"Path finding error: {e}")
            # Continue with other examples
    
    def example_6_pattern_discovery(self):
        """Example 6: Complex Pattern Discovery"""
        print("\n" + "="*60)
        print("🔍 Example 6: Complex Pattern Discovery")
        print("="*60)
        
        # 6.1 Discover work patterns
        print("\n6.1 Discovering work-related patterns:")
        work_patterns = self.graph_db.discover_relationship_patterns(
            pattern_description="people who work in technology",
            entity_types={"person": "Entity", "role": "Entity"},
            limit=10
        )
        
        print(f"   💼 Found {len(work_patterns)} work patterns:")
        for i, pattern in enumerate(work_patterns[:3], 1):
            pattern_type = pattern.get('pattern_type', 'unknown')
            print(f"\n   Pattern #{i} ({pattern_type}):")
            
            if pattern_type == "single_triplet":
                triplet = pattern.get('triplet')
                if triplet:
                    subj = triplet.get_subject_safe()
                    rel = triplet.get_relationship_safe()
                    obj = triplet.get_object_safe()
                    conf = pattern.get('confidence', 0.0)
                    print(f"      {subj} -{rel}-> {obj} (confidence: {conf:.2f})")
            
            elif pattern_type == "multi_entity":
                entities = pattern.get('entities', [])
                path_conf = pattern.get('path_confidence', 0.0)
                print(f"      Entities: {entities}")
                print(f"      Path confidence: {path_conf:.2f}")
        
        # 6.2 Discover collaboration patterns
        print(f"\n6.2 Discovering collaboration patterns:")
        collab_patterns = self.graph_db.discover_relationship_patterns(
            pattern_description="people who collaborate on projects",
            limit=5
        )
        
        print(f"   🤝 Found {len(collab_patterns)} collaboration patterns:")
        for pattern in collab_patterns[:2]:
            pattern_type = pattern.get('pattern_type', 'unknown')
            print(f"      Pattern type: {pattern_type}")
            
            if 'triplet' in pattern:
                triplet = pattern['triplet']
                subj = triplet.get_subject_safe()
                rel = triplet.get_relationship_safe()
                obj = triplet.get_object_safe()
                print(f"      {subj} -{rel}-> {obj}")
        
        # 6.3 Discover skill patterns
        print(f"\n6.3 Discovering skill-based patterns:")
        skill_patterns = self.graph_db.discover_relationship_patterns(
            pattern_description="technical skills and expertise",
            limit=8
        )
        
        print(f"   🎯 Found {len(skill_patterns)} skill patterns:")
        for pattern in skill_patterns[:3]:
            if 'triplet' in pattern:
                triplet = pattern['triplet']
                if triplet.get_relationship_safe() == "SKILLED_IN":
                    person = triplet.get_subject_safe()
                    skill = triplet.get_object_safe()
                    print(f"      {person} has expertise in: {skill}")
    
    def example_7_advanced_queries(self):
        """Example 7: Advanced Queries and Analytics"""
        print("\n" + "="*60)
        print("📊 Example 7: Advanced Queries and Analytics")
        print("="*60)
        
        # 7.1 Entity relationship summary
        print("\n7.1 Comprehensive relationship summary for 'Tor':")
        
        # Get all relationships
        all_triplets = self.graph_db.get_entity_relationships_optimized(
            entity="Tor",
            filter_obsolete=False,  # Include obsolete to show history
            max_depth=1,
            limit=50
        )
        
        # Categorize relationships
        categories = {
            "Work": ["WORKS_AS", "WORKS_AT", "SKILLED_IN"],
            "Location": ["LIVES_IN", "BORN_IN"],
            "Interests": ["ENJOYS"],
            "Education": ["STUDIED_AT"],
            "Social": ["COLLABORATES_WITH", "MENTORED_BY"]
        }
        
        for category, rel_types in categories.items():
            print(f"\n   {category} Relationships:")
            category_triplets = [t for t in all_triplets 
                               if t.edge.get_relationship_safe() in rel_types]
            
            for triplet in category_triplets:
                edge = triplet.edge
                rel = edge.get_relationship_safe()
                obj = edge.get_object_safe()
                status = "obsolete" if edge.metadata.obsolete else "active"
                conf = edge.metadata.confidence
                print(f"      • {rel}: {obj} [{status}] (conf: {conf:.2f})")
        
        # 7.2 Find duplicate relationships
        print(f"\n7.2 Checking for duplicate relationships:")
        
        # Check for duplicates in photography hobby
        photo_edge_data = EdgeData(
            subject="Tor",
            relationship="ENJOYS",
            object="photography",
            metadata=EdgeMetadata(summary="test", confidence=0.5)
        )
        
        duplicates = self.graph_db.find_duplicate_edges(photo_edge_data)
        print(f"   🔍 Found {len(duplicates)} duplicate 'enjoys photography' relationships")
        
        for dup in duplicates:
            conf = dup.metadata.confidence
            source = dup.metadata.source or "unknown"
            print(f"      • Confidence: {conf:.2f}, Source: {source}")
        
        # 7.3 Graph statistics
        print(f"\n7.3 Graph statistics:")
        stats = self.graph_db.get_stats()
        
        print(f"   📈 Graph Overview:")
        print(f"      Total entities: {stats['total_entities']}")
        print(f"      Total edges: {stats['total_edges']}")
        print(f"      Active edges: {stats['active_edges']}")
        print(f"      Obsolete edges: {stats['obsolete_edges']}")
        print(f"      Relationship types: {stats['relationship_types']}")
        
        print(f"\n   🔗 Relationship Types:")
        for rel_type in stats['relationships'][:10]:  # Show first 10
            print(f"      • {rel_type}")
        
        # 7.4 Index performance
        print(f"\n7.4 Index performance statistics:")
        
        print(f"   📊 Index Statistics:")
        print(f"      Indexes created: {self.graph_db._indexes_created}")
        print(f"      Optimized queries enabled")
    
    def example_8_optimization_features(self):
        """Example 8: Performance Optimization Features"""
        print("\n" + "="*60)
        print("⚡ Example 8: Performance Optimization Features")
        print("="*60)
        
        # 8.1 Force index creation
        print("\n8.1 Performance index management:")
        index_created = self.graph_db.force_create_indexes()
        print(f"   📊 Performance indexes created: {index_created}")
        
        # 8.2 Optimization statistics
        print(f"\n8.2 Comprehensive optimization statistics:")
        opt_stats = self.graph_db.get_optimization_stats()
        
        if 'error' not in opt_stats:
            print("   🚀 Database Statistics:")
            db_stats = opt_stats.get('database_stats', {})
            for key, value in db_stats.items():
                print(f"      {key}: {value}")
            
            
            print("\n   🔧 Available Optimized Methods:")
            methods = opt_stats.get('available_optimized_methods', [])
            for method in methods:
                print(f"      • {method}")
        
        # 8.3 Query optimization demonstration
        print(f"\n8.3 Query optimization demonstration:")
        
        # Query with optimization
        start_time = datetime.now()
        conflicts = self.graph_db.detect_relationship_conflicts_optimized(
            entity_name="Tor",
            confidence_threshold=0.5
        )
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"   ⚡ Optimized query: {duration:.2f}ms")
        print(f"   📊 Found {len(conflicts)} conflicts")
        print(f"   🚀 Using indexed fields and optimized Cypher")
        
        # 8.4 Entity alias management
        print(f"\n8.4 Entity alias management:")
        
        # Add aliases for Tor
        self.graph_db.add_entity_alias("david", "Tor")
        self.graph_db.add_entity_alias("dave", "Tor")
        
        print("   📝 Added aliases: 'david' and 'dave' -> 'Tor'")
        
        # Test normalization
        normalized = self.graph_db.normalize_entity_name("David")
        print(f"   🔄 'David' normalizes to: '{normalized}'")
        
        normalized = self.graph_db.normalize_entity_name("DAVE")
        print(f"   🔄 'DAVE' normalizes to: '{normalized}'")
    
    def run_all_examples(self):
        """Run all examples in sequence"""
        try:
            # Setup
            self.clear_and_setup()
            
            # Run all examples
            self.example_1_basic_operations()
            self.example_2_optimized_entity_exploration()
            self.example_3_conflict_detection()
            self.example_4_temporal_analysis()
            self.example_5_path_finding()
            self.example_6_pattern_discovery()
            self.example_7_advanced_queries()
            self.example_8_optimization_features()
            
            # Summary
            print("\n" + "="*60)
            print("🎉 All GraphDB Examples Completed Successfully!")
            print("="*60)
            
            final_stats = self.graph_db.get_stats()
            print(f"\nFinal Graph State:")
            print(f"   • Entities: {final_stats['total_entities']}")
            print(f"   • Relationships: {final_stats['total_edges']}")
            print(f"   • Active: {final_stats['active_edges']}")
            print(f"   • Types: {final_stats['relationship_types']}")
            
        except Exception as e:
            logger.error(f"Error running examples: {e}")
            raise


def main():
    """Main function to run all GraphDB examples"""
    try:
        examples = GraphDBExamples()
        examples.run_all_examples()
        
    except Exception as e:
        logger.error(f"Failed to run examples: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("  1. Neo4j is running and accessible")
        print("  2. Connection credentials are correct")
        print("  3. Database permissions are sufficient")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())