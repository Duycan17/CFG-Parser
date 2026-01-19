"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_analyze_simple_code(self, client: TestClient, simple_java_method: str):
        """Test analyzing simple Java code."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["class_name"] == "Simple"
        assert data["method_count"] == 1
        assert len(data["method_graphs"]) == 1

    def test_analyze_returns_cfg(self, client: TestClient, simple_java_method: str):
        """Test that analysis returns CFG."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        method_graph = data["method_graphs"][0]

        assert "cfg" in method_graph
        cfg = method_graph["cfg"]

        assert "edge_list" in cfg
        assert "adjacency_matrix" in cfg
        assert "sequence" in cfg

    def test_analyze_returns_ddg(self, client: TestClient, simple_java_method: str):
        """Test that analysis returns DDG."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        method_graph = data["method_graphs"][0]

        assert "ddg" in method_graph
        ddg = method_graph["ddg"]

        assert "edge_list" in ddg
        assert "adjacency_matrix" in ddg
        assert "sequence" in ddg

    def test_analyze_class_graph(self, client: TestClient, sample_java_code: str):
        """Test that analysis returns class-level graph."""
        response = client.post(
            "/api/v1/analyze",
            json={
                "code": sample_java_code,
                "include_class_graph": True,
            },
        )

        data = response.json()
        assert data["class_graph"] is not None
        assert "cfg" in data["class_graph"]
        assert "ddg" in data["class_graph"]

    def test_analyze_exclude_class_graph(self, client: TestClient, simple_java_method: str):
        """Test excluding class-level graph."""
        response = client.post(
            "/api/v1/analyze",
            json={
                "code": simple_java_method,
                "include_class_graph": False,
            },
        )

        data = response.json()
        assert data["class_graph"] is None

    def test_analyze_exclude_method_graphs(self, client: TestClient, simple_java_method: str):
        """Test excluding method-level graphs."""
        response = client.post(
            "/api/v1/analyze",
            json={
                "code": simple_java_method,
                "include_method_graphs": False,
                "include_class_graph": True,
            },
        )

        data = response.json()
        assert len(data["method_graphs"]) == 0

    def test_analyze_invalid_code(self, client: TestClient):
        """Test analyzing invalid Java code."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": "not valid java {"},
        )

        assert response.status_code == 422

    def test_analyze_empty_code(self, client: TestClient):
        """Test analyzing empty code."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": ""},
        )

        assert response.status_code == 422  # Validation error

    def test_edge_list_format(self, client: TestClient, simple_java_method: str):
        """Test edge list format structure."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        cfg = data["method_graphs"][0]["cfg"]
        edge_list = cfg["edge_list"]

        assert "nodes" in edge_list
        assert "edges" in edge_list
        assert "node_count" in edge_list
        assert "edge_count" in edge_list

        # Check node structure
        if edge_list["nodes"]:
            node = edge_list["nodes"][0]
            assert "id" in node
            assert "type" in node
            assert "code" in node

    def test_adjacency_matrix_format(self, client: TestClient, simple_java_method: str):
        """Test adjacency matrix format structure."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        cfg = data["method_graphs"][0]["cfg"]
        adj = cfg["adjacency_matrix"]

        assert "matrix" in adj
        assert "node_ids" in adj
        assert "node_types" in adj

    def test_sequence_format(self, client: TestClient, simple_java_method: str):
        """Test sequence format structure."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        cfg = data["method_graphs"][0]["cfg"]
        seq = cfg["sequence"]

        assert "tokens" in seq
        assert "node_sequence" in seq
        assert "traversal_type" in seq

    def test_method_graph_metadata(self, client: TestClient, simple_java_method: str):
        """Test method graph contains metadata."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": simple_java_method},
        )

        data = response.json()
        method = data["method_graphs"][0]

        assert method["method_name"] == "sum"
        assert method["class_name"] == "Simple"
        assert method["parameters"] == ["x", "y"]
        assert method["return_type"] == "int"

    def test_analyze_complex_code(self, client: TestClient, sample_java_code: str):
        """Test analyzing complex code with multiple methods."""
        response = client.post(
            "/api/v1/analyze",
            json={"code": sample_java_code},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["method_count"] == 3
        method_names = [m["method_name"] for m in data["method_graphs"]]
        assert "add" in method_names
        assert "factorial" in method_names
        assert "divide" in method_names
