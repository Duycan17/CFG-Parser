# Java CFG/DDG Parser - Complete Project Summary

## Project Structure

```
CFG-Parser/
├── app/                    # FastAPI Backend
│   ├── api/               # API routes
│   ├── core/              # Configuration & exceptions
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic (parser, CFG, DDG builders)
│   └── utils/             # Utilities
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/    # React components
│   │   └── App.tsx       # Main app
│   └── package.json
├── tests/                  # Unit tests
├── requirements.txt       # Python dependencies
└── README.md
```

## Features

### Backend (FastAPI)
- ✅ Java code parsing using `javalang`
- ✅ Control Flow Graph (CFG) generation
- ✅ Data Dependence Graph (DDG) generation
- ✅ Multiple output formats (edge list, adjacency matrix, sequence)
- ✅ Method-level and class-level analysis
- ✅ RESTful API with OpenAPI docs
- ✅ File upload support

### Frontend (React)
- ✅ Modern, responsive UI with Tailwind CSS
- ✅ Code editor with syntax highlighting
- ✅ Interactive graph visualization with React Flow
- ✅ CFG and DDG diagram display
- ✅ Method navigation
- ✅ Real-time code analysis

## Quick Start

### 1. Backend Setup

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload
```

Backend runs on: **http://localhost:8000**
- API Docs: http://localhost:8000/api/v1/docs

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: **http://localhost:3000**

## API Endpoints

### POST `/api/v1/analyze`
Analyze Java code string

**Request:**
```json
{
  "code": "public class Test { public int add(int a, int b) { return a + b; } }",
  "include_method_graphs": true,
  "include_class_graph": false
}
```

### POST `/api/v1/analyze/file`
Upload and analyze Java file

### GET `/api/v1/health`
Health check endpoint

## Testing

### Backend Tests
```bash
pytest tests/ -v
```

### Frontend Manual Test
1. Open http://localhost:3000
2. Enter Java code
3. Click "Analyze Code"
4. View graphs

### API Test (cURL)
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"code": "public class Test { public int add(int a, int b) { return a + b; } }"}'
```

## Graph Visualization

### Node Types
- **ENTRY/EXIT**: Graph entry/exit points
- **METHOD_ENTRY/EXIT**: Method boundaries
- **CONDITION**: If/else conditions
- **LOOP_HEADER**: Loop conditions
- **STATEMENT**: General statements
- **RETURN/THROW**: Control flow exits
- And more...

### Edge Types
- **SEQUENTIAL**: Normal flow
- **TRUE_BRANCH/FALSE_BRANCH**: Conditional branches
- **LOOP_BACK**: Loop iterations
- **DATA_DEP**: Data dependencies
- **DEF_USE**: Definition to use chains

## Output Formats

1. **Edge List**: Nodes and edges as JSON arrays (PyTorch Geometric compatible)
2. **Adjacency Matrix**: Dense matrix representation
3. **Sequence**: DFS traversal tokens for sequence models

## Technologies

### Backend
- FastAPI
- javalang (Java AST parser)
- NetworkX (graph operations)
- Pydantic (data validation)
- Uvicorn (ASGI server)

### Frontend
- React 19
- TypeScript
- Vite
- Tailwind CSS
- React Flow (graph visualization)
- Axios (HTTP client)

## Production Deployment

### Backend
```bash
# Using Docker
docker build -t cfg-parser .
docker run -p 8000:8000 cfg-parser

# Or with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ directory with nginx or similar
```

## Next Steps

- [ ] Add file upload UI in frontend
- [ ] Add graph export (PNG/SVG)
- [ ] Add graph statistics panel
- [ ] Add code examples library
- [ ] Add dark mode toggle
- [ ] Add graph layout algorithms (hierarchical, force-directed)
- [ ] Add node/edge details on hover
- [ ] Add sequence view visualization
