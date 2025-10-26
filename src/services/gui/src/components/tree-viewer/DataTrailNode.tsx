import { NodeDataTrailData } from "./types";
import { Badge } from "@/components/ui/badge";
import { Position, Handle } from "reactflow";

export function DataTrailNode({
  data,
}: {
  data: NodeDataTrailData & { index: number };
}) {
  function getStatusColor() {
    if (data.success) return "#90EE90"; // lightgreen
    if (data.fixed_by_problem_fixer) return "#FFFACD"; // lightyellow
    return "#FFCCCB"; // lightred
  }

  const bgColor = getStatusColor();

  return (
    <div className="relative">
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: "#555", width: 10, height: 10 }}
      />

      <div
        className="w-64 min-h-[150px] border-2 rounded-md text-xs"
        style={{
          backgroundColor: bgColor,
          borderColor: data.success ? "#006400" : "#8B0000",
        }}
      >
        <div className="border-b px-3 py-2 font-bold">
          Attempt #{data.attempt_num ?? data.index + 1}
        </div>

        <div className="flex flex-col gap-2 p-3">
          <div className="flex items-center gap-2">
            <span className="font-medium">Status:</span>
            <Badge
              variant="default"
              className={
                data.success
                  ? "bg-green-600"
                  : data.fixed_by_problem_fixer
                  ? "bg-yellow-400"
                  : "bg-red-600"
              }
            >
              {data.success
                ? "Success"
                : data.fixed_by_problem_fixer
                ? "Fixed"
                : "Failed"}
            </Badge>
          </div>

          {(data.tests_passed_num !== null ||
            data.tests_failed_num !== null) && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Tests:</span>
              <Badge className="bg-green-600">
                {data.tests_passed_num ?? 0} passed
              </Badge>
              <Badge className="bg-red-600">
                {data.tests_failed_num ?? 0} failed
              </Badge>
              {data.tests_errored_num !== null && (
                <Badge className="bg-yellow-400">
                  {data.tests_errored_num} errored
                </Badge>
              )}
            </div>
          )}

          {data.error_feedback && (
            <span className="text-red-700 font-medium">
              Error: {data.error_feedback.substring(0, 100)}
              {data.error_feedback.length > 100 ? "..." : ""}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
