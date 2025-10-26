import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { PhaseColors } from "./types";
import React from "react";

const phaseColors: PhaseColors = {
  1: { bg: "#FFFACD", border: "#00008B" },
  2: { bg: "#90EE90", border: "#006400" },
  3: { bg: "#ADD8E6", border: "#00008B" },
};

const edgeColors = {
  improved: "#008000",
  same: "#808080",
  decreased: "#FF0000",
};

interface LegendDrawerProps {
  opened: boolean;
  onClose: () => void;
}

export function LegendDrawer({ opened, onClose }: LegendDrawerProps) {
  return (
    <Sheet open={opened} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="left" className="w-80 sm:w-96 overflow-y-auto">
        <SheetTitle>Tree Visualization Legend</SheetTitle>
        <div className="mt-6 space-y-4 text-sm">
          <div>
            <h4 className="font-semibold mb-2">Node Phases</h4>
            <div className="flex flex-col gap-2">
              {Object.entries(phaseColors).map(([phase, colors]) => (
                <div key={phase} className="flex items-center gap-2">
                  <div
                    className="w-5 h-5 rounded-sm border"
                    style={{
                      backgroundColor: colors.bg,
                      borderColor: colors.border,
                    }}
                  />
                  <span>Phase {phase}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Connection Types</h4>
            <div className="flex flex-col gap-2">
              {Object.entries(edgeColors).map(([perf, color]) => (
                <div key={perf} className="flex items-center gap-2">
                  <div
                    className="w-10 h-1"
                    style={{ backgroundColor: color }}
                  />
                  <span className="capitalize">{perf}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Difficulty Levels</h4>
            <div className="flex flex-wrap gap-2">
              {[
                { diff: "very easy", color: "bg-blue-600" },
                { diff: "easy", color: "bg-green-600" },
                { diff: "medium", color: "bg-yellow-500" },
                { diff: "hard", color: "bg-orange-600" },
                { diff: "very hard", color: "bg-red-600" },
              ].map(({ diff, color }) => (
                <Badge key={diff} className={`${color}`}>
                  {diff}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Data Trail Status</h4>
            <div className="flex gap-2">
              <Badge className="bg-green-600">Success</Badge>
              <Badge className="bg-yellow-400">Fixed</Badge>
              <Badge className="bg-red-600">Failed</Badge>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
