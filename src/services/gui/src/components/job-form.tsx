"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useJobs } from "@/hooks/use-jobs";
import { JobTemplate, JobFormData } from "@/lib/types";
import { v4 as uuidv4 } from "uuid";

interface JobFormProps {
  onJobStart: (taskId: string) => void;
  initialTemplate?: JobTemplate | null;
}

export function JobForm({ onJobStart, initialTemplate }: JobFormProps) {
  const { createJob, loading } = useJobs();
  const [formData, setFormData] = useState<JobFormData>({
    sessionId: `session-${uuidv4()}`,
    experimentConfig: "default",
    phaseSequence: ["phase_1"],
  });

  // Update form when initial template changes
  useEffect(() => {
    if (initialTemplate) {
      setFormData({
        ...initialTemplate.config,
        sessionId: `${initialTemplate.config.sessionId}-${Date.now()}`, // Make unique
      });
    }
  }, [initialTemplate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const job = await createJob(formData);
      onJobStart(job.id);

      // Reset form for next use
      setFormData({
        sessionId: `session-${uuidv4()}`,
        experimentConfig: "default",
        phaseSequence: ["phase_1"],
      });
    } catch (error) {
      // Error handling is managed by useJobs hook
      console.error("Failed to start job:", error);
    }
  };

  const handlePhaseChange = (phase: string, checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      phaseSequence: checked
        ? [...(prev.phaseSequence || []), phase]
        : (prev.phaseSequence || []).filter((p) => p !== phase),
    }));
  };

  const availablePhases = ["phase_1", "phase_2", "phase_3"];
  const selectedPhases = formData.phaseSequence || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Start New Job</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {initialTemplate && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2">
                <Badge variant="secondary">
                  Template: {initialTemplate.name}
                </Badge>
              </div>
              {initialTemplate.description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {initialTemplate.description}
                </p>
              )}
            </div>
          )}

          <div>
            <Label htmlFor="sessionId">Session ID</Label>
            <Input
              id="sessionId"
              value={formData.sessionId}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, sessionId: e.target.value }))
              }
              placeholder="Enter session ID"
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              Unique identifier for this search session
            </p>
          </div>

          <div>
            <Label htmlFor="experimentConfig">Experiment Configuration</Label>
            <Select
              value={formData.experimentConfig || "default"}
              onValueChange={(value: string) =>
                setFormData((prev) => ({ ...prev, experimentConfig: value }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select configuration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="default">Default</SelectItem>
                <SelectItem value="comprehensive">Comprehensive</SelectItem>
                <SelectItem value="quick">Quick Test</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Phase Sequence</Label>
            <div className="space-y-2 mt-2">
              {availablePhases.map((phase) => (
                <div key={phase} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={phase}
                    checked={selectedPhases.includes(phase)}
                    onChange={(e) => handlePhaseChange(phase, e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor={phase} className="text-sm capitalize">
                    {phase}
                  </Label>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Select which phases to execute in sequence
            </p>
          </div>

          {selectedPhases.length === 0 && (
            <div className="text-sm text-red-600">
              Please select at least one phase to execute
            </div>
          )}

          <Button
            type="submit"
            disabled={loading || selectedPhases.length === 0}
            className="w-full"
          >
            {loading ? "Creating Job..." : "Start Job"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
