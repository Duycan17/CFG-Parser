import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

const DEFAULT_CODE = `public class Calculator {
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

    public int divide(int a, int b) {
        try {
            return a / b;
        } catch (ArithmeticException e) {
            return 0;
        }
    }
}`;

export default function CodeEditor({ code, onChange, onAnalyze, isLoading }: CodeEditorProps) {
  const [showPreview, setShowPreview] = useState(false);

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const loadExample = () => {
    onChange(DEFAULT_CODE);
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg overflow-hidden border border-gray-700">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-300">Java Code Editor</span>
          <button
            onClick={loadExample}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-200 rounded transition-colors"
          >
            Load Example
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-200 rounded transition-colors"
          >
            {showPreview ? 'Edit' : 'Preview'}
          </button>
          <button
            onClick={onAnalyze}
            disabled={isLoading || !code.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded font-medium transition-colors"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Code'}
          </button>
        </div>
      </div>
      
      <div className="flex-1 relative">
        {showPreview ? (
          <div className="h-full overflow-auto">
            <SyntaxHighlighter
              language="java"
              style={vscDarkPlus}
              customStyle={{ margin: 0, height: '100%' }}
            >
              {code || '// Enter your Java code here'}
            </SyntaxHighlighter>
          </div>
        ) : (
          <textarea
            value={code}
            onChange={handleCodeChange}
            placeholder="// Enter your Java code here..."
            className="w-full h-full p-4 bg-gray-900 text-gray-100 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            spellCheck={false}
          />
        )}
      </div>
    </div>
  );
}
