"""Manual test of the full pipeline."""

from app.services.java_parser import JavaParser
from app.services.cfg_builder import CFGBuilder
from app.services.ddg_builder import DDGBuilder
from app.services.graph_converter import GraphConverter

code = """
public class Test {
    public int add(int a, int b) {
        return a + b;
    }
}
"""

print("1. Parsing Java code...")
parser = JavaParser()
try:
    classes = parser.parse(code)
    print(f"   [OK] Parsed {len(classes)} classes")
    print(f"   Class: {classes[0].name}")
    print(f"   Methods: {len(classes[0].methods)}")
except Exception as e:
    print(f"   [ERROR] Parse error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n2. Building CFG...")
cfg_builder = CFGBuilder()
try:
    method = classes[0].methods[0]
    cfg_graph, cfg_nodes, cfg_edges = cfg_builder.build_method_cfg(method)
    print(f"   [OK] CFG built: {len(cfg_nodes)} nodes, {len(cfg_edges)} edges")
except Exception as e:
    print(f"   [ERROR] CFG build error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n3. Building DDG...")
ddg_builder = DDGBuilder()
try:
    ddg_graph, ddg_nodes, ddg_edges = ddg_builder.build_method_ddg(method, cfg_nodes)
    print(f"   [OK] DDG built: {len(ddg_nodes)} nodes, {len(ddg_edges)} edges")
except Exception as e:
    print(f"   [ERROR] DDG build error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n4. Converting graphs...")
converter = GraphConverter()
try:
    cfg_output = converter.convert(cfg_graph, cfg_nodes, cfg_edges)
    ddg_output = converter.convert(ddg_graph, ddg_nodes, ddg_edges)
    print(f"   [OK] CFG converted: edge_list={cfg_output.edge_list.node_count} nodes")
    print(f"   [OK] DDG converted: edge_list={ddg_output.edge_list.node_count} nodes")
except Exception as e:
    print(f"   [ERROR] Conversion error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n[SUCCESS] All tests passed! Pipeline works correctly.")
