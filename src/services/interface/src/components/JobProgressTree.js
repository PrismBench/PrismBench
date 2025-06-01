import React, { useState, memo } from "react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { ChartContainer, SimpleBarChart } from "./ui/chart";
import {
  ChevronDown,
  ChevronRight,
  TreePine,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  BarChart3,
  Eye,
  EyeOff,
} from "lucide-react";

// Status icons mapping
const getStatusIcon = (status) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-4 h-4 text-green-600" />;
    case "running":
      return <Activity className="w-4 h-4 text-blue-600" />;
    case "error":
      return <AlertCircle className="w-4 h-4 text-red-600" />;
    case "pending":
      return <Clock className="w-4 h-4 text-gray-600" />;
    default:
      return <Clock className="w-4 h-4 text-gray-600" />;
  }
};

// Memoized TreeNode component for optimal performance
const TreeNode = memo(function TreeNode({
  node,
  allNodesMap,
  level,
  isLast = false,
}) {
  const [isExpanded, setIsExpanded] = useState(level < 2); // Auto-expand first 2 levels

  if (!node) return null;

  const children = node.children
    .map((childId) => allNodesMap.get(childId))
    .filter((child) => child);

  const hasChildren = children.length > 0;
  const marginLeft = level * 24;

  return (
    <div className="relative">
      {/* Tree line connections */}
      {level > 0 && (
        <>
          {/* Horizontal line */}
          <div
            className="absolute border-l-2 border-border"
            style={{
              left: marginLeft - 24,
              top: 0,
              height: "24px",
              width: "16px",
              borderBottom: "2px solid hsl(var(--border))",
            }}
          />
          {/* Vertical line for non-last items */}
          {!isLast && (
            <div
              className="absolute border-l-2 border-border"
              style={{
                left: marginLeft - 24,
                top: 24,
                height: "100%",
              }}
            />
          )}
        </>
      )}

      <div style={{ marginLeft }} className="relative">
        <Card className="mb-2 transition-all duration-200 hover:shadow-md">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              {hasChildren && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="h-6 w-6 p-0"
                >
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </Button>
              )}
              {!hasChildren && <div className="w-6" />}

              <div className="flex items-center gap-2 flex-1">
                {getStatusIcon(node.status)}
                <CardTitle className="text-sm font-medium">
                  Node {node.id}
                </CardTitle>
                <Badge variant="outline" className="text-xs">
                  Phase {node.phase || "N/A"}
                </Badge>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-0 space-y-2">
            {node.challenge_description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {node.challenge_description}
              </p>
            )}

            <div className="grid grid-cols-2 gap-2 text-xs">
              {node.difficulty && (
                <div>
                  <span className="font-medium">Difficulty:</span>{" "}
                  {node.difficulty}
                </div>
              )}
              {node.value !== undefined && (
                <div>
                  <span className="font-medium">Value:</span>{" "}
                  {node.value.toFixed(3)}
                </div>
              )}
              {node.visits !== undefined && (
                <div>
                  <span className="font-medium">Visits:</span> {node.visits}
                </div>
              )}
              {node.status && (
                <div>
                  <span className="font-medium">Status:</span> {node.status}
                </div>
              )}
            </div>

            {/* Progress bar based on value or visits */}
            {(node.value !== undefined || node.visits !== undefined) && (
              <div className="mt-2 space-y-2">
                {node.value !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs text-muted-foreground mb-1">
                      <span>Value Progress</span>
                      <span>{(node.value * 100).toFixed(1)}%</span>
                    </div>
                    <Progress
                      value={Math.min(Math.max(node.value * 100, 0), 100)}
                      className="h-2"
                    />
                  </div>
                )}
                {node.visits !== undefined && (
                  <div>
                    <div className="flex justify-between text-xs text-muted-foreground mb-1">
                      <span>Visit Progress</span>
                      <span>{node.visits} visits</span>
                    </div>
                    <Progress
                      value={Math.min(Math.max((node.visits || 0) * 5, 0), 100)}
                      className="h-2"
                    />
                  </div>
                )}
              </div>
            )}

            {/* Parent and children info */}
            {(node.parents?.length > 0 || node.children?.length > 0) && (
              <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
                {node.parents?.length > 0 && (
                  <div>
                    <span className="font-medium">Parents:</span>{" "}
                    {node.parents.join(", ")}
                  </div>
                )}
                {node.children?.length > 0 && (
                  <div>
                    <span className="font-medium">Children:</span>{" "}
                    {node.children.length} nodes
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Render children */}
        {hasChildren && isExpanded && (
          <div className="pl-6">
            {children.map((childNode, index) => (
              <TreeNode
                key={childNode.id}
                node={childNode}
                allNodesMap={allNodesMap}
                level={level + 1}
                isLast={index === children.length - 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
});

function JobProgressTree({ jobId, jobName, treeData, status, statusInfo }) {
  const [showChart, setShowChart] = useState(false);
  const [showDetails, setShowDetails] = useState(true);

  let rootNodes = [];
  let nodesMap = new Map();
  let chartData = [];

  if (treeData && treeData.nodes && treeData.nodes.length > 0) {
    treeData.nodes.forEach((node) => nodesMap.set(node.id, node));

    // Find root nodes (nodes with empty parents list)
    rootNodes = treeData.nodes.filter(
      (node) => !node.parents || node.parents.length === 0
    );

    // Fallback: find nodes not referenced as children
    if (rootNodes.length === 0) {
      const allChildIds = new Set();
      treeData.nodes.forEach((n) => {
        if (n.children) {
          n.children.forEach((childId) => allChildIds.add(childId));
        }
      });
      rootNodes = treeData.nodes.filter((n) => !allChildIds.has(n.id));

      // Final fallback: use first node if no clear roots
      if (rootNodes.length === 0 && treeData.nodes.length > 0) {
        rootNodes = [treeData.nodes[0]];
      }
    }

    // Prepare chart data for visualization
    chartData = treeData.nodes.slice(0, 10).map((node, index) => ({
      name: `Node ${node.id}`,
      value: node.value || 0,
      visits: node.visits || 0,
      phase: node.phase || 1,
    }));
  }

  return (
    <div className="space-y-4">
      {/* Job summary and controls */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <TreePine className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Tree Structure</span>
            <div className="flex items-center gap-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowChart(!showChart)}
                className="h-6 px-2 text-xs"
              >
                <BarChart3 className="w-3 h-3 mr-1" />
                {showChart ? "Hide Chart" : "Show Chart"}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="h-6 px-2 text-xs"
              >
                {showDetails ? (
                  <EyeOff className="w-3 h-3 mr-1" />
                ) : (
                  <Eye className="w-3 h-3 mr-1" />
                )}
                {showDetails ? "Hide" : "Show"} Details
              </Button>
            </div>
          </div>
          {treeData && treeData.nodes && (
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Nodes: {treeData.nodes.length}</p>
              {treeData.concepts && (
                <p>
                  Concepts: {treeData.concepts.slice(0, 3).join(", ")}
                  {treeData.concepts.length > 3 ? "..." : ""}
                </p>
              )}
              {treeData.difficulties && (
                <p>
                  Difficulties: {treeData.difficulties.slice(0, 3).join(", ")}
                  {treeData.difficulties.length > 3 ? "..." : ""}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Status info summary */}
        {statusInfo?.phases && (
          <div className="text-xs space-y-1">
            {Object.entries(statusInfo.phases).map(([phase, info]) => (
              <div key={phase} className="flex items-center gap-2">
                <span className="capitalize">{phase}:</span>
                <Badge variant="outline" className="text-xs">
                  {info.status || "pending"}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Chart visualization */}
      {showChart && chartData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Node Performance Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer className="h-[200px]">
              <SimpleBarChart
                data={chartData}
                dataKey="value"
                xKey="name"
                color="#3b82f6"
              />
            </ChartContainer>
          </CardContent>
        </Card>
      )}

      {/* Tree visualization */}
      {showDetails &&
        (treeData && treeData.nodes ? (
          rootNodes.length > 0 ? (
            <div className="space-y-2">
              {rootNodes.map((rootNode, index) => (
                <TreeNode
                  key={rootNode.id}
                  node={rootNode}
                  allNodesMap={nodesMap}
                  level={0}
                  isLast={index === rootNodes.length - 1}
                />
              ))}
            </div>
          ) : (
            <Card className="border-dashed">
              <CardContent className="pt-6 text-center">
                <TreePine className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">
                  No tree structure available for visualization
                </p>
              </CardContent>
            </Card>
          )
        ) : (
          <Card className="border-dashed">
            <CardContent className="pt-6 text-center">
              <div className="animate-pulse">
                <TreePine className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">
                  Loading tree data...
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
    </div>
  );
}

export default JobProgressTree;
