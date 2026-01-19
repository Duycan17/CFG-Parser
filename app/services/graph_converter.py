"""Graph format converters for transformer model input."""

from collections import deque
from typing import Any

import networkx as nx
import numpy as np

from app.models.graph_models import (
    GraphNode,
    GraphEdge,
    GraphOutput,
    EdgeListFormat,
    AdjacencyMatrixFormat,
    SequenceFormat,
)


class GraphConverter:
    """Converts graphs to various formats suitable for transformer models."""

    def convert(
        self,
        graph: nx.DiGraph,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> GraphOutput:
        """Convert a graph to all output formats.

        Args:
            graph: NetworkX directed graph.
            nodes: List of graph nodes.
            edges: List of graph edges.

        Returns:
            GraphOutput containing all format representations.
        """
        edge_list = self._to_edge_list(nodes, edges)
        adjacency_matrix = self._to_adjacency_matrix(graph, nodes, edges)
        sequence = self._to_sequence(graph, nodes)

        return GraphOutput(
            edge_list=edge_list,
            adjacency_matrix=adjacency_matrix,
            sequence=sequence,
        )

    def _to_edge_list(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> EdgeListFormat:
        """Convert to edge list format.

        Format suitable for GNN/Transformer models that consume edge lists.
        """
        return EdgeListFormat(
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges),
        )

    def _to_adjacency_matrix(
        self,
        graph: nx.DiGraph,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> AdjacencyMatrixFormat:
        """Convert to adjacency matrix format.

        Creates a dense adjacency matrix with node ID mappings.
        """
        if not nodes:
            return AdjacencyMatrixFormat(
                matrix=[],
                node_ids=[],
                node_types=[],
                edge_types_matrix=[],
            )

        # Create node ID to index mapping
        node_ids = [node.id for node in nodes]
        node_types = [node.type.value for node in nodes]
        id_to_idx = {nid: idx for idx, nid in enumerate(node_ids)}

        n = len(nodes)

        # Initialize matrices
        adjacency = [[0] * n for _ in range(n)]
        edge_types: list[list[str | None]] = [[None] * n for _ in range(n)]

        # Fill matrices from edges
        for edge in edges:
            if edge.source in id_to_idx and edge.target in id_to_idx:
                src_idx = id_to_idx[edge.source]
                tgt_idx = id_to_idx[edge.target]
                adjacency[src_idx][tgt_idx] = 1
                edge_types[src_idx][tgt_idx] = edge.type.value

        return AdjacencyMatrixFormat(
            matrix=adjacency,
            node_ids=node_ids,
            node_types=node_types,
            edge_types_matrix=edge_types,
        )

    def _to_sequence(
        self, graph: nx.DiGraph, nodes: list[GraphNode]
    ) -> SequenceFormat:
        """Convert to sequence format using DFS traversal.

        Creates a linearized token sequence suitable for sequence models.
        """
        if not nodes:
            return SequenceFormat(tokens=[], node_sequence=[], traversal_type="DFS")

        # Find entry nodes (nodes with no predecessors)
        entry_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]

        if not entry_nodes:
            # If no entry nodes, start from first node
            entry_nodes = [nodes[0].id] if nodes else []

        # DFS traversal
        tokens: list[str] = []
        node_sequence: list[str] = []
        visited: set[str] = set()

        node_map = {node.id: node for node in nodes}

        for entry in entry_nodes:
            self._dfs_traverse(graph, entry, node_map, tokens, node_sequence, visited)

        return SequenceFormat(
            tokens=tokens,
            node_sequence=node_sequence,
            traversal_type="DFS",
        )

    def _dfs_traverse(
        self,
        graph: nx.DiGraph,
        node_id: str,
        node_map: dict[str, GraphNode],
        tokens: list[str],
        node_sequence: list[str],
        visited: set[str],
    ) -> None:
        """Perform DFS traversal and collect tokens."""
        if node_id in visited:
            return

        visited.add(node_id)
        node_sequence.append(node_id)

        # Get node info
        node = node_map.get(node_id)
        if node:
            # Add node type token
            tokens.append(f"[{node.type.value}]")

            # Add code tokens (simplified tokenization)
            code_tokens = self._tokenize_code(node.code)
            tokens.extend(code_tokens)

            # Add variable tokens
            for var in node.variables_defined:
                tokens.append(f"[DEF:{var}]")
            for var in node.variables_used:
                tokens.append(f"[USE:{var}]")

        # Traverse successors
        for successor in graph.successors(node_id):
            if successor not in visited:
                # Add edge token
                edge_data = graph.edges.get((node_id, successor), {})
                edge_type = edge_data.get("type", "SEQUENTIAL")
                tokens.append(f"[EDGE:{edge_type}]")

                self._dfs_traverse(graph, successor, node_map, tokens, node_sequence, visited)

    def _tokenize_code(self, code: str) -> list[str]:
        """Tokenize code snippet into tokens.

        Simple tokenization for transformer input.
        """
        if not code:
            return []

        # Clean and split code
        code = code.strip()

        # Simple tokenization: split on whitespace and special characters
        tokens: list[str] = []
        current = ""

        special_chars = set("(){}[];,.<>=+-*/%&|!?:")

        for char in code:
            if char.isspace():
                if current:
                    tokens.append(current)
                    current = ""
            elif char in special_chars:
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(char)
            else:
                current += char

        if current:
            tokens.append(current)

        # Limit tokens for very long code
        max_tokens = 50
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens] + ["..."]

        return tokens

    def to_transformer_input(
        self,
        graph_output: GraphOutput,
        format_type: str = "edge_list",
    ) -> dict[str, Any]:
        """Convert graph output to a specific transformer-ready format.

        Args:
            graph_output: GraphOutput object.
            format_type: One of "edge_list", "adjacency_matrix", "sequence", or "all".

        Returns:
            Dictionary with transformer-ready data.
        """
        if format_type == "edge_list":
            return self._edge_list_to_transformer(graph_output.edge_list)
        elif format_type == "adjacency_matrix":
            return self._adjacency_to_transformer(graph_output.adjacency_matrix)
        elif format_type == "sequence":
            return self._sequence_to_transformer(graph_output.sequence)
        else:  # "all"
            return {
                "edge_list": self._edge_list_to_transformer(graph_output.edge_list),
                "adjacency_matrix": self._adjacency_to_transformer(graph_output.adjacency_matrix),
                "sequence": self._sequence_to_transformer(graph_output.sequence),
            }

    def _edge_list_to_transformer(self, edge_list: EdgeListFormat) -> dict[str, Any]:
        """Convert edge list format to transformer input.

        Produces format compatible with PyTorch Geometric and similar libraries.
        """
        # Node features
        node_features = []
        node_type_vocab: dict[str, int] = {}

        for node in edge_list.nodes:
            # Build vocabulary
            if node.type.value not in node_type_vocab:
                node_type_vocab[node.type.value] = len(node_type_vocab)

            node_features.append({
                "id": node.id,
                "type_id": node_type_vocab[node.type.value],
                "type": node.type.value,
                "code": node.code,
                "line": node.line_number,
                "vars_defined": node.variables_defined,
                "vars_used": node.variables_used,
            })

        # Edge index (COO format for PyTorch Geometric)
        node_id_to_idx = {node.id: idx for idx, node in enumerate(edge_list.nodes)}
        edge_index = [[], []]  # [source_indices, target_indices]
        edge_types = []
        edge_type_vocab: dict[str, int] = {}

        for edge in edge_list.edges:
            if edge.source in node_id_to_idx and edge.target in node_id_to_idx:
                edge_index[0].append(node_id_to_idx[edge.source])
                edge_index[1].append(node_id_to_idx[edge.target])

                if edge.type.value not in edge_type_vocab:
                    edge_type_vocab[edge.type.value] = len(edge_type_vocab)
                edge_types.append(edge_type_vocab[edge.type.value])

        return {
            "num_nodes": len(edge_list.nodes),
            "num_edges": len(edge_list.edges),
            "node_features": node_features,
            "edge_index": edge_index,
            "edge_types": edge_types,
            "node_type_vocab": node_type_vocab,
            "edge_type_vocab": edge_type_vocab,
        }

    def _adjacency_to_transformer(self, adj: AdjacencyMatrixFormat) -> dict[str, Any]:
        """Convert adjacency matrix format to transformer input."""
        # Create type ID mappings
        type_vocab: dict[str, int] = {}
        type_ids = []

        for t in adj.node_types:
            if t not in type_vocab:
                type_vocab[t] = len(type_vocab)
            type_ids.append(type_vocab[t])

        return {
            "adjacency_matrix": adj.matrix,
            "node_ids": adj.node_ids,
            "node_type_ids": type_ids,
            "node_type_vocab": type_vocab,
            "edge_types_matrix": adj.edge_types_matrix,
            "num_nodes": len(adj.node_ids),
        }

    def _sequence_to_transformer(self, seq: SequenceFormat) -> dict[str, Any]:
        """Convert sequence format to transformer input.

        Produces tokenized sequence with vocabulary mapping.
        """
        # Build vocabulary
        vocab: dict[str, int] = {"[PAD]": 0, "[UNK]": 1, "[CLS]": 2, "[SEP]": 3}

        for token in seq.tokens:
            if token not in vocab:
                vocab[token] = len(vocab)

        # Convert to IDs
        token_ids = [vocab.get(t, vocab["[UNK]"]) for t in seq.tokens]

        return {
            "tokens": seq.tokens,
            "token_ids": token_ids,
            "node_sequence": seq.node_sequence,
            "vocab": vocab,
            "vocab_size": len(vocab),
            "sequence_length": len(seq.tokens),
            "traversal_type": seq.traversal_type,
        }

    def to_sparse_format(
        self, graph_output: GraphOutput
    ) -> dict[str, Any]:
        """Convert to sparse format for large graphs.

        Uses COO (Coordinate) format for efficient storage.
        """
        edge_list = graph_output.edge_list
        node_id_to_idx = {node.id: idx for idx, node in enumerate(edge_list.nodes)}

        # COO format: (row, col, data)
        rows = []
        cols = []
        edge_data = []

        for edge in edge_list.edges:
            if edge.source in node_id_to_idx and edge.target in node_id_to_idx:
                rows.append(node_id_to_idx[edge.source])
                cols.append(node_id_to_idx[edge.target])
                edge_data.append(edge.type.value)

        return {
            "format": "COO",
            "shape": [len(edge_list.nodes), len(edge_list.nodes)],
            "row": rows,
            "col": cols,
            "edge_types": edge_data,
            "nnz": len(rows),  # Number of non-zero elements
        }

    def to_dgl_format(self, graph_output: GraphOutput) -> dict[str, Any]:
        """Convert to DGL (Deep Graph Library) compatible format."""
        edge_list = graph_output.edge_list
        node_id_to_idx = {node.id: idx for idx, node in enumerate(edge_list.nodes)}

        src_nodes = []
        dst_nodes = []

        for edge in edge_list.edges:
            if edge.source in node_id_to_idx and edge.target in node_id_to_idx:
                src_nodes.append(node_id_to_idx[edge.source])
                dst_nodes.append(node_id_to_idx[edge.target])

        # Node features as list of dicts
        node_data = {
            "type": [n.type.value for n in edge_list.nodes],
            "code": [n.code for n in edge_list.nodes],
            "line": [n.line_number for n in edge_list.nodes],
        }

        return {
            "num_nodes": len(edge_list.nodes),
            "src": src_nodes,
            "dst": dst_nodes,
            "node_data": node_data,
        }
