import React from "react";
import { Button } from "@/components/ui/button";
import { Panel } from "reactflow";
import { NodeData } from "./types";
import { Info } from "lucide-react";

interface ControlsPanelProps {
  selectedNodeData: NodeData | null | undefined;
  onReset: () => void;
  onCenter: (id: string) => void;
  onToggleLegend: () => void;
  liveUpdate: boolean;
  onToggleLiveUpdate: () => void;
  onRefresh: () => void;
}

export function ControlsPanel({
  selectedNodeData,
  onReset,
  onCenter,
  onToggleLegend,
  liveUpdate,
  onToggleLiveUpdate,
  onRefresh,
}: ControlsPanelProps) {
  return (
    <Panel position="top-right">
      <Button
        variant="secondary"
        size="sm"
        className="mr-2 flex items-center gap-1"
        onClick={onToggleLegend}
      >
        <Info className="h-3 w-3" /> Legend
      </Button>
      <Button variant="secondary" size="sm" className="mr-2" onClick={onReset}>
        Reset View
      </Button>
      <Button
        variant={liveUpdate ? "default" : "secondary"}
        size="sm"
        className="mr-2"
        onClick={onToggleLiveUpdate}
      >
        {liveUpdate ? "Pause Live" : "Live Update"}
      </Button>
      <Button
        variant="secondary"
        size="sm"
        className="mr-2"
        onClick={onRefresh}
      >
        Refresh
      </Button>
      {selectedNodeData && (
        <Button
          variant="default"
          size="sm"
          onClick={() => onCenter(selectedNodeData.id)}
        >
          Focus Selected
        </Button>
      )}
    </Panel>
  );
}
