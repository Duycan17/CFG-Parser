# cURL Examples for Java CFG/DDG Parser API

## Prerequisites
Make sure the server is running on `http://localhost:8000`

## 1. Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{"status":"healthy","version":"1.0.0"}
```

## 2. Analyze Simple Java Code

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true,
    "include_class_graph": false
  }'
```

## 3. Analyze Complex Java Code (with loops and conditionals)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Calculator { public int factorial(int n) { if (n <= 1) { return 1; } int fact = 1; for (int i = 2; i <= n; i++) { fact = fact * i; } return fact; } }",
    "include_method_graphs": true,
    "include_class_graph": true
  }'
```

## 4. Analyze Java Code with Try-Catch

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Divider { public int divide(int a, int b) { try { return a / b; } catch (ArithmeticException e) { return 0; } } }",
    "include_method_graphs": true,
    "include_class_graph": false
  }'
```

## 5. Analyze Java File Upload

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/file" \
  -F "file=@test_example.java" \
  -F "include_class_graph=true" \
  -F "include_method_graphs=true"
```

**Note:** Make sure `test_example.java` exists in the current directory.

## 6. Pretty Print JSON Response (using jq)

If you have `jq` installed:

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true
  }' | jq .
```

## 7. Save Response to File

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true
  }' -o response.json
```

## 8. Test Invalid Code (should return error)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "this is not valid java code {"
  }'
```

**Expected Response:** HTTP 422 with error details

## 9. Get Only CFG Edge List

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true
  }' | jq '.method_graphs[0].cfg.edge_list'
```

## 10. Get Only DDG Nodes

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public int add(int a, int b) { return a + b; } }",
    "include_method_graphs": true
  }' | jq '.method_graphs[0].ddg.edge_list.nodes'
```

## Windows PowerShell Alternative

On Windows, you can use PowerShell's `Invoke-RestMethod`:

```powershell
$body = @{
    code = "public class Test { public int add(int a, int b) { return a + b; } }"
    include_method_graphs = $true
    include_class_graph = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10
```

## Response Structure

The API returns:
- `success`: boolean
- `class_name`: string
- `method_count`: integer
- `method_graphs`: array of method graphs, each containing:
  - `method_name`: string
  - `parameters`: array
  - `return_type`: string
  - `cfg`: Control Flow Graph with:
    - `edge_list`: nodes and edges
    - `adjacency_matrix`: matrix representation
    - `sequence`: token sequence
  - `ddg`: Data Dependence Graph (same structure as CFG)
- `class_graph`: optional class-level graph
- `errors`: array of error messages
- `warnings`: array of warning messages
