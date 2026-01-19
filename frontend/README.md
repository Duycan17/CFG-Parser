# Java CFG/DDG Parser - Frontend

React frontend for visualizing Java Control Flow Graphs (CFG) and Data Dependence Graphs (DDG).

## Features

- **Code Editor**: Input Java code with syntax highlighting
- **Graph Visualization**: Interactive CFG and DDG diagrams using React Flow
- **Method Navigation**: Switch between multiple methods in a class
- **Real-time Analysis**: Connect to FastAPI backend for code analysis

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Configuration

Create a `.env` file (optional):
```
VITE_API_URL=http://localhost:8000/api/v1
```

## Build

```bash
npm run build
```

## Technologies

- React 19
- TypeScript
- Vite
- Tailwind CSS
- React Flow (graph visualization)
- Axios (API client)
- React Syntax Highlighter
