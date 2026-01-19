import { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import ResultsPanel from './components/ResultsPanel';
import { analyzeCode } from './api/client';
import type { AnalyzeResponse } from './api/client';

function App() {
  const [code, setCode] = useState('');
  const [results, setResults] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some Java code');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await analyzeCode({
        code: code.trim(),
        include_method_graphs: true,
        include_class_graph: false,
      });
      setResults(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to analyze code';
      setError(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Java CFG/DDG Parser
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Generate Control Flow Graphs and Data Dependence Graphs from Java source code
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" style={{ minHeight: 'calc(100vh - 200px)' }}>
          {/* Left panel - Code Editor */}
          <div className="flex flex-col">
            <CodeEditor
              code={code}
              onChange={setCode}
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
            />
          </div>

          {/* Right panel - Results */}
          <div className="flex flex-col">
            <ResultsPanel
              results={results}
              isLoading={isLoading}
              error={error}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <p className="text-sm text-gray-600 text-center">
            Java CFG/DDG Parser - Powered by FastAPI & React
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
