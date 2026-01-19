import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalyzeRequest {
  code: string;
  include_method_graphs?: boolean;
  include_class_graph?: boolean;
}

export interface GraphNode {
  id: string;
  type: string;
  code: string;
  line_number: number | null;
  column: number | null;
  variables_defined: string[];
  variables_used: string[];
  metadata: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  label: string;
  variable: string | null;
  metadata: Record<string, any>;
}

export interface EdgeListFormat {
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}

export interface GraphOutput {
  edge_list: EdgeListFormat;
  adjacency_matrix: {
    matrix: number[][];
    node_ids: string[];
    node_types: string[];
    edge_types_matrix: (string | null)[][];
  };
  sequence: {
    tokens: string[];
    node_sequence: string[];
    traversal_type: string;
  };
}

export interface MethodGraph {
  method_name: string;
  class_name: string;
  parameters: string[];
  return_type: string;
  line_start: number | null;
  line_end: number | null;
  cfg: GraphOutput;
  ddg: GraphOutput;
}

export interface AnalyzeResponse {
  success: boolean;
  source_file: string | null;
  class_name: string;
  method_count: number;
  method_graphs: MethodGraph[];
  class_graph: {
    class_name: string;
    cfg: GraphOutput;
    ddg: GraphOutput;
  } | null;
  errors: string[];
  warnings: string[];
}

export const analyzeCode = async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
  const response = await apiClient.post<AnalyzeResponse>('/analyze', request);
  return response.data;
};

export const analyzeFile = async (file: File, includeClassGraph = true, includeMethodGraphs = true): Promise<AnalyzeResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('include_class_graph', includeClassGraph.toString());
  formData.append('include_method_graphs', includeMethodGraphs.toString());
  
  const response = await apiClient.post<AnalyzeResponse>('/analyze/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
