"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.java_parser import JavaParser
from app.services.cfg_builder import CFGBuilder
from app.services.ddg_builder import DDGBuilder
from app.services.graph_converter import GraphConverter


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def java_parser() -> JavaParser:
    """Create Java parser instance."""
    return JavaParser()


@pytest.fixture
def cfg_builder() -> CFGBuilder:
    """Create CFG builder instance."""
    return CFGBuilder()


@pytest.fixture
def ddg_builder() -> DDGBuilder:
    """Create DDG builder instance."""
    return DDGBuilder()


@pytest.fixture
def graph_converter() -> GraphConverter:
    """Create graph converter instance."""
    return GraphConverter()


@pytest.fixture
def sample_java_code() -> str:
    """Sample Java code for testing."""
    return '''
public class Calculator {
    private int result;

    public int add(int a, int b) {
        result = a + b;
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
'''


@pytest.fixture
def simple_java_method() -> str:
    """Simple Java class with one method."""
    return '''
public class Simple {
    public int sum(int x, int y) {
        int result = x + y;
        return result;
    }
}
'''


@pytest.fixture
def loop_java_code() -> str:
    """Java code with loop structures."""
    return '''
public class LoopExample {
    public int sumArray(int[] arr) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum = sum + arr[i];
        }
        return sum;
    }

    public int whileExample(int n) {
        int count = 0;
        while (n > 0) {
            count++;
            n--;
        }
        return count;
    }
}
'''


@pytest.fixture
def conditional_java_code() -> str:
    """Java code with conditional structures."""
    return '''
public class ConditionalExample {
    public String classify(int score) {
        String grade;
        if (score >= 90) {
            grade = "A";
        } else if (score >= 80) {
            grade = "B";
        } else if (score >= 70) {
            grade = "C";
        } else {
            grade = "F";
        }
        return grade;
    }

    public int abs(int x) {
        if (x < 0) {
            return -x;
        }
        return x;
    }
}
'''
