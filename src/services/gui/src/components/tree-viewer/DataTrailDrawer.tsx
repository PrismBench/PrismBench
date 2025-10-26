"use client";

import React, { useCallback } from "react";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { NodeData, NodeDataTrailData } from "./types";

interface DataTrailDrawerProps {
  opened: boolean;
  onClose: () => void;
  selectedNodeData: NodeData | null | undefined;
}

export function DataTrailDrawer({
  opened,
  onClose,
  selectedNodeData,
}: DataTrailDrawerProps) {
  const renderDataTrailContent = useCallback(() => {
    if (
      !selectedNodeData ||
      !selectedNodeData.run_results ||
      selectedNodeData.run_results.length === 0
    )
      return (
        <p className="text-sm text-muted-foreground">
          No execution history available for this node.
        </p>
      );

    return (
      <Accordion type="multiple" className="w-full">
        {selectedNodeData.run_results.map((runResult, runIndex) => (
          <AccordionItem key={`run-${runIndex}`} value={`run-${runIndex}`}>
            <AccordionTrigger>
              <div className="flex items-center gap-2">
                <span className="font-medium">Run #{runIndex + 1}</span>
                <Badge
                  className={runResult.success ? "bg-green-600" : "bg-red-600"}
                >
                  {runResult.success ? "Success" : "Failed"}
                </Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {runResult.data_trail &&
                runResult.data_trail[0]?.problem_statement && (
                  <div className="mb-2">
                    <p className="font-semibold mb-1">Problem Statement:</p>
                    <div className="border p-2 rounded text-sm prose dark:prose-invert">
                      {runResult.data_trail[0].problem_statement}
                    </div>
                  </div>
                )}

              {(!runResult.data_trail || runResult.data_trail.length === 0) && (
                <p className="text-sm text-muted-foreground">
                  No attempts data available for this run.
                </p>
              )}

              {runResult.data_trail && runResult.data_trail.length > 0 && (
                <Accordion type="multiple" className="w-full">
                  {runResult.data_trail.map(
                    (trail: NodeDataTrailData, idx: number) => (
                      <AccordionItem
                        key={idx}
                        value={`attempt-${runIndex}-${idx}`}
                      >
                        <AccordionTrigger>
                          <div className="flex items-center gap-2">
                            <span className="font-medium">
                              Attempt #{(trail.attempt_num ?? idx) + 1}
                            </span>
                            <Badge
                              className={
                                trail.success
                                  ? "bg-green-600"
                                  : trail.fixed_by_problem_fixer
                                  ? "bg-yellow-400"
                                  : "bg-red-600"
                              }
                            >
                              {trail.success
                                ? "Success"
                                : trail.fixed_by_problem_fixer
                                ? "Fixed"
                                : "Failed"}
                            </Badge>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-2 text-sm">
                            {(trail.tests_passed_num !== null ||
                              trail.tests_failed_num !== null) && (
                              <div className="flex items-center gap-2">
                                <span className="font-semibold">
                                  Test Results:
                                </span>
                                <Badge className="bg-green-600">
                                  {trail.tests_passed_num ?? 0} passed
                                </Badge>
                                <Badge className="bg-red-600">
                                  {trail.tests_failed_num ?? 0} failed
                                </Badge>
                                {trail.tests_errored_num !== null && (
                                  <Badge className="bg-yellow-400">
                                    {trail.tests_errored_num} errored
                                  </Badge>
                                )}
                              </div>
                            )}

                            {trail.solution_code && (
                              <div>
                                <p className="font-semibold">Solution Code:</p>
                                <pre className="whitespace-pre-wrap bg-muted p-2 rounded overflow-auto text-xs">
                                  {trail.solution_code}
                                </pre>
                              </div>
                            )}

                            {trail.test_cases && (
                              <div>
                                <p className="font-semibold">Test Cases:</p>
                                <pre className="whitespace-pre-wrap bg-muted p-2 rounded overflow-auto text-xs">
                                  {trail.test_cases}
                                </pre>
                              </div>
                            )}

                            {trail.output && (
                              <div>
                                <p className="font-semibold">
                                  Execution Output:
                                </p>
                                <pre className="whitespace-pre-wrap bg-muted p-2 rounded overflow-auto text-xs">
                                  {trail.output}
                                </pre>
                              </div>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    )
                  )}
                </Accordion>
              )}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    );
  }, [selectedNodeData]);

  return (
    <Sheet open={opened} onOpenChange={(o) => !o && onClose()}>
      <SheetContent
        side="right"
        className="w-full sm:w-[800px] overflow-y-auto"
      >
        <SheetTitle>
          {selectedNodeData
            ? `Node ${selectedNodeData.id} Data Trail`
            : "Data Trail"}
        </SheetTitle>

        {selectedNodeData && (
          <ScrollArea className="h-[calc(100vh-120px)] pr-4 mt-4">
            <div className="space-y-6">
              <div className="border p-4 rounded">
                <h5 className="font-semibold mb-2">Challenge Details</h5>
                <div className="flex flex-wrap gap-2 mb-2">
                  <span className="font-semibold text-sm">Concepts:</span>
                  {selectedNodeData.concepts.sort().map((concept, idx) => (
                    <Badge key={idx}>{concept}</Badge>
                  ))}
                </div>
                <div className="text-sm mb-1">
                  <span className="font-semibold">Difficulty:</span>{" "}
                  {selectedNodeData.difficulty}
                </div>
                <div className="text-sm">
                  <span className="font-semibold">Phase:</span>{" "}
                  {selectedNodeData.phase}
                </div>
              </div>

              <div>
                <h5 className="font-semibold mb-2">Execution History</h5>
                {renderDataTrailContent()}
              </div>
            </div>
          </ScrollArea>
        )}
      </SheetContent>
    </Sheet>
  );
}
