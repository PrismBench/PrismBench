"use client";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, Clock } from "lucide-react";
import { useTreeData } from "@/hooks/use-tree-data";

interface JobTreePreviewProps {
  sessionId: string;
  jobStatus: string;
  className?: string;
}

export function JobTreePreview({
  sessionId,
  jobStatus,
  className = "",
}: JobTreePreviewProps) {
  const { data, stats, loading, error, lastUpdate } = useTreeData(sessionId, {
    enablePolling: jobStatus === "running" || jobStatus === "pending",
    pollingInterval: 5000,
    jobStatus,
  });

  const isJobActive = jobStatus === "running" || jobStatus === "pending";

  if (loading && !data) {
    return (
      <div className={`space-y-2 ${className}`}>
        <div className="flex items-center gap-2 mb-2">
          <div className="text-xs font-medium text-muted-foreground">
            Live Tree Visualization
          </div>
          {isJobActive && (
            <Badge variant="outline" className="text-xs animate-pulse">
              <Activity className="h-2 w-2 mr-1" />
              Live
            </Badge>
          )}
        </div>
        <div className="grid grid-cols-4 gap-2">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data || data.nodes.length === 0) {
    return (
      <div className={`space-y-2 ${className}`}>
        <div className="flex items-center gap-2 mb-2">
          <div className="text-xs font-medium text-muted-foreground">
            Live Tree Visualization
          </div>
          {isJobActive && (
            <Badge variant="outline" className="text-xs animate-pulse">
              <Activity className="h-2 w-2 mr-1" />
              Live
            </Badge>
          )}
        </div>
        <div className="text-center py-3 text-xs text-muted-foreground">
          {isJobActive ? "Waiting for tree data..." : "No tree data available"}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="text-xs font-medium text-muted-foreground">
            Live Tree Visualization
          </div>
          <Badge variant="secondary" className="text-xs">
            {data.nodes.length} nodes
          </Badge>
          {isJobActive && (
            <Badge variant="outline" className="text-xs animate-pulse">
              <Activity className="h-2 w-2 mr-1" />
              Live
            </Badge>
          )}
        </div>
        {lastUpdate && (
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Clock className="h-2 w-2" />
            {lastUpdate.toLocaleTimeString()}
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-2 text-xs">
        <div className="bg-muted p-2 rounded border">
          <div className="text-lg font-bold text-blue-600">
            {stats?.totalNodes || 0}
          </div>
          <div className="text-xs text-muted-foreground">Total Nodes</div>
        </div>
        <div className="bg-muted p-2 rounded border">
          <div className="text-lg font-bold text-green-600">
            {stats?.maxDepth || 0}
          </div>
          <div className="text-xs text-muted-foreground">Max Depth</div>
        </div>
        <div className="bg-muted p-2 rounded border">
          <div className="text-lg font-bold text-purple-600">
            {Object.keys(stats?.conceptDistribution || {}).length}
          </div>
          <div className="text-xs text-muted-foreground">Concepts</div>
        </div>
        <div className="bg-muted p-2 rounded border">
          <div className="text-lg font-bold text-orange-600">
            {Object.keys(stats?.conceptCombinations || {}).length}
          </div>
          <div className="text-xs text-muted-foreground">Combinations</div>
        </div>
      </div>

      {/* Mini Phase Distribution */}
      {stats && Object.keys(stats.phaseDistribution).length > 0 && (
        <div className="space-y-1">
          <div className="text-xs font-medium text-muted-foreground">
            Phase Distribution
          </div>
          <div className="flex gap-1">
            {Object.entries(stats.phaseDistribution).map(([phase, count]) => {
              const percentage = ((count / stats.totalNodes) * 100).toFixed(1);
              const phaseColors = {
                1: "bg-yellow-500",
                2: "bg-green-500",
                3: "bg-blue-500",
              };

              const color =
                phaseColors[parseInt(phase) as keyof typeof phaseColors] ||
                "bg-gray-500";

              return (
                <div key={phase} className="flex-1">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs">P{phase}</span>
                    <span className="text-xs">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className={`${color} h-1.5 rounded-full transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
