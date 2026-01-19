# Debug Steps for Blank Page Issue

## Quick Checks

1. **Open Browser Console (F12)**
   - Look for red error messages
   - Check the Console tab
   - Check the Network tab for failed requests

2. **Verify Dev Server is Running**
   ```bash
   cd frontend
   npm run dev
   ```
   Should show: `Local: http://localhost:3000/`

3. **Check if React is Loading**
   - Right-click on the page → "Inspect"
   - Look at the Elements tab
   - Check if there's a `<div id="root">` element
   - Check if anything is inside it

4. **Common Errors to Look For:**
   - `Cannot find module` - Missing dependency
   - `React is not defined` - Import issue
   - `Unexpected token` - Syntax error
   - CORS errors - Backend not running or CORS not configured

## Test with Minimal App

If the page is still blank, temporarily replace `src/App.tsx` with:

```tsx
function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test - React Works!</h1>
    </div>
  );
}

export default App;
```

If this shows up, the issue is in the component code.

## Check These Files

1. `src/main.tsx` - Entry point
2. `index.html` - HTML template
3. `src/App.tsx` - Main component
4. Browser console for errors

## Next Steps

Share the browser console errors and I can help fix them!
