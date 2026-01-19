"""Data Dependence Graph builder using def-use chain analysis."""

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from app.models.graph_models import GraphNode, GraphEdge, NodeType, EdgeType
from app.services.java_parser import ParsedMethod, ParsedStatement, ParsedClass
from app.core.exceptions import DDGBuildError


@dataclass
class VariableDefinition:
    """Represents a variable definition point."""

    variable: str
    node_id: str
    line: int | None
    is_parameter: bool = False


@dataclass
class VariableUse:
    """Represents a variable use point."""

    variable: str
    node_id: str
    line: int | None


@dataclass
class DefUseChain:
    """Represents a def-use chain for a variable."""

    variable: str
    definition: VariableDefinition
    uses: list[VariableUse] = field(default_factory=list)


class DDGBuilder:
    """Builds Data Dependence Graphs using def-use chain analysis."""

    def __init__(self) -> None:
        self._node_counter: int = 0
        self._graph: nx.DiGraph = nx.DiGraph()
        self._definitions: dict[str, list[VariableDefinition]] = {}
        self._uses: dict[str, list[VariableUse]] = {}
        self._node_map: dict[str, GraphNode] = {}
        self._reaching_definitions: dict[str, dict[str, set[str]]] = {}

    def build_method_ddg(
        self, method: ParsedMethod, cfg_nodes: list[GraphNode]
    ) -> tuple[nx.DiGraph, list[GraphNode], list[GraphEdge]]:
        """Build DDG for a single method.

        Args:
            method: Parsed method to analyze.
            cfg_nodes: CFG nodes for reference.

        Returns:
            Tuple of (NetworkX DiGraph, list of nodes, list of edges).
        """
        self._reset()

        # Create entry node for parameters
        entry_node = self._create_node(
            NodeType.METHOD_ENTRY,
            f"PARAMS: {', '.join(method.parameters)}",
            method.line_start,
            vars_defined=method.parameters.copy(),
        )

        # Register parameter definitions
        for param in method.parameters:
            self._register_definition(param, entry_node.id, method.line_start, is_parameter=True)

        # Process all statements to collect defs and uses
        self._process_statements(method.statements)

        # Build def-use edges
        self._build_def_use_edges()

        nodes = self._get_all_nodes()
        edges = self._get_all_edges()

        return self._graph, nodes, edges

    def build_class_ddg(
        self, parsed_class: ParsedClass, cfg_nodes: list[GraphNode]
    ) -> tuple[nx.DiGraph, list[GraphNode], list[GraphEdge]]:
        """Build combined DDG for all methods in a class.

        Args:
            parsed_class: Parsed class to analyze.
            cfg_nodes: CFG nodes for reference.

        Returns:
            Tuple of (NetworkX DiGraph, list of nodes, list of edges).
        """
        self._reset()

        # Create class-level field definitions
        if parsed_class.fields:
            fields_node = self._create_node(
                NodeType.DECLARATION,
                f"FIELDS: {', '.join(parsed_class.fields)}",
                parsed_class.line_start,
                vars_defined=parsed_class.fields.copy(),
            )
            for field_name in parsed_class.fields:
                self._register_definition(field_name, fields_node.id, parsed_class.line_start)

        # Process each method
        for method in parsed_class.methods:
            # Create entry node for method parameters
            method_entry = self._create_node(
                NodeType.METHOD_ENTRY,
                f"METHOD {method.name}: {', '.join(method.parameters)}",
                method.line_start,
                vars_defined=method.parameters.copy(),
            )

            for param in method.parameters:
                self._register_definition(param, method_entry.id, method.line_start, is_parameter=True)

            # Process method statements
            self._process_statements(method.statements)

        # Build def-use edges
        self._build_def_use_edges()

        nodes = self._get_all_nodes()
        edges = self._get_all_edges()

        return self._graph, nodes, edges

    def _process_statements(self, statements: list[ParsedStatement]) -> None:
        """Process statements to extract definitions and uses."""
        for stmt in statements:
            self._process_statement(stmt)

    def _process_statement(self, stmt: ParsedStatement) -> None:
        """Process a single statement."""
        # Create node for this statement
        node = self._create_node(
            self._map_statement_type(stmt.statement_type),
            stmt.code,
            stmt.line_number,
            stmt.column,
            stmt.variables_defined,
            stmt.variables_used,
        )

        # Register definitions
        for var in stmt.variables_defined:
            self._register_definition(var, node.id, stmt.line_number)

        # Register uses
        for var in stmt.variables_used:
            self._register_use(var, node.id, stmt.line_number)

        # Process children recursively
        for child in stmt.children:
            self._process_statement(child)

    def _register_definition(
        self, variable: str, node_id: str, line: int | None, is_parameter: bool = False
    ) -> None:
        """Register a variable definition."""
        definition = VariableDefinition(
            variable=variable,
            node_id=node_id,
            line=line,
            is_parameter=is_parameter,
        )

        if variable not in self._definitions:
            self._definitions[variable] = []
        self._definitions[variable].append(definition)

    def _register_use(self, variable: str, node_id: str, line: int | None) -> None:
        """Register a variable use."""
        use = VariableUse(
            variable=variable,
            node_id=node_id,
            line=line,
        )

        if variable not in self._uses:
            self._uses[variable] = []
        self._uses[variable].append(use)

    def _build_def_use_edges(self) -> None:
        """Build edges from definitions to uses using reaching definitions."""
        for variable, uses in self._uses.items():
            if variable not in self._definitions:
                continue

            definitions = self._definitions[variable]

            for use in uses:
                # Find the most recent definition before this use
                reaching_def = self._find_reaching_definition(variable, use, definitions)

                if reaching_def:
                    self._add_edge(
                        reaching_def.node_id,
                        use.node_id,
                        EdgeType.DATA_DEP,
                        variable,
                    )

    def _find_reaching_definition(
        self,
        variable: str,
        use: VariableUse,
        definitions: list[VariableDefinition],
    ) -> VariableDefinition | None:
        """Find the reaching definition for a use.

        Uses a simple heuristic: the most recent definition before the use line.
        For more accurate analysis, proper data-flow analysis would be needed.
        """
        reaching: VariableDefinition | None = None

        for defn in definitions:
            # Definition must come before use
            if defn.line is None or use.line is None:
                # If no line info, include all definitions
                if reaching is None:
                    reaching = defn
                continue

            if defn.line <= use.line:
                # Parameters always reach (unless overwritten)
                if defn.is_parameter:
                    if reaching is None or not reaching.is_parameter:
                        reaching = defn
                elif reaching is None or (reaching.line is not None and defn.line > reaching.line):
                    reaching = defn

        return reaching

    def _build_use_def_edges(self) -> None:
        """Build edges from uses to their next definitions (anti-dependence)."""
        for variable, definitions in self._definitions.items():
            if variable not in self._uses:
                continue

            uses = self._uses[variable]

            for defn in definitions:
                for use in uses:
                    # Use must come before definition
                    if use.line and defn.line and use.line < defn.line:
                        # Check if this is the closest following definition
                        is_closest = True
                        for other_def in definitions:
                            if (other_def.line and use.line and other_def.node_id != defn.node_id
                                    and use.line < other_def.line < defn.line):
                                is_closest = False
                                break

                        if is_closest and use.node_id != defn.node_id:
                            self._add_edge(
                                use.node_id,
                                defn.node_id,
                                EdgeType.USE_DEF,
                                variable,
                            )

    def _map_statement_type(self, stmt_type: str) -> NodeType:
        """Map statement type string to NodeType enum."""
        mapping = {
            "IF": NodeType.CONDITION,
            "WHILE": NodeType.LOOP_HEADER,
            "FOR": NodeType.LOOP_HEADER,
            "DO_WHILE": NodeType.LOOP_HEADER,
            "SWITCH": NodeType.SWITCH,
            "CASE": NodeType.CASE,
            "DEFAULT": NodeType.CASE,
            "TRY": NodeType.TRY,
            "TRY_BLOCK": NodeType.TRY,
            "CATCH": NodeType.CATCH,
            "FINALLY": NodeType.FINALLY,
            "RETURN": NodeType.RETURN,
            "THROW": NodeType.THROW,
            "BREAK": NodeType.BREAK,
            "CONTINUE": NodeType.CONTINUE,
            "ASSIGNMENT": NodeType.ASSIGNMENT,
            "DECLARATION": NodeType.DECLARATION,
            "METHOD_CALL": NodeType.METHOD_CALL,
        }
        return mapping.get(stmt_type, NodeType.STATEMENT)

    def _reset(self) -> None:
        """Reset builder state."""
        self._node_counter = 0
        self._graph = nx.DiGraph()
        self._definitions = {}
        self._uses = {}
        self._node_map = {}
        self._reaching_definitions = {}

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
        node_id = f"d{self._node_counter}"
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

        self._node_map[node_id] = node
        return node

    def _add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        variable: str,
    ) -> GraphEdge:
        """Add a data dependence edge."""
        # Avoid self-loops and duplicate edges
        if source_id == target_id:
            return GraphEdge(source=source_id, target=target_id, type=edge_type, variable=variable)

        if self._graph.has_edge(source_id, target_id):
            # Check if edge with same variable already exists
            existing = self._graph.edges[source_id, target_id]
            existing_vars = existing.get("variables", [])
            if variable not in existing_vars:
                existing_vars.append(variable)
                self._graph.edges[source_id, target_id]["variables"] = existing_vars
            return GraphEdge(source=source_id, target=target_id, type=edge_type, variable=variable)

        edge = GraphEdge(
            source=source_id,
            target=target_id,
            type=edge_type,
            variable=variable,
            label=f"dep:{variable}",
        )

        self._graph.add_edge(
            source_id,
            target_id,
            type=edge_type.value,
            variable=variable,
            variables=[variable],
            label=f"dep:{variable}",
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
            # Create an edge for each variable dependency
            variables = data.get("variables", [data.get("variable", "")])
            for var in variables:
                edge = GraphEdge(
                    source=source,
                    target=target,
                    type=EdgeType(data.get("type", "DATA_DEP")),
                    variable=var,
                    label=f"dep:{var}",
                )
                edges.append(edge)
                break  # Only add one edge per pair
        return edges
