# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

### 3. Make Sure Backend is Running
The backend should be running on: **http://localhost:8000**

```bash
# In another terminal
cd ..
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## Features

### Code Editor
- Syntax highlighting for Java code
- Preview mode to see formatted code
- Load example code button
- Real-time editing

### Graph Visualization
- **Control Flow Graph (CFG)**: Shows program flow with nodes and edges
- **Data Dependence Graph (DDG)**: Shows variable dependencies
- Interactive graphs with zoom, pan, and minimap
- Color-coded nodes by type:
  - Green: Entry points
  - Red: Exit points
  - Blue: Method entry/exit
  - Purple: Conditions
  - Pink: Loops
  - And more...

### Method Navigation
- Switch between multiple methods in a class
- View CFG and DDG for each method separately
- See method metadata (parameters, return type, etc.)

## Usage

1. **Enter Java Code**: Type or paste Java code in the left panel
2. **Click "Analyze Code"**: The code will be sent to the backend API
3. **View Results**: 
   - See the graph visualization in the right panel
   - Switch between CFG and DDG tabs
   - Navigate between methods if multiple exist

## Example Code

Try this example:

```java
public class Calculator {
    public int add(int a, int b) {
        int result = a + b;
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
}
```

## Troubleshooting

### CORS Errors
- Make sure the backend CORS middleware is enabled (already configured)
- Check that backend is running on port 8000

### Graph Not Displaying
- Check browser console for errors
- Verify the API response contains graph data
- Make sure React Flow styles are loaded

### API Connection Issues
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check the API URL in `src/api/client.ts`
- Look at browser Network tab for failed requests

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Technologies Used

- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Styling
- **React Flow**: Graph visualization
- **Axios**: HTTP client
- **React Syntax Highlighter**: Code syntax highlighting
