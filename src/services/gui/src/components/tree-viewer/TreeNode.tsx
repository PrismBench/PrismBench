import { Badge } from "@/components/ui/badge";
import { Position, Handle } from "reactflow";

import { NodeData } from "./types";
import { Phase, PhaseColors } from "./types";

const phaseColors: PhaseColors = {
  1: { bg: "#FFFACD", border: "#00008B" },
  2: { bg: "#90EE90", border: "#006400" },
  3: { bg: "#ADD8E6", border: "#00008B" },
};

export function TreeNode({
  data,
  selected,
}: {
  data: NodeData;
  selected: boolean;
}) {
  const { bg, border } = phaseColors[data.phase as Phase] ?? {
    bg: "#FFFFFF",
    border: "#000000",
  };

  return (
    <div className="relative">
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: "#555", width: 10, height: 10 }}
      />

      <div
        className="w-72 min-h-[200px] rounded-md border-2 p-4 text-xs"
        style={{
          backgroundColor: bg,
          borderColor: selected ? "#FF5500" : border,
          borderWidth: selected ? 3 : 2,
          boxShadow: selected ? "0 0 10px rgba(255,85,0,.5)" : "none",
        }}
      >
        <div className="flex items-center justify-between gap-1 border-b pb-2">
          <div className="flex flex-wrap gap-1">
            {data.concepts.sort().map((concept, idx) => (
              <Badge key={idx} variant="secondary" className="text-[10px]">
                {concept}
              </Badge>
            ))}
          </div>
          <Badge
            className={
              data.difficulty === "very easy"
                ? "bg-blue-600"
                : data.difficulty === "easy"
                ? "bg-green-600"
                : data.difficulty === "medium"
                ? "bg-yellow-500"
                : data.difficulty === "hard"
                ? "bg-orange-600"
                : "bg-red-600"
            }
          >
            {data.difficulty}
          </Badge>
        </div>

        <div className="flex flex-col gap-1 mt-2">
          <div className="flex items-center gap-1">
            <span className="font-medium">Score:</span>
            <span>{data.value.toFixed(2)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="font-medium">Visits:</span>
            <span>{data.visits}</span>
          </div>
          <div className="font-bold mt-1">Phase {data.phase}</div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: "#555", width: 10, height: 10 }}
      />
    </div>
  );
}
