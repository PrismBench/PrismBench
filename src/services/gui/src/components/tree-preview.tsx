"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Eye, Activity, Layers, Brain } from "lucide-react";
import { useTreeData } from "@/hooks/use-tree-data";

interface TreePreviewProps {
  sessionId: string;
  onViewResults?: () => void;
}

export function TreePreview({ sessionId, onViewResults }: TreePreviewProps) {
  const { data, stats, loading, error } = useTreeData(sessionId, {
    enablePolling: false, // TreePreview doesn't need polling
  });

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">Tree Preview</CardTitle>
            <Skeleton className="h-4 w-16" />
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </CardContent>
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Tree Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            {error || "No tree data available"}
          </p>
        </CardContent>
      </Card>
    );
  }

  const topPhase = Object.entries(stats.phaseDistribution).sort(
    (a, b) => b[1] - a[1]
  )[0];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">Tree Preview</CardTitle>
          {onViewResults && (
            <Button size="sm" variant="ghost" onClick={onViewResults}>
              <Eye className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="flex items-center gap-1">
            <Activity className="h-3 w-3 text-blue-500" />
            <span className="font-medium">{stats.totalNodes}</span>
            <span className="text-muted-foreground">nodes</span>
          </div>
          <div className="flex items-center gap-1">
            <Layers className="h-3 w-3 text-green-500" />
            <span className="font-medium">{stats.maxDepth}</span>
            <span className="text-muted-foreground">depth</span>
          </div>
          <div className="flex items-center gap-1">
            <Brain className="h-3 w-3 text-purple-500" />
            <span className="font-medium">
              {Object.keys(stats.conceptDistribution).length}
            </span>
            <span className="text-muted-foreground">concepts</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-orange-500 font-medium">Avg:</span>
            <span className="font-medium">{stats.avgNodeValue.toFixed(2)}</span>
          </div>
        </div>

        {topPhase && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Top phase:</span>
            <Badge variant="secondary" className="text-xs">
              Phase {topPhase[0]} ({topPhase[1]} nodes)
            </Badge>
          </div>
        )}

        <div className="flex flex-wrap gap-1">
          {Object.entries(stats.conceptDistribution)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3)
            .map(([concept, count]) => (
              <Badge key={concept} variant="outline" className="text-xs">
                {concept}
              </Badge>
            ))}
          {Object.keys(stats.conceptDistribution).length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{Object.keys(stats.conceptDistribution).length - 3} more
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
