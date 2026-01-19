"""Quick test for the parser API."""

import httpx
import json

# Simple test code
code = """
public class Test {
    public int add(int a, int b) {
        return a + b;
    }
}
"""

print("Testing parser API...")
print(f"Code:\n{code}\n")

try:
    response = httpx.post(
        "http://localhost:8000/api/v1/analyze",
        json={"code": code, "include_method_graphs": True, "include_class_graph": False},
        timeout=30.0
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n[SUCCESS]")
        print(f"Class: {data['class_name']}")
        print(f"Methods: {data['method_count']}")
        
        if data['method_graphs']:
            method = data['method_graphs'][0]
            print(f"\nMethod: {method['method_name']}")
            print(f"CFG Nodes: {method['cfg']['edge_list']['node_count']}")
            print(f"CFG Edges: {method['cfg']['edge_list']['edge_count']}")
            print(f"DDG Nodes: {method['ddg']['edge_list']['node_count']}")
            print(f"DDG Edges: {method['ddg']['edge_list']['edge_count']}")
            
            # Show first few nodes
            print("\nFirst 3 CFG Nodes:")
            for node in method['cfg']['edge_list']['nodes'][:3]:
                print(f"  {node['id']}: {node['type']} - {node['code'][:40]}")
    else:
        print(f"\n[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            # Try to get more details
            print(f"Full response headers: {dict(response.headers)}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content[:500]}")
        
except httpx.ConnectError:
    print("[ERROR] Could not connect to server. Is it running?")
except Exception as e:
    print(f"[ERROR] {e}")
