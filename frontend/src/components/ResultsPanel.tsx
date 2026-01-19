import { useState } from 'react';
import GraphVisualization from './GraphVisualization';
import type { AnalyzeResponse } from '../api/client';

interface ResultsPanelProps {
  results: AnalyzeResponse | null;
  isLoading: boolean;
  error: string | null;
}

export default function ResultsPanel({ results, isLoading, error }: ResultsPanelProps) {
  const [selectedMethod, setSelectedMethod] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'cfg' | 'ddg'>('cfg');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg border border-gray-300">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Analyzing Java code...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg border border-gray-300">
        <p className="text-gray-500">Enter Java code and click "Analyze Code" to see results</p>
      </div>
    );
  }

  if (!results.success) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">Analysis Issues</h3>
        {results.errors.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-yellow-700 mb-2">Errors:</h4>
            <ul className="list-disc list-inside text-yellow-600">
              {results.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          </div>
        )}
        {results.warnings.length > 0 && (
          <div>
            <h4 className="font-semibold text-yellow-700 mb-2">Warnings:</h4>
            <ul className="list-disc list-inside text-yellow-600">
              {results.warnings.map((warn, idx) => (
                <li key={idx}>{warn}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  const currentMethod = results.method_graphs[selectedMethod];
  const currentGraph = activeTab === 'cfg' ? currentMethod?.cfg : currentMethod?.ddg;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-300 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-300">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-gray-800">
            Analysis Results: {results.class_name}
          </h2>
          <span className="text-sm text-gray-600">
            {results.method_count} method{results.method_count !== 1 ? 's' : ''} found
          </span>
        </div>

        {/* Method selector */}
        {results.method_graphs.length > 1 && (
          <div className="flex gap-2 mt-2">
            {results.method_graphs.map((method, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedMethod(idx)}
                className={`px-3 py-1 text-sm rounded transition-colors ${selectedMethod === idx
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
              >
                {method.method_name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Method info */}
      {currentMethod && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-300">
          <div className="flex items-center gap-4 text-sm">
            <div>
              <span className="font-semibold text-gray-700">Method:</span>
              <span className="ml-2 text-gray-600">{currentMethod.method_name}</span>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Return:</span>
              <span className="ml-2 text-gray-600">{currentMethod.return_type}</span>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Parameters:</span>
              <span className="ml-2 text-gray-600">
                {currentMethod.parameters.join(', ') || 'none'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Graph tabs */}
      {currentMethod && (
        <div className="flex border-b border-gray-300 bg-gray-50">
          <button
            onClick={() => setActiveTab('cfg')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'cfg'
                ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
              }`}
          >
            Control Flow Graph (CFG)
          </button>
          <button
            onClick={() => setActiveTab('ddg')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'ddg'
                ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
              }`}
          >
            Data Dependence Graph (DDG)
          </button>
        </div>
      )}

      {/* Graph visualization */}
      <div className="flex-1 overflow-hidden">
        {currentGraph ? (
          <GraphVisualization
            nodes={currentGraph.edge_list.nodes}
            edges={currentGraph.edge_list.edges}
            title={`${activeTab.toUpperCase()}: ${currentMethod?.method_name || 'Graph'}`}
            height="100%"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">No graph data available</p>
          </div>
        )}
      </div>
    </div>
  );
}
