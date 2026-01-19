"""Test script for the Java CFG/DDG Parser API."""

import json
import httpx

BASE_URL = "http://localhost:8000/api/v1"

# Sample Java code for testing
SAMPLE_JAVA_CODE = """
public class Calculator {
    public int add(int a, int b) {
        int result = a + b;
        return result;
    }

    public int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        int fact = 1;
        for (int i = 2; i <= n; i++) {
            fact = fact * i;
        }
        return fact;
    }

    public int divide(int a, int b) {
        try {
            return a / b;
        } catch (ArithmeticException e) {
            return 0;
        }
    }
}
"""


def test_health_check():
    """Test health check endpoint."""
    print("=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    
    response = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_analyze_code():
    """Test code analysis endpoint."""
    print("=" * 60)
    print("Testing Code Analysis")
    print("=" * 60)
    
    payload = {
        "code": SAMPLE_JAVA_CODE,
        "include_class_graph": True,
        "include_method_graphs": True
    }
    
    response = httpx.post(f"{BASE_URL}/analyze", json=payload, timeout=30.0)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Class: {data['class_name']}")
        print(f"Methods found: {data['method_count']}")
        print(f"\nMethod names:")
        for method in data['method_graphs']:
            print(f"  - {method['method_name']}")
            cfg_nodes = method['cfg']['edge_list']['node_count']
            cfg_edges = method['cfg']['edge_list']['edge_count']
            ddg_nodes = method['ddg']['edge_list']['node_count']
            ddg_edges = method['ddg']['edge_list']['edge_count']
            print(f"    CFG: {cfg_nodes} nodes, {cfg_edges} edges")
            print(f"    DDG: {ddg_nodes} nodes, {ddg_edges} edges")
        
        # Save full response to file
        with open("test_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nFull response saved to test_response.json")
    else:
        print(f"Error: {response.text}")
    print()


def test_simple_method():
    """Test with a simple method."""
    print("=" * 60)
    print("Testing Simple Method")
    print("=" * 60)
    
    simple_code = """
    public class Simple {
        public int sum(int x, int y) {
            int result = x + y;
            return result;
        }
    }
    """
    
    payload = {
        "code": simple_code,
        "include_class_graph": False,
        "include_method_graphs": True
    }
    
    response = httpx.post(f"{BASE_URL}/analyze", json=payload, timeout=30.0)
    
    if response.status_code == 200:
        data = response.json()
        method = data['method_graphs'][0]
        
        print(f"Method: {method['method_name']}")
        print(f"Parameters: {method['parameters']}")
        print(f"Return type: {method['return_type']}")
        
        # Show CFG nodes
        print("\nCFG Nodes:")
        for node in method['cfg']['edge_list']['nodes'][:5]:  # First 5 nodes
            print(f"  {node['id']}: {node['type']} - {node['code'][:50]}")
        
        # Show CFG edges
        print("\nCFG Edges:")
        for edge in method['cfg']['edge_list']['edges'][:5]:  # First 5 edges
            print(f"  {edge['source']} -> {edge['target']} ({edge['type']})")
        
        # Show sequence format
        print(f"\nSequence tokens (first 10):")
        tokens = method['cfg']['sequence']['tokens'][:10]
        print(f"  {' '.join(tokens)}")
    else:
        print(f"Error: {response.text}")
    print()


def test_invalid_code():
    """Test with invalid Java code."""
    print("=" * 60)
    print("Testing Invalid Code (should fail)")
    print("=" * 60)
    
    invalid_code = "this is not valid java code {"
    
    payload = {"code": invalid_code}
    response = httpx.post(f"{BASE_URL}/analyze", json=payload, timeout=30.0)
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Expected error: {response.json()}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Java CFG/DDG Parser API Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Run tests
        test_health_check()
        test_analyze_code()
        test_simple_method()
        test_invalid_code()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except httpx.ConnectError:
        print("ERROR: Could not connect to the server.")
        print("Make sure the server is running at http://localhost:8000")
        print("\nStart it with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")
