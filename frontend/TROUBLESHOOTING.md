# Troubleshooting Guide

## Issue: Blank page at localhost:3000

### Step 1: Check if dev server is running
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Step 2: Check browser console
1. Open http://localhost:3000
2. Press F12 to open Developer Tools
3. Check the Console tab for errors
4. Check the Network tab for failed requests

### Step 3: Common issues and fixes

#### Issue: "Cannot find module 'reactflow'"
**Fix:**
```bash
npm install reactflow
```

#### Issue: Tailwind CSS not working
**Fix:**
```bash
npm install tailwindcss@^3.4.0
```

#### Issue: CORS errors
**Fix:** Make sure backend is running on port 8000 and CORS is enabled

#### Issue: Blank white page
**Possible causes:**
1. JavaScript error - check browser console
2. React component error - check for import issues
3. CSS not loading - check if Tailwind is configured

### Step 4: Test with minimal app

Temporarily replace `src/App.tsx` with:

```tsx
function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test - React is working!</h1>
    </div>
  );
}

export default App;
```

If this works, the issue is in the component imports.

### Step 5: Check imports

Verify all imports in:
- `src/App.tsx`
- `src/components/CodeEditor.tsx`
- `src/components/GraphVisualization.tsx`
- `src/components/ResultsPanel.tsx`
- `src/api/client.ts`

### Step 6: Clear cache and reinstall

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```
