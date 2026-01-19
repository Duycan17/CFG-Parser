#!/bin/bash
# Curl test commands for Java CFG/DDG Parser API

BASE_URL="http://localhost:8000/api/v1"

echo "=========================================="
echo "1. Health Check"
echo "=========================================="
curl -X GET "${BASE_URL}/health" \
  -H "Content-Type: application/json" \
  -w "\nStatus: %{http_code}\n\n"

echo "=========================================="
echo "2. Analyze Simple Java Code"
echo "=========================================="
curl -X POST "${BASE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true,
    "include_class_graph": false
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "=========================================="
echo "3. Analyze Complex Java Code with CFG and DDG"
echo "=========================================="
curl -X POST "${BASE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Calculator { public int factorial(int n) { if (n <= 1) { return 1; } int fact = 1; for (int i = 2; i <= n; i++) { fact = fact * i; } return fact; } }",
    "include_method_graphs": true,
    "include_class_graph": true
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo "=========================================="
echo "4. Analyze Java File Upload"
echo "=========================================="
curl -X POST "${BASE_URL}/analyze/file" \
  -F "file=@test_example.java" \
  -F "include_class_graph=true" \
  -F "include_method_graphs=true" \
  -w "\nStatus: %{http_code}\n\n"

echo "=========================================="
echo "5. Test Invalid Code (should fail)"
echo "=========================================="
curl -X POST "${BASE_URL}/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "this is not valid java code {"
  }' \
  -w "\nStatus: %{http_code}\n\n"
