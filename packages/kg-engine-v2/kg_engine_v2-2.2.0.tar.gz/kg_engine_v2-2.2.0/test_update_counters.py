#!/usr/bin/env python3
"""
Test the _update_counters method fix
"""

from src.kg_engine.core.engine import KnowledgeGraphEngineV2
from src.kg_engine.config import Neo4jConfig

def test_update_counters():
    """Test that _update_counters works correctly with different edge results"""
    print("🧪 Testing _update_counters method")
    print("=" * 50)
    
    # Initialize engine
    config = Neo4jConfig()
    engine = KnowledgeGraphEngineV2(
        api_key="test",
        neo4j_config=config
    )
    
    # Initialize results dictionary
    results = {
        "processed_items": 0,
        "new_edges": 0,
        "updated_edges": 0,
        "obsoleted_edges": 0,
        "duplicates_ignored": 0,
        "errors": [],
        "edge_results": []
    }
    
    # Test different edge result types
    test_cases = [
        {
            "name": "Created edge",
            "edge_result": {"action": "created", "message": "Edge created successfully"},
            "expected_changes": {"new_edges": 1}
        },
        {
            "name": "Updated edge", 
            "edge_result": {"action": "updated", "message": "Edge updated successfully"},
            "expected_changes": {"updated_edges": 1}
        },
        {
            "name": "Obsoleted edge",
            "edge_result": {"action": "obsoleted", "count": 2, "message": "2 edges obsoleted"},
            "expected_changes": {"obsoleted_edges": 2}
        },
        {
            "name": "Duplicate edge",
            "edge_result": {"action": "duplicate", "message": "Duplicate ignored"},
            "expected_changes": {"duplicates_ignored": 1}
        },
        {
            "name": "Error case",
            "edge_result": {"action": "error", "message": "Something went wrong"},
            "expected_changes": {"errors": ["Something went wrong"]}
        },
        {
            "name": "Error case - duplicate message",
            "edge_result": {"action": "error", "message": "Something went wrong"},
            "expected_changes": {"errors": ["Something went wrong"]}  # Should not duplicate
        },
        {
            "name": "Unknown action",
            "edge_result": {"action": "unknown_action", "message": "Unknown action"},
            "expected_changes": {}  # Should not change any counters
        }
    ]
    
    print("Testing each edge result type:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. {test_case['name']}:")
        
        # Save current state
        before_state = {
            "new_edges": results["new_edges"],
            "updated_edges": results["updated_edges"], 
            "obsoleted_edges": results["obsoleted_edges"],
            "duplicates_ignored": results["duplicates_ignored"],
            "errors": results["errors"].copy()
        }
        
        # Apply the update
        try:
            engine._update_counters(results, test_case["edge_result"])
            print(f"   ✅ Method executed successfully")
            
            # Check expected changes
            success = True
            for key, expected_value in test_case["expected_changes"].items():
                if key == "errors":
                    # For errors, check if all expected messages are present
                    for expected_msg in expected_value:
                        if expected_msg not in results[key]:
                            print(f"   ❌ Expected error message '{expected_msg}' not found")
                            success = False
                    # Also check we don't have duplicates for the duplicate error test
                    if test_case["name"] == "Error case - duplicate message":
                        error_count = results["errors"].count("Something went wrong")
                        if error_count > 1:
                            print(f"   ❌ Duplicate error message found ({error_count} times)")
                            success = False
                        else:
                            print(f"   ✅ Duplicate error correctly prevented")
                else:
                    # For numeric counters, check exact values
                    actual_change = results[key] - before_state[key]
                    if isinstance(expected_value, int):
                        if actual_change != expected_value:
                            print(f"   ❌ Expected {key} to increase by {expected_value}, but increased by {actual_change}")
                            success = False
                        else:
                            print(f"   ✅ {key} correctly increased by {expected_value}")
            
            if success and not test_case["expected_changes"]:
                print(f"   ✅ No changes applied as expected")
                
        except Exception as e:
            print(f"   ❌ Method failed with error: {e}")
    
    print(f"\n" + "=" * 50)
    print("Final Results Summary:")
    print(f"  - New edges: {results['new_edges']}")
    print(f"  - Updated edges: {results['updated_edges']}")
    print(f"  - Obsoleted edges: {results['obsoleted_edges']}")
    print(f"  - Duplicates ignored: {results['duplicates_ignored']}")
    print(f"  - Errors: {len(results['errors'])} ({results['errors']})")
    
    # Verify totals
    expected_totals = {
        "new_edges": 1,
        "updated_edges": 1,
        "obsoleted_edges": 2,
        "duplicates_ignored": 1,
        "errors": 1  # Should be 1, not 2 due to duplicate prevention
    }
    
    print(f"\nValidation:")
    all_correct = True
    for key, expected in expected_totals.items():
        actual = len(results[key]) if key == "errors" else results[key]
        if actual == expected:
            print(f"  ✅ {key}: {actual} (correct)")
        else:
            print(f"  ❌ {key}: {actual} (expected {expected})")
            all_correct = False
    
    if all_correct:
        print(f"\n🎉 All tests passed! _update_counters is working correctly.")
        return True
    else:
        print(f"\n❌ Some tests failed. Please check the implementation.")
        return False

def main():
    """Run the update counters test"""
    try:
        success = test_update_counters()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())