# Testing Guide for Java CFG/DDG Parser

## Quick Start

### 1. Start the Server

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload
```

### 2. Test Methods

#### Method 1: Interactive API Docs (Easiest)
1. Open browser: http://localhost:8000/api/v1/docs
2. Click on `POST /api/v1/analyze`
3. Click "Try it out"
4. Paste Java code in the request body
5. Click "Execute"

#### Method 2: Python Test Script
```powershell
python quick_test.py
```

#### Method 3: PowerShell/HTTP Request
```powershell
$code = @"
public class Test {
    public int add(int a, int b) {
        return a + b;
    }
}
"@

$body = @{
    code = $code
    include_method_graphs = $true
    include_class_graph = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

#### Method 4: File Upload Test
```powershell
$file = Get-Item "test_example.java"
$form = @{
    file = $file
    include_class_graph = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze/file" `
    -Method POST `
    -ContentType "multipart/form-data" `
    -Body $form
```

#### Method 5: Run Unit Tests
```powershell
# Test parser only
pytest tests/test_parser.py -v

# Test CFG builder
pytest tests/test_cfg.py -v

# Test DDG builder
pytest tests/test_ddg.py -v

# Test API endpoints
pytest tests/test_api.py -v

# Run all tests
pytest -v
```

## Example Test Cases

### Simple Method
```java
public class Simple {
    public int sum(int x, int y) {
        int result = x + y;
        return result;
    }
}
```

### Method with Control Flow
```java
public class Conditional {
    public int max(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }
}
```

### Method with Loop
```java
public class Loop {
    public int sumArray(int[] arr) {
        int sum = 0;
        for (int i = 0; i < arr.length; i++) {
            sum = sum + arr[i];
        }
        return sum;
    }
}
```

### Method with Try-Catch
```java
public class Exception {
    public int divide(int a, int b) {
        try {
            return a / b;
        } catch (ArithmeticException e) {
            return 0;
        }
    }
}
```

## Expected Output Format

The API returns:
- **CFG (Control Flow Graph)**: Edge list, adjacency matrix, and sequence format
- **DDG (Data Dependence Graph)**: Variable dependencies between statements
- **Node information**: Type, code snippet, line numbers, variables defined/used
- **Edge information**: Source, target, edge type, labels

## Troubleshooting

### Server not starting
- Check if port 8000 is available
- Verify virtual environment is activated
- Check for import errors: `python -c "import app.main"`

### 500 Internal Server Error
- Check server logs in terminal
- Verify all dependencies are installed: `uv pip list`
- Test parser directly: `python -c "from app.services.java_parser import JavaParser; p = JavaParser(); print(p.parse('public class T {}'))"`

### Parsing Errors
- Ensure Java code is valid
- Check for missing semicolons, braces
- Verify class and method declarations are correct

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/analyze` - Analyze Java code string
- `POST /api/v1/analyze/file` - Analyze uploaded Java file

## Output Formats

1. **Edge List**: Nodes and edges as lists (PyTorch Geometric compatible)
2. **Adjacency Matrix**: Dense matrix representation
3. **Sequence**: DFS traversal tokens for sequence models
