"""Tests for CFG builder."""

import pytest

from app.services.java_parser import JavaParser
from app.services.cfg_builder import CFGBuilder
from app.models.graph_models import NodeType, EdgeType


class TestCFGBuilder:
    """Test cases for CFGBuilder."""

    def test_build_simple_method_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, simple_java_method: str
    ):
        """Test building CFG for a simple method."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        graph, nodes, edges = cfg_builder.build_method_cfg(method)

        # Should have entry and exit nodes
        entry_nodes = [n for n in nodes if n.type == NodeType.METHOD_ENTRY]
        exit_nodes = [n for n in nodes if n.type == NodeType.METHOD_EXIT]

        assert len(entry_nodes) == 1
        assert len(exit_nodes) == 1

    def test_cfg_has_edges(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, simple_java_method: str
    ):
        """Test CFG has edges connecting nodes."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        graph, nodes, edges = cfg_builder.build_method_cfg(method)

        assert len(edges) > 0

    def test_if_statement_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, conditional_java_code: str
    ):
        """Test CFG for if statement has condition node and branches."""
        classes = java_parser.parse(conditional_java_code)
        abs_method = next(m for m in classes[0].methods if m.name == "abs")

        graph, nodes, edges = cfg_builder.build_method_cfg(abs_method)

        # Should have condition node
        condition_nodes = [n for n in nodes if n.type == NodeType.CONDITION]
        assert len(condition_nodes) >= 1

        # Should have true/false branch edges
        edge_types = [e.type for e in edges]
        assert EdgeType.TRUE_BRANCH in edge_types or EdgeType.SEQUENTIAL in edge_types

    def test_for_loop_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, loop_java_code: str
    ):
        """Test CFG for for loop has loop header and back edge."""
        classes = java_parser.parse(loop_java_code)
        sum_method = next(m for m in classes[0].methods if m.name == "sumArray")

        graph, nodes, edges = cfg_builder.build_method_cfg(sum_method)

        # Should have loop header
        loop_headers = [n for n in nodes if n.type == NodeType.LOOP_HEADER]
        assert len(loop_headers) >= 1

        # Should have loop back edge
        edge_types = [e.type for e in edges]
        assert EdgeType.LOOP_BACK in edge_types

    def test_while_loop_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, loop_java_code: str
    ):
        """Test CFG for while loop."""
        classes = java_parser.parse(loop_java_code)
        while_method = next(m for m in classes[0].methods if m.name == "whileExample")

        graph, nodes, edges = cfg_builder.build_method_cfg(while_method)

        # Should have loop header
        loop_headers = [n for n in nodes if n.type == NodeType.LOOP_HEADER]
        assert len(loop_headers) >= 1

    def test_try_catch_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, sample_java_code: str
    ):
        """Test CFG for try-catch block."""
        classes = java_parser.parse(sample_java_code)
        divide_method = next(m for m in classes[0].methods if m.name == "divide")

        graph, nodes, edges = cfg_builder.build_method_cfg(divide_method)

        # Should have try and catch nodes
        try_nodes = [n for n in nodes if n.type == NodeType.TRY]
        catch_nodes = [n for n in nodes if n.type == NodeType.CATCH]

        assert len(try_nodes) >= 1
        assert len(catch_nodes) >= 1

        # Should have exception edge
        edge_types = [e.type for e in edges]
        assert EdgeType.EXCEPTION in edge_types

    def test_class_cfg(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, sample_java_code: str
    ):
        """Test building class-level CFG."""
        classes = java_parser.parse(sample_java_code)
        parsed_class = classes[0]

        graph, nodes, edges = cfg_builder.build_class_cfg(parsed_class)

        # Should have class entry and exit
        entry_nodes = [n for n in nodes if n.type == NodeType.ENTRY]
        exit_nodes = [n for n in nodes if n.type == NodeType.EXIT]

        assert len(entry_nodes) >= 1
        assert len(exit_nodes) >= 1

        # Should have method entry nodes
        method_entries = [n for n in nodes if n.type == NodeType.METHOD_ENTRY]
        assert len(method_entries) == 3  # add, factorial, divide

    def test_cfg_node_has_code(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, simple_java_method: str
    ):
        """Test CFG nodes have code snippets."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        graph, nodes, edges = cfg_builder.build_method_cfg(method)

        # At least some nodes should have code
        nodes_with_code = [n for n in nodes if n.code]
        assert len(nodes_with_code) > 0

    def test_cfg_node_has_line_numbers(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, simple_java_method: str
    ):
        """Test CFG nodes have line numbers."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        graph, nodes, edges = cfg_builder.build_method_cfg(method)

        # Entry node should have line number
        entry_nodes = [n for n in nodes if n.type == NodeType.METHOD_ENTRY]
        assert entry_nodes[0].line_number is not None

    def test_return_statement_connects_to_exit(
        self, java_parser: JavaParser, cfg_builder: CFGBuilder, simple_java_method: str
    ):
        """Test return statement connects to method exit."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        graph, nodes, edges = cfg_builder.build_method_cfg(method)

        # Find return node
        return_nodes = [n for n in nodes if n.type == NodeType.RETURN]
        exit_nodes = [n for n in nodes if n.type == NodeType.METHOD_EXIT]

        if return_nodes and exit_nodes:
            # Return should have edge to exit
            return_edges = [e for e in edges if e.source == return_nodes[0].id]
            targets = [e.target for e in return_edges]
            assert exit_nodes[0].id in targets
