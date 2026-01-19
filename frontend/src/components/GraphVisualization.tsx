import { useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import type { Node, Edge } from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import type { GraphNode, GraphEdge } from '../api/client';

interface GraphVisualizationProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  title: string;
  height?: string;
}

// Helper to check if a string is roughly an identifier (like b1, n0)
const isIdentifier = (str: string) => /^[a-zA-Z][a-zA-Z0-9]*$/.test(str);

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 50, height: 50 }); // Assume fixed circle size
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    // Center the node
    node.position = {
      x: nodeWithPosition.x - 25,
      y: nodeWithPosition.y - 25,
    };
    return node;
  });

  return { nodes: layoutedNodes, edges };
};

export default function GraphVisualization({
  nodes: rawNodes,
  edges: rawEdges,
  title,
  height = '600px',
}: GraphVisualizationProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!rawNodes.length) {
      setNodes([]);
      setEdges([]);
      return;
    }

    // Transform to ReactFlow nodes with "Academic" styling
    const initialFlowNodes: Node[] = rawNodes.map((node) => {
      // Logic to determine label. If code is short (like b1, n0), use it. 
      // Otherwise use ID or type abbr to keep it small and circular.
      let label = node.id;
      // Heuristic: short code snippets or identifiers might be good labels. 
      // If code is too long, stick to ID.
      if (node.code && node.code.length < 5 && isIdentifier(node.code)) {
        label = node.code;
      } else {
        // Fallback for academic look: b + index or n + index usually
        // We will just use the ID if we can't find a better short one.
        // For Method Entry/Exit, maybe use "Start"/"End"
        if (node.type === 'METHOD_ENTRY' || node.type === 'ENTRY') label = 'Start';
        if (node.type === 'METHOD_EXIT' || node.type === 'EXIT') label = 'End';
      }

      return {
        id: node.id,
        type: 'default',
        position: { x: 0, y: 0 }, // will be set by layout
        data: { label },
        style: {
          background: '#ffffff',
          color: '#000000',
          border: '1px solid #000000',
          borderRadius: '50%',
          width: 50,
          height: 50,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '12px',
          fontWeight: 'normal',
        },
      };
    });

    const initialFlowEdges: Edge[] = rawEdges.map((edge) => {
      let label = '';
      if (edge.type === 'TRUE_BRANCH') label = 'T';
      if (edge.type === 'FALSE_BRANCH') label = 'F';

      return {
        id: `${edge.source}-${edge.target}-${edge.type}`, // Make unqiue
        source: edge.source,
        target: edge.target,
        label: label,
        type: 'straight', // Straight edges look more academic/formal often, or 'smoothstep'
        style: {
          stroke: '#000000',
          strokeWidth: 1,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#000000',
          width: 20,
          height: 20,
        },
        labelStyle: {
          fill: '#000000',
          fontWeight: 400,
          fontSize: '12px',
        },
      };
    });

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      initialFlowNodes,
      initialFlowEdges
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [rawNodes, rawEdges, setNodes, setEdges]); // Rerun when data changes

  if (rawNodes.length === 0) {
    return (
      <div className="border border-gray-300 rounded-lg p-8 text-center bg-gray-50" style={{ height }}>
        <p className="text-gray-500">No graph data to display</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col border border-gray-300 rounded-lg overflow-hidden bg-white" style={{ height }}>
      <div className="px-4 py-2 bg-gray-100 border-b border-gray-300">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
        <p className="text-xs text-gray-500 mt-1">
          Academic Style: {nodes.length} nodes, {edges.length} edges
        </p>
      </div>
      <div className="flex-1" style={{ position: 'relative', minHeight: '400px' }}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            fitViewOptions={{ padding: 0.2 }}
          >
            <Background color="#f0f0f0" gap={16} />
            <Controls />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    </div>
  );
}
