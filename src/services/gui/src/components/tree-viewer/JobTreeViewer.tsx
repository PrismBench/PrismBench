"use client";

import React, { useMemo, useState, useCallback, useEffect } from "react";
import { Loader2 } from "lucide-react";
import ReactFlow, {
  Edge,
  Node,
  NodeTypes,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  Position,
  useReactFlow,
  NodeMouseHandler,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import dagre from "dagre";

import { useTreeData } from "@/hooks/use-tree-data";
import { NodeData, TreeData, NodeDataTrailData } from "./types";
import { TreeNode } from "./TreeNode";
import { DataTrailNode } from "./DataTrailNode";
import { ControlsPanel } from "./ControlsPanel";
import { DataTrailDrawer } from "./DataTrailDrawer";
import { LegendDrawer } from "./LegendDrawer";

const edgeColors = {
  improved: "#008000",
  same: "#808080",
  decreased: "#FF0000",
};

interface JobTreeViewerProps {
  sessionId: string;
  jobStatus?: string;
}

export default function JobTreeViewer({
  sessionId,
  jobStatus,
}: JobTreeViewerProps) {
  const [liveUpdate, setLiveUpdate] = useState(
    jobStatus !== "completed" && jobStatus !== "failed"
  );

  const {
    data: treeData,
    loading,
    error,
    refetch,
  } = useTreeData(sessionId, {
    enablePolling:
      liveUpdate && jobStatus !== "completed" && jobStatus !== "failed",
    pollingInterval: 5000,
    jobStatus,
  });

  // Define node types once
  const nodeTypes: NodeTypes = useMemo(
    () => ({
      customNode: TreeNode,
      dataTrailNode: DataTrailNode,
    }),
    []
  );

  // Transform nodes and edges using dagre
  const { nodes, edges } = useMemo(() => {
    if (!treeData) return { nodes: [], edges: [] };

    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: "TB", nodesep: 100, ranksep: 150 });

    const nodeWidth = 300;
    const nodeHeight = 320;

    treeData.nodes.forEach((node: NodeData) => {
      dagreGraph.setNode(node.id, {
        label: node.id,
        width: nodeWidth,
        height: nodeHeight,
      });
    });

    // Build edges from children relationships
    const computedEdges: Edge[] = [];
    treeData.nodes.forEach((node: NodeData) => {
      node.children.forEach((childId: string) => {
        dagreGraph.setEdge(node.id, childId);
        computedEdges.push({
          id: `${node.id}-${childId}`,
          source: node.id,
          target: childId,
          style: { stroke: edgeColors.same, strokeWidth: 2 },
          animated: false,
          type: "smoothstep",
        });
      });
    });

    dagre.layout(dagreGraph);

    const reactFlowNodes: Node<NodeData>[] = treeData.nodes.map(
      (nodeData: NodeData) => {
        const pos = dagreGraph.node(nodeData.id);
        return {
          id: nodeData.id,
          position: { x: pos.x - nodeWidth / 2, y: pos.y - nodeHeight / 2 },
          data: nodeData,
          type: "customNode",
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
        };
      }
    );

    return { nodes: reactFlowNodes, edges: computedEdges };
  }, [treeData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (error || !treeData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-lg font-semibold">
          {error || "No tree data available."}
        </p>
      </div>
    );
  }

  // ---------- Flow inner component ----------
  const FlowContent = () => {
    const reactFlowInstance = useReactFlow();
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const [dataTrailDrawerOpen, setDataTrailDrawerOpen] = useState(false);
    const [legendDrawerOpen, setLegendDrawerOpen] = useState(false);
    const [sidebarDataTrailNodes, setSidebarDataTrailNodes] = useState<Node[]>(
      []
    );
    const [sidebarDataTrailEdges, setSidebarDataTrailEdges] = useState<Edge[]>(
      []
    );

    const createSidebarDataTrailNodes = useCallback((nodeData: NodeData) => {
      if (!nodeData.run_results || nodeData.run_results.length === 0) {
        setSidebarDataTrailNodes([]);
        setSidebarDataTrailEdges([]);
        return;
      }
      const sourceNode: Node<NodeData> = {
        id: "sidebar-source",
        type: "customNode",
        position: { x: 150, y: 150 },
        data: nodeData,
      };
      const dNodes: Node[] = [];
      const dEdges: Edge[] = [];

      nodeData.run_results.forEach((run: any, runIdx: number) => {
        if (run.data_trail && run.data_trail.length > 0) {
          const runNode: Node = {
            id: `sidebar-run-${runIdx}`,
            type: "dataTrailNode",
            position: { x: 400, y: 50 + runIdx * 300 },
            data: {
              success: run.success,
              attempt_num: runIdx + 1,
              problem_statement: "Run Summary",
              test_cases: null,
              solution_code: null,
              output: null,
              tests_passed_num: null,
              tests_failed_num: null,
              tests_errored_num: null,
              fixed_by_problem_fixer: null,
              error_feedback: null,
              index: runIdx,
            } as NodeDataTrailData & { index: number },
          };
          dNodes.push(runNode);
          dEdges.push({
            id: `sidebar-edge-${runIdx}`,
            source: sourceNode.id,
            target: runNode.id,
            type: "straight",
            animated: true,
            style: { stroke: "#666", strokeDasharray: "5,5" },
          });

          run.data_trail.forEach(
            (trail: NodeDataTrailData, attemptIdx: number) => {
              const attemptNode: Node = {
                id: `sidebar-run-${runIdx}-attempt-${attemptIdx}`,
                type: "dataTrailNode",
                position: { x: 650, y: 50 + runIdx * 300 + attemptIdx * 150 },
                data: { ...trail, index: attemptIdx } as NodeDataTrailData & {
                  index: number;
                },
              };
              dNodes.push(attemptNode);
              dEdges.push({
                id: `sidebar-edge-from-run-${runIdx}-to-attempt-${attemptIdx}`,
                source: runNode.id,
                target: attemptNode.id,
                type: "straight",
                style: {
                  stroke: "#888",
                  strokeWidth: 1,
                  strokeDasharray: "3,3",
                },
              });
            }
          );
        }
      });
      setSidebarDataTrailNodes([sourceNode, ...dNodes]);
      setSidebarDataTrailEdges(dEdges);
    }, []);

    const onNodeClick: NodeMouseHandler = useCallback(
      (_, node) => {
        setSelectedNode(node.id);
        setDataTrailDrawerOpen(true);
        createSidebarDataTrailNodes(node.data as NodeData);
      },
      [createSidebarDataTrailNodes]
    );

    const centerOnNode = useCallback(
      (nodeId: string) => {
        const node = nodes.find((n) => n.id === nodeId);
        if (node && reactFlowInstance) {
          const nodeW = node.width || 300;
          const nodeH = node.height || 250;
          reactFlowInstance.setCenter(
            node.position.x + nodeW / 2,
            node.position.y + nodeH / 2,
            {
              zoom: 1.5,
              duration: 800,
            }
          );
        }
      },
      [nodes, reactFlowInstance]
    );

    const resetView = useCallback(() => {
      reactFlowInstance?.fitView({ padding: 0.2, duration: 800 });
      setSelectedNode(null);
    }, [reactFlowInstance]);

    const handleToggleLiveUpdate = () => {
      setLiveUpdate((prev) => !prev);
    };

    const handleRefresh = () => {
      if (!liveUpdate) {
        // manual refresh only if live update is off to avoid duplicate fetches
        refetch();
      }
    };

    const selectedNodeData = useMemo(() => {
      if (!selectedNode) return null;
      return treeData.nodes.find((n) => n.id === selectedNode) as
        | NodeData
        | undefined;
    }, [selectedNode, treeData]);

    const didInitialFitRef = React.useRef(false);

    useEffect(() => {
      if (
        !didInitialFitRef.current &&
        reactFlowInstance &&
        nodes.length > 0 &&
        edges.length > 0
      ) {
        const t = setTimeout(() => {
          reactFlowInstance.fitView({ padding: 0.2, duration: 800 });
          didInitialFitRef.current = true;
        }, 100);
        return () => clearTimeout(t);
      }
    }, [reactFlowInstance, nodes, edges]);

    return (
      <>
        <div className="h-[90vh] w-full relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.05}
            onNodeClick={onNodeClick}
            defaultEdgeOptions={{
              type: "smoothstep",
              style: { strokeWidth: 2 },
            }}
          >
            <Background variant={BackgroundVariant.Dots} />
            <Controls />
            <MiniMap nodeStrokeWidth={3} zoomable pannable />
            <ControlsPanel
              selectedNodeData={selectedNodeData}
              onReset={resetView}
              onCenter={centerOnNode}
              onToggleLegend={() => setLegendDrawerOpen(true)}
              liveUpdate={liveUpdate}
              onToggleLiveUpdate={handleToggleLiveUpdate}
              onRefresh={handleRefresh}
            />
          </ReactFlow>
        </div>

        <DataTrailDrawer
          opened={dataTrailDrawerOpen}
          onClose={() => {
            setDataTrailDrawerOpen(false);
          }}
          selectedNodeData={selectedNodeData}
        />

        <LegendDrawer
          opened={legendDrawerOpen}
          onClose={() => setLegendDrawerOpen(false)}
        />
      </>
    );
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Challenge Tree Visualization</h2>
      <ReactFlowProvider>
        <FlowContent />
      </ReactFlowProvider>
    </div>
  );
}
