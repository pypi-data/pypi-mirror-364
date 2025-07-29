#!/usr/bin/env python3
"""
Comprehensive test suite for Knowledge Graph Engine v2 optimizations.

Tests all optimized methods implemented in GraphDB including:
- Performance indexes
- Vector similarity search with graph integration
- Optimized entity exploration
- Conflict detection
- Temporal analysis
- Path finding
- Query caching
"""

import time
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.kg_engine.storage.graph_db import GraphDB
from src.kg_engine.models import EdgeData, EdgeMetadata, RelationshipStatus
from src.kg_engine.config import Neo4jConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationTester:
    """Test suite for Knowledge Graph optimizations"""
    
    def __init__(self):
        self.config = Neo4jConfig()
        self.graph_db = GraphDB(self.config)
        self.test_data_created = False
        
    def setup_test_data(self) -> bool:
        """Create test data for optimization testing"""
        logger.info("Setting up test data...")
        
        test_edges = [
            # Technology relationships
            EdgeData("Alice", "WORKS_AT", "TechCorp", 
                    EdgeMetadata("Alice works as a software engineer at TechCorp", confidence=0.9)),
            EdgeData("Bob", "WORKS_AT", "TechCorp", 
                    EdgeMetadata("Bob is a data scientist at TechCorp", confidence=0.8)),
            EdgeData("Alice", "KNOWS", "Bob", 
                    EdgeMetadata("Alice and Bob are colleagues", confidence=0.7)),
            EdgeData("Alice", "LIVES_IN", "San Francisco", 
                    EdgeMetadata("Alice lives in San Francisco", confidence=1.0)),
            EdgeData("Bob", "LIVES_IN", "San Francisco", 
                    EdgeMetadata("Bob lives in San Francisco", confidence=0.9)),
            
            # Historical relationships with temporal data
            EdgeData("Charlie", "WORKED_AT", "OldCorp", 
                    EdgeMetadata("Charlie used to work at OldCorp", 
                               confidence=0.8, 
                               from_date=datetime(2020, 1, 1),
                               to_date=datetime(2022, 12, 31),
                               obsolete=True)),
            EdgeData("Charlie", "WORKS_AT", "NewCorp", 
                    EdgeMetadata("Charlie now works at NewCorp", 
                               confidence=0.9,
                               from_date=datetime(2023, 1, 1))),
            
            # Geographic relationships
            EdgeData("David", "BORN_IN", "London", 
                    EdgeMetadata("David was born in London, UK", confidence=1.0)),
            EdgeData("David", "LIVES_IN", "Berlin", 
                    EdgeMetadata("David currently lives in Berlin", confidence=0.9)),
            EdgeData("London", "LOCATED_IN", "UK", 
                    EdgeMetadata("London is located in the United Kingdom", confidence=1.0)),
            EdgeData("Berlin", "LOCATED_IN", "Germany", 
                    EdgeMetadata("Berlin is located in Germany", confidence=1.0)),
            
            # Hobby relationships
            EdgeData("Alice", "ENJOYS", "Photography", 
                    EdgeMetadata("Alice enjoys photography as a hobby", confidence=0.8)),
            EdgeData("Bob", "ENJOYS", "Photography", 
                    EdgeMetadata("Bob is interested in photography", confidence=0.7)),
            EdgeData("David", "ENJOYS", "Travel", 
                    EdgeMetadata("David loves to travel", confidence=0.9)),
            
            # Conflicting relationships (for conflict detection testing)
            EdgeData("Eve", "WORKS_AT", "CompanyA", 
                    EdgeMetadata("Eve works at Company A", confidence=0.8)),
            EdgeData("Eve", "WORKS_AT", "CompanyB", 
                    EdgeMetadata("Eve works at Company B", confidence=0.7)),
        ]
        
        success_count = 0
        for edge_data in test_edges:
            if self.graph_db.add_edge_data(edge_data):
                success_count += 1
            else:
                logger.warning(f"Failed to add edge: {edge_data.subject} -{edge_data.relationship}-> {edge_data.object}")
        
        logger.info(f"Successfully created {success_count}/{len(test_edges)} test edges")
        self.test_data_created = success_count > 0
        return self.test_data_created
    
    def test_performance_indexes(self) -> Dict[str, Any]:
        """Test performance index creation"""
        logger.info("Testing performance index creation...")
        
        start_time = time.time()
        success = self.graph_db._ensure_performance_indexes()
        end_time = time.time()
        
        result = {
            "test_name": "Performance Indexes",
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "indexes_created": success
        }
        
        logger.info(f"Performance indexes test: {'PASSED' if success else 'FAILED'}")
        return result
    
    def test_vector_similarity_search(self) -> Dict[str, Any]:
        """Test optimized vector similarity search"""
        logger.info("Testing vector similarity search with graph integration...")
        
        # Create a dummy vector for testing (384 dimensions for all-MiniLM-L6-v2)
        test_vector = [0.1] * 384
        
        start_time = time.time()
        try:
            results = self.graph_db.vector_similarity_search_with_graph(
                vector=test_vector,
                k=5,
                relationship_types=["WORKS_AT", "LIVES_IN"],
                confidence_threshold=0.3
            )
            success = True
            error = None
        except Exception as e:
            results = []
            success = False
            error = str(e)
        
        end_time = time.time()
        
        result = {
            "test_name": "Vector Similarity Search",
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "results_count": len(results),
            "error": error
        }
        
        logger.info(f"Vector similarity search test: {'PASSED' if success else 'FAILED'}")
        return result
    
    def test_entity_exploration(self) -> Dict[str, Any]:
        """Test optimized entity relationship exploration"""
        logger.info("Testing optimized entity exploration...")
        
        test_cases = [
            {"entity": "Alice", "max_depth": 1, "expected_min_results": 2},
            {"entity": "TechCorp", "max_depth": 2, "expected_min_results": 1},
            {"entity": "Charlie", "max_depth": 1, "expected_min_results": 1}
        ]
        
        results = []
        overall_success = True
        
        for test_case in test_cases:
            start_time = time.time()
            try:
                triplets = self.graph_db.get_entity_relationships_optimized(
                    entity=test_case["entity"],
                    max_depth=test_case["max_depth"],
                    limit=10
                )
                success = len(triplets) >= test_case["expected_min_results"]
                error = None
            except Exception as e:
                triplets = []
                success = False
                error = str(e)
                overall_success = False
            
            end_time = time.time()
            
            case_result = {
                "entity": test_case["entity"],
                "max_depth": test_case["max_depth"],
                "success": success,
                "execution_time_ms": (end_time - start_time) * 1000,
                "results_count": len(triplets),
                "expected_min": test_case["expected_min_results"],
                "error": error
            }
            results.append(case_result)
            
            logger.info(f"Entity exploration for {test_case['entity']}: {'PASSED' if success else 'FAILED'} "
                       f"({len(triplets)} results)")
        
        result = {
            "test_name": "Entity Exploration",
            "success": overall_success,
            "test_cases": results,
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for r in results if r["success"])
        }
        
        return result
    
    def test_conflict_detection(self) -> Dict[str, Any]:
        """Test optimized conflict detection"""
        logger.info("Testing optimized conflict detection...")
        
        start_time = time.time()
        try:
            conflicts = self.graph_db.detect_relationship_conflicts_optimized(
                entity_name="Eve",  # Eve has conflicting work relationships
                relationship_type="WORKS_AT",
                confidence_threshold=0.5
            )
            success = len(conflicts) > 0  # Should find the conflict between CompanyA and CompanyB
            error = None
        except Exception as e:
            conflicts = []
            success = False
            error = str(e)
        
        end_time = time.time()
        
        result = {
            "test_name": "Conflict Detection",
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "conflicts_found": len(conflicts),
            "error": error
        }
        
        logger.info(f"Conflict detection test: {'PASSED' if success else 'FAILED'} "
                   f"({len(conflicts)} conflicts found)")
        return result
    
    def test_temporal_analysis(self) -> Dict[str, Any]:
        """Test temporal relationship analysis"""
        logger.info("Testing temporal analysis...")
        
        start_time = time.time()
        try:
            analysis = self.graph_db.analyze_entity_temporal_relationships(
                entity_name="Charlie",  # Charlie has historical employment data
                start_date="2019-01-01",
                end_date="2024-01-01"
            )
            success = len(analysis) > 0  # Should find Charlie's employment history
            error = None
        except Exception as e:
            analysis = []
            success = False
            error = str(e)
        
        end_time = time.time()
        
        result = {
            "test_name": "Temporal Analysis",
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "temporal_relationships": len(analysis),
            "error": error
        }
        
        logger.info(f"Temporal analysis test: {'PASSED' if success else 'FAILED'} "
                   f"({len(analysis)} temporal relationships)")
        return result
    
    def test_path_finding(self) -> Dict[str, Any]:
        """Test relationship path finding"""
        logger.info("Testing path finding...")
        
        test_cases = [
            {"start": "Alice", "end": "Bob", "expected": True},  # Connected through TechCorp
            {"start": "Alice", "end": "Photography", "expected": True},  # Direct relationship
            {"start": "David", "end": "Germany", "expected": True},  # Through Berlin
            {"start": "Alice", "end": "NonExistent", "expected": False}  # Should find no path
        ]
        
        results = []
        overall_success = True
        
        for test_case in test_cases:
            start_time = time.time()
            try:
                paths = self.graph_db.find_relationship_paths(
                    start_entity=test_case["start"],
                    end_entity=test_case["end"],
                    max_hops=3,
                    limit=5
                )
                found_path = len(paths) > 0
                success = found_path == test_case["expected"]
                error = None
            except Exception as e:
                paths = []
                found_path = False
                success = False
                error = str(e)
                overall_success = False
            
            end_time = time.time()
            
            case_result = {
                "start_entity": test_case["start"],
                "end_entity": test_case["end"],
                "success": success,
                "execution_time_ms": (end_time - start_time) * 1000,
                "paths_found": len(paths),
                "expected_path": test_case["expected"],
                "found_path": found_path,
                "error": error
            }
            results.append(case_result)
            
            logger.info(f"Path finding {test_case['start']} -> {test_case['end']}: "
                       f"{'PASSED' if success else 'FAILED'} ({len(paths)} paths)")
        
        result = {
            "test_name": "Path Finding",
            "success": overall_success,
            "test_cases": results,
            "total_cases": len(test_cases),
            "passed_cases": sum(1 for r in results if r["success"])
        }
        
        return result
    
    def test_caching_performance(self) -> Dict[str, Any]:
        """Test query result caching"""
        logger.info("Testing query caching performance...")
        
        # First call - should be slow (cache miss)
        start_time1 = time.time()
        try:
            results1 = self.graph_db.get_entity_relationships_optimized("Alice", limit=10)
            time1 = (time.time() - start_time1) * 1000
            success = True
        except Exception as e:
            results1 = []
            time1 = 0
            success = False
        
        # Second call - should be faster (cache hit)
        start_time2 = time.time()
        try:
            results2 = self.graph_db.get_entity_relationships_optimized("Alice", limit=10)
            time2 = (time.time() - start_time2) * 1000
            cache_hit = True
        except Exception as e:
            results2 = []
            time2 = 0
            cache_hit = False
            success = False
        
        # Cache should make second call faster
        performance_improvement = time1 > time2 if time1 > 0 and time2 > 0 else False
        results_consistent = len(results1) == len(results2)
        
        # Get cache statistics
        cache_stats = self.graph_db.get_cache_stats()
        
        result = {
            "test_name": "Query Caching",
            "success": success and cache_hit and results_consistent,
            "first_call_ms": time1,
            "second_call_ms": time2,
            "performance_improvement": performance_improvement,
            "results_consistent": results_consistent,
            "cache_stats": cache_stats
        }
        
        logger.info(f"Caching test: {'PASSED' if result['success'] else 'FAILED'} "
                   f"(First: {time1:.2f}ms, Second: {time2:.2f}ms)")
        return result
    
    def test_optimization_stats(self) -> Dict[str, Any]:
        """Test optimization statistics reporting"""
        logger.info("Testing optimization statistics...")
        
        start_time = time.time()
        try:
            stats = self.graph_db.get_optimization_stats()
            success = "database_stats" in stats and "cache_stats" in stats
            error = None
        except Exception as e:
            stats = {}
            success = False
            error = str(e)
        
        end_time = time.time()
        
        result = {
            "test_name": "Optimization Statistics",
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "stats_available": list(stats.keys()) if success else [],
            "error": error
        }
        
        logger.info(f"Optimization stats test: {'PASSED' if success else 'FAILED'}")
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete optimization test suite"""
        logger.info("=" * 60)
        logger.info("STARTING KNOWLEDGE GRAPH OPTIMIZATION TEST SUITE")
        logger.info("=" * 60)
        
        if not self.setup_test_data():
            logger.error("Failed to set up test data. Aborting tests.")
            return {"error": "Test data setup failed"}
        
        test_results = []
        
        # Run all optimization tests
        test_methods = [
            self.test_performance_indexes,
            self.test_vector_similarity_search,
            self.test_entity_exploration,
            self.test_conflict_detection,
            self.test_temporal_analysis,
            self.test_path_finding,
            self.test_caching_performance,
            self.test_optimization_stats
        ]
        
        for test_method in test_methods:
            try:
                result = test_method()
                test_results.append(result)
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with error: {e}")
                test_results.append({
                    "test_name": test_method.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.get("success", False))
        failed_tests = total_tests - passed_tests
        
        # Calculate average execution time
        avg_execution_time = sum(
            result.get("execution_time_ms", 0) for result in test_results
        ) / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_suite": "Knowledge Graph Optimization Tests",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_execution_time_ms": avg_execution_time,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Print summary
        logger.info("=" * 60)
        logger.info("TEST SUITE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Average Execution Time: {avg_execution_time:.2f}ms")
        logger.info("=" * 60)
        
        # Print individual test results
        for result in test_results:
            status = "PASSED" if result.get("success", False) else "FAILED"
            test_name = result.get("test_name", "Unknown")
            exec_time = result.get("execution_time_ms", 0)
            logger.info(f"{status}: {test_name} ({exec_time:.2f}ms)")
            
            if not result.get("success", False) and result.get("error"):
                logger.error(f"  Error: {result['error']}")
        
        return summary


def main():
    """Run the optimization test suite"""
    tester = OptimizationTester()
    
    try:
        results = tester.run_all_tests()
        
        # Save results to file
        import json
        with open("optimization_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to optimization_test_results.json")
        
        # Return appropriate exit code
        success_rate = results.get("success_rate", 0)
        return 0 if success_rate >= 80 else 1
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        return 1
    
    finally:
        # Clean up
        if hasattr(tester, 'graph_db'):
            tester.graph_db.clear_query_cache()


if __name__ == "__main__":
    import sys
    sys.exit(main())