"""Graph node and edge models for CFG and DDG representation."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of nodes in the control flow graph."""

    ENTRY = "ENTRY"
    EXIT = "EXIT"
    STATEMENT = "STATEMENT"
    CONDITION = "CONDITION"
    LOOP_HEADER = "LOOP_HEADER"
    SWITCH = "SWITCH"
    CASE = "CASE"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    ASSIGNMENT = "ASSIGNMENT"
    DECLARATION = "DECLARATION"
    METHOD_CALL = "METHOD_CALL"
    METHOD_ENTRY = "METHOD_ENTRY"
    METHOD_EXIT = "METHOD_EXIT"


class EdgeType(str, Enum):
    """Types of edges in graphs."""

    # CFG edge types
    SEQUENTIAL = "SEQUENTIAL"
    TRUE_BRANCH = "TRUE_BRANCH"
    FALSE_BRANCH = "FALSE_BRANCH"
    LOOP_BACK = "LOOP_BACK"
    LOOP_EXIT = "LOOP_EXIT"
    CASE_BRANCH = "CASE_BRANCH"
    DEFAULT_BRANCH = "DEFAULT_BRANCH"
    EXCEPTION = "EXCEPTION"
    FINALLY_EDGE = "FINALLY_EDGE"
    CALL = "CALL"
    RETURN_EDGE = "RETURN_EDGE"

    # DDG edge types
    DATA_DEP = "DATA_DEP"
    DEF_USE = "DEF_USE"
    USE_DEF = "USE_DEF"
    PARAM_IN = "PARAM_IN"
    PARAM_OUT = "PARAM_OUT"


class GraphNode(BaseModel):
    """Represents a node in the graph."""

    id: str = Field(..., description="Unique node identifier")
    type: NodeType = Field(..., description="Type of the node")
    code: str = Field(default="", description="Code snippet for this node")
    line_number: int | None = Field(default=None, description="Source line number")
    column: int | None = Field(default=None, description="Source column number")
    variables_defined: list[str] = Field(default_factory=list, description="Variables defined at this node")
    variables_used: list[str] = Field(default_factory=list, description="Variables used at this node")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GraphEdge(BaseModel):
    """Represents an edge in the graph."""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Type of the edge")
    label: str = Field(default="", description="Edge label")
    variable: str | None = Field(default=None, description="Variable associated with this edge (for DDG)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EdgeListFormat(BaseModel):
    """Edge list representation for transformer input."""

    nodes: list[GraphNode] = Field(default_factory=list, description="List of graph nodes")
    edges: list[GraphEdge] = Field(default_factory=list, description="List of graph edges")
    node_count: int = Field(default=0, description="Total number of nodes")
    edge_count: int = Field(default=0, description="Total number of edges")


class AdjacencyMatrixFormat(BaseModel):
    """Adjacency matrix representation for transformer input."""

    matrix: list[list[int]] = Field(default_factory=list, description="Adjacency matrix")
    node_ids: list[str] = Field(default_factory=list, description="Node IDs in matrix order")
    node_types: list[str] = Field(default_factory=list, description="Node types in matrix order")
    edge_types_matrix: list[list[str | None]] = Field(
        default_factory=list, description="Edge types matrix"
    )


class SequenceFormat(BaseModel):
    """Sequence representation for transformer input."""

    tokens: list[str] = Field(default_factory=list, description="Linearized graph tokens")
    node_sequence: list[str] = Field(default_factory=list, description="Node IDs in traversal order")
    traversal_type: str = Field(default="DFS", description="Type of traversal (DFS/BFS)")


class GraphOutput(BaseModel):
    """Complete graph output in all formats."""

    edge_list: EdgeListFormat = Field(default_factory=EdgeListFormat)
    adjacency_matrix: AdjacencyMatrixFormat = Field(default_factory=AdjacencyMatrixFormat)
    sequence: SequenceFormat = Field(default_factory=SequenceFormat)
