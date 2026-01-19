"""Control Flow Graph builder from parsed Java AST."""

from typing import Any

import networkx as nx

from app.models.graph_models import GraphNode, GraphEdge, NodeType, EdgeType
from app.services.java_parser import ParsedMethod, ParsedStatement, ParsedClass
from app.core.exceptions import CFGBuildError


class CFGBuilder:
    """Builds Control Flow Graphs from parsed Java methods."""

    def __init__(self) -> None:
        self._node_counter: int = 0
        self._graph: nx.DiGraph = nx.DiGraph()

    def build_method_cfg(self, method: ParsedMethod) -> tuple[nx.DiGraph, list[GraphNode], list[GraphEdge]]:
        """Build CFG for a single method.

        Args:
            method: Parsed method to build CFG for.

        Returns:
            Tuple of (NetworkX DiGraph, list of nodes, list of edges).
        """
        self._reset()

        # Create entry node
        entry_node = self._create_node(
            NodeType.METHOD_ENTRY,
            f"ENTRY: {method.name}",
            method.line_start,
            vars_defined=method.parameters.copy(),
        )

        # Create exit node
        exit_node = self._create_node(
            NodeType.METHOD_EXIT,
            f"EXIT: {method.name}",
            method.line_end,
        )

        # Build CFG for method body
        if method.statements:
            first_stmt_node, last_nodes = self._build_cfg_for_statements(
                method.statements, exit_node
            )
            if first_stmt_node:
                self._add_edge(entry_node, first_stmt_node, EdgeType.SEQUENTIAL)
            else:
                self._add_edge(entry_node, exit_node, EdgeType.SEQUENTIAL)

            # Connect all terminal nodes to exit
            for last_node in last_nodes:
                if last_node.id != exit_node.id:
                    self._add_edge(last_node, exit_node, EdgeType.SEQUENTIAL)
        else:
            self._add_edge(entry_node, exit_node, EdgeType.SEQUENTIAL)

        nodes = self._get_all_nodes()
        edges = self._get_all_edges()

        return self._graph, nodes, edges

    def build_class_cfg(self, parsed_class: ParsedClass) -> tuple[nx.DiGraph, list[GraphNode], list[GraphEdge]]:
        """Build combined CFG for all methods in a class.

        Args:
            parsed_class: Parsed class to build CFG for.

        Returns:
            Tuple of (NetworkX DiGraph, list of nodes, list of edges).
        """
        self._reset()

        # Create class entry node
        class_entry = self._create_node(
            NodeType.ENTRY,
            f"CLASS: {parsed_class.name}",
            parsed_class.line_start,
        )

        # Create class exit node
        class_exit = self._create_node(
            NodeType.EXIT,
            f"END CLASS: {parsed_class.name}",
            parsed_class.line_end,
        )

        method_entries: list[GraphNode] = []
        method_exits: list[GraphNode] = []

        for method in parsed_class.methods:
            # Create method entry
            method_entry = self._create_node(
                NodeType.METHOD_ENTRY,
                f"METHOD: {method.name}",
                method.line_start,
                vars_defined=method.parameters.copy(),
            )
            method_entries.append(method_entry)

            # Create method exit
            method_exit = self._create_node(
                NodeType.METHOD_EXIT,
                f"END METHOD: {method.name}",
                method.line_end,
            )
            method_exits.append(method_exit)

            # Build CFG for method body
            if method.statements:
                first_stmt, last_nodes = self._build_cfg_for_statements(
                    method.statements, method_exit
                )
                if first_stmt:
                    self._add_edge(method_entry, first_stmt, EdgeType.SEQUENTIAL)
                else:
                    self._add_edge(method_entry, method_exit, EdgeType.SEQUENTIAL)

                for last_node in last_nodes:
                    if last_node.id != method_exit.id:
                        self._add_edge(last_node, method_exit, EdgeType.SEQUENTIAL)
            else:
                self._add_edge(method_entry, method_exit, EdgeType.SEQUENTIAL)

            # Connect to class structure
            self._add_edge(class_entry, method_entry, EdgeType.CALL)
            self._add_edge(method_exit, class_exit, EdgeType.RETURN_EDGE)

        nodes = self._get_all_nodes()
        edges = self._get_all_edges()

        return self._graph, nodes, edges

    def _build_cfg_for_statements(
        self, statements: list[ParsedStatement], exit_node: GraphNode
    ) -> tuple[GraphNode | None, list[GraphNode]]:
        """Build CFG for a list of statements.

        Returns:
            Tuple of (first node, list of terminal nodes that need connection).
        """
        if not statements:
            return None, []

        first_node: GraphNode | None = None
        prev_nodes: list[GraphNode] = []

        for i, stmt in enumerate(statements):
            stmt_first, stmt_last = self._build_cfg_for_statement(stmt, exit_node)

            if stmt_first is None:
                continue

            if first_node is None:
                first_node = stmt_first

            # Connect previous nodes to current statement
            for prev in prev_nodes:
                self._add_edge(prev, stmt_first, EdgeType.SEQUENTIAL)

            prev_nodes = stmt_last

        return first_node, prev_nodes

    def _build_cfg_for_statement(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode | None, list[GraphNode]]:
        """Build CFG for a single statement.

        Returns:
            Tuple of (first node, list of terminal nodes).
        """
        if stmt.statement_type == "IF":
            return self._build_if_cfg(stmt, exit_node)
        elif stmt.statement_type == "WHILE":
            return self._build_while_cfg(stmt, exit_node)
        elif stmt.statement_type == "FOR":
            return self._build_for_cfg(stmt, exit_node)
        elif stmt.statement_type == "DO_WHILE":
            return self._build_do_while_cfg(stmt, exit_node)
        elif stmt.statement_type == "SWITCH":
            return self._build_switch_cfg(stmt, exit_node)
        elif stmt.statement_type == "TRY":
            return self._build_try_cfg(stmt, exit_node)
        elif stmt.statement_type == "RETURN":
            return self._build_return_cfg(stmt, exit_node)
        elif stmt.statement_type == "THROW":
            return self._build_throw_cfg(stmt, exit_node)
        elif stmt.statement_type in ("BREAK", "CONTINUE"):
            return self._build_jump_cfg(stmt)
        elif stmt.statement_type == "BLOCK":
            return self._build_cfg_for_statements(stmt.children, exit_node)
        else:
            return self._build_simple_statement_cfg(stmt)

    def _build_if_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for if statement."""
        condition_node = self._create_node(
            NodeType.CONDITION,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
            stmt.metadata,
        )

        terminal_nodes: list[GraphNode] = []

        # Find then and else branches in children
        has_else = stmt.metadata.get("has_else", False)
        mid_point = len(stmt.children) // 2 if has_else else len(stmt.children)

        then_children = stmt.children[:mid_point] if has_else else stmt.children
        else_children = stmt.children[mid_point:] if has_else else []

        # Build then branch
        if then_children:
            then_first, then_last = self._build_cfg_for_statements(then_children, exit_node)
            if then_first:
                self._add_edge(condition_node, then_first, EdgeType.TRUE_BRANCH, "true")
                terminal_nodes.extend(then_last)
            else:
                terminal_nodes.append(condition_node)
        else:
            terminal_nodes.append(condition_node)

        # Build else branch
        if else_children:
            else_first, else_last = self._build_cfg_for_statements(else_children, exit_node)
            if else_first:
                self._add_edge(condition_node, else_first, EdgeType.FALSE_BRANCH, "false")
                terminal_nodes.extend(else_last)
            else:
                terminal_nodes.append(condition_node)
        else:
            # No else branch - condition can fall through
            terminal_nodes.append(condition_node)

        return condition_node, terminal_nodes

    def _build_while_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for while loop."""
        condition_node = self._create_node(
            NodeType.LOOP_HEADER,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
            stmt.metadata,
        )

        # Build loop body
        if stmt.children:
            body_first, body_last = self._build_cfg_for_statements(stmt.children, exit_node)
            if body_first:
                self._add_edge(condition_node, body_first, EdgeType.TRUE_BRANCH, "true")
                # Loop back edges
                for last in body_last:
                    self._add_edge(last, condition_node, EdgeType.LOOP_BACK)
        
        # Condition is the only terminal (loop exit)
        return condition_node, [condition_node]

    def _build_for_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for for loop."""
        # For loop header (contains init, condition, update)
        header_node = self._create_node(
            NodeType.LOOP_HEADER,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
            stmt.metadata,
        )

        # Build loop body
        if stmt.children:
            body_first, body_last = self._build_cfg_for_statements(stmt.children, exit_node)
            if body_first:
                self._add_edge(header_node, body_first, EdgeType.TRUE_BRANCH, "true")
                # Loop back edges
                for last in body_last:
                    self._add_edge(last, header_node, EdgeType.LOOP_BACK)

        return header_node, [header_node]

    def _build_do_while_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for do-while loop."""
        # Body entry node
        body_entry = self._create_node(
            NodeType.STATEMENT,
            "do",
            stmt.line_number,
        )

        # Condition node
        condition_node = self._create_node(
            NodeType.LOOP_HEADER,
            f"while ({stmt.metadata.get('condition', '')})",
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
        )

        # Build body
        if stmt.children:
            body_first, body_last = self._build_cfg_for_statements(stmt.children, exit_node)
            if body_first:
                self._add_edge(body_entry, body_first, EdgeType.SEQUENTIAL)
                for last in body_last:
                    self._add_edge(last, condition_node, EdgeType.SEQUENTIAL)
            else:
                self._add_edge(body_entry, condition_node, EdgeType.SEQUENTIAL)
        else:
            self._add_edge(body_entry, condition_node, EdgeType.SEQUENTIAL)

        # Loop back from condition
        self._add_edge(condition_node, body_entry, EdgeType.LOOP_BACK, "true")

        return body_entry, [condition_node]

    def _build_switch_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for switch statement."""
        switch_node = self._create_node(
            NodeType.SWITCH,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
            stmt.metadata,
        )

        terminal_nodes: list[GraphNode] = []

        for case_stmt in stmt.children:
            case_node = self._create_node(
                NodeType.CASE if case_stmt.statement_type == "CASE" else NodeType.CASE,
                case_stmt.code,
                case_stmt.line_number,
                case_stmt.column,
            )

            edge_type = EdgeType.DEFAULT_BRANCH if case_stmt.statement_type == "DEFAULT" else EdgeType.CASE_BRANCH
            self._add_edge(switch_node, case_node, edge_type, case_stmt.code)

            if case_stmt.children:
                case_first, case_last = self._build_cfg_for_statements(case_stmt.children, exit_node)
                if case_first:
                    self._add_edge(case_node, case_first, EdgeType.SEQUENTIAL)
                    terminal_nodes.extend(case_last)
                else:
                    terminal_nodes.append(case_node)
            else:
                terminal_nodes.append(case_node)

        return switch_node, terminal_nodes

    def _build_try_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for try-catch-finally."""
        try_node = self._create_node(
            NodeType.TRY,
            stmt.code,
            stmt.line_number,
            stmt.column,
        )

        terminal_nodes: list[GraphNode] = []
        finally_node: GraphNode | None = None

        for child in stmt.children:
            if child.statement_type == "TRY_BLOCK":
                if child.children:
                    try_first, try_last = self._build_cfg_for_statements(child.children, exit_node)
                    if try_first:
                        self._add_edge(try_node, try_first, EdgeType.SEQUENTIAL)
                        terminal_nodes.extend(try_last)

            elif child.statement_type == "CATCH":
                catch_node = self._create_node(
                    NodeType.CATCH,
                    child.code,
                    child.line_number,
                    child.column,
                    child.variables_defined,
                )
                self._add_edge(try_node, catch_node, EdgeType.EXCEPTION)

                if child.children:
                    catch_first, catch_last = self._build_cfg_for_statements(child.children, exit_node)
                    if catch_first:
                        self._add_edge(catch_node, catch_first, EdgeType.SEQUENTIAL)
                        terminal_nodes.extend(catch_last)
                    else:
                        terminal_nodes.append(catch_node)
                else:
                    terminal_nodes.append(catch_node)

            elif child.statement_type == "FINALLY":
                finally_node = self._create_node(
                    NodeType.FINALLY,
                    "finally",
                    child.line_number,
                )
                if child.children:
                    finally_first, finally_last = self._build_cfg_for_statements(child.children, exit_node)
                    if finally_first:
                        self._add_edge(finally_node, finally_first, EdgeType.SEQUENTIAL)
                        # Connect all terminals to finally
                        for term in terminal_nodes:
                            self._add_edge(term, finally_node, EdgeType.FINALLY_EDGE)
                        terminal_nodes = finally_last
                    else:
                        for term in terminal_nodes:
                            self._add_edge(term, finally_node, EdgeType.FINALLY_EDGE)
                        terminal_nodes = [finally_node]

        if not terminal_nodes:
            terminal_nodes = [try_node]

        return try_node, terminal_nodes

    def _build_return_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for return statement."""
        return_node = self._create_node(
            NodeType.RETURN,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
        )
        # Return directly connects to exit
        self._add_edge(return_node, exit_node, EdgeType.RETURN_EDGE)
        return return_node, []  # No successor nodes

    def _build_throw_cfg(
        self, stmt: ParsedStatement, exit_node: GraphNode
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for throw statement."""
        throw_node = self._create_node(
            NodeType.THROW,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
        )
        # Throw connects to exit (exception path)
        self._add_edge(throw_node, exit_node, EdgeType.EXCEPTION)
        return throw_node, []  # No normal successor

    def _build_jump_cfg(
        self, stmt: ParsedStatement
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for break/continue."""
        node_type = NodeType.BREAK if stmt.statement_type == "BREAK" else NodeType.CONTINUE
        jump_node = self._create_node(
            node_type,
            stmt.code,
            stmt.line_number,
            stmt.column,
        )
        # Break/continue need special handling in loop context
        return jump_node, []

    def _build_simple_statement_cfg(
        self, stmt: ParsedStatement
    ) -> tuple[GraphNode, list[GraphNode]]:
        """Build CFG for simple statements."""
        node_type = self._map_statement_type(stmt.statement_type)
        node = self._create_node(
            node_type,
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
            stmt.metadata,
        )
        return node, [node]

    def _map_statement_type(self, stmt_type: str) -> NodeType:
        """Map statement type string to NodeType enum."""
        mapping = {
            "ASSIGNMENT": NodeType.ASSIGNMENT,
            "DECLARATION": NodeType.DECLARATION,
            "METHOD_CALL": NodeType.METHOD_CALL,
            "EXPRESSION": NodeType.STATEMENT,
            "STATEMENT": NodeType.STATEMENT,
        }
        return mapping.get(stmt_type, NodeType.STATEMENT)

    def _reset(self) -> None:
        """Reset builder state."""
        self._node_counter = 0
        self._graph = nx.DiGraph()

    def _create_node(
        self,
        node_type: NodeType,
        code: str,
        line: int | None,
        column: int | None = None,
        vars_defined: list[str] | None = None,
        vars_used: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GraphNode:
        """Create a new graph node."""
        node_id = f"n{self._node_counter}"
        self._node_counter += 1

        node = GraphNode(
            id=node_id,
            type=node_type,
            code=code,
            line_number=line,
            column=column,
            variables_defined=vars_defined or [],
            variables_used=vars_used or [],
            metadata=metadata or {},
        )

        self._graph.add_node(
            node_id,
            type=node_type.value,
            code=code,
            line=line,
            vars_def=vars_defined or [],
            vars_use=vars_used or [],
        )

        return node

    def _add_edge(
        self,
        source: GraphNode,
        target: GraphNode,
        edge_type: EdgeType,
        label: str = "",
    ) -> GraphEdge:
        """Add an edge between two nodes."""
        edge = GraphEdge(
            source=source.id,
            target=target.id,
            type=edge_type,
            label=label,
        )

        self._graph.add_edge(
            source.id,
            target.id,
            type=edge_type.value,
            label=label,
        )

        return edge

    def _get_all_nodes(self) -> list[GraphNode]:
        """Get all nodes from the graph."""
        nodes = []
        for node_id in self._graph.nodes():
            data = self._graph.nodes[node_id]
            node = GraphNode(
                id=node_id,
                type=NodeType(data.get("type", "STATEMENT")),
                code=data.get("code", ""),
                line_number=data.get("line"),
                column=data.get("column"),
                variables_defined=data.get("vars_def", []),
                variables_used=data.get("vars_use", []),
            )
            nodes.append(node)
        return nodes

    def _get_all_edges(self) -> list[GraphEdge]:
        """Get all edges from the graph."""
        edges = []
        for source, target, data in self._graph.edges(data=True):
            edge = GraphEdge(
                source=source,
                target=target,
                type=EdgeType(data.get("type", "SEQUENTIAL")),
                label=data.get("label", ""),
            )
            edges.append(edge)
        return edges
