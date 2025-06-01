import React, { useState } from "react";
import { v4 as uuidv4 } from "uuid"; // For generating unique session IDs
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Card, CardContent } from "./ui/card";

function JobSubmissionForm({ onJobSubmitted }) {
  // Added onJobSubmitted prop
  const [jobName, setJobName] = useState("");
  const [jobConfig, setJobConfig] = useState(""); // Kept for completeness, though not sent
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState("");

  const handleSubmit = async (event) => {
    // Made async
    event.preventDefault();
    setIsSubmitting(true);
    setValidationError("");

    const currentJobName = jobName.trim();
    const sessionId = currentJobName || uuidv4();
    const displayJobName = currentJobName || sessionId; // Use sessionId as name if original was empty

    // Job Configuration (jobConfig) is not sent to /run as per requirements

    try {
      const response = await fetch("/api/run", {
        // Using nginx proxy /api/run
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (response.status === 202) {
        // Check for 202 Accepted
        const data = await response.json();
        if (onJobSubmitted) {
          onJobSubmitted({
            taskId: data.task_id, // Response uses snake_case task_id
            sessionId: data.session_id, // session_id from response
            jobName: displayJobName,
          });
        }
        // Optionally clear form or give success feedback
        setJobName("");
        setJobConfig("");
      } else {
        const errorData = await response.text(); // Get text for more detailed error
        setValidationError(
          `Error submitting job: ${response.status} - ${errorData}`
        );
        console.error("Error submitting job:", response.status, errorData);
      }
    } catch (error) {
      setValidationError(`Network error: ${error.message}`);
      console.error("Network error submitting job:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Display validation errors */}
      {validationError && (
        <Card className="border-destructive bg-destructive/10">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">{validationError}</p>
          </CardContent>
        </Card>
      )}

      <div className="space-y-2">
        <Label htmlFor="jobName">Job Name (Optional)</Label>
        <Input
          type="text"
          id="jobName"
          value={jobName}
          onChange={(e) => setJobName(e.target.value)}
          placeholder="Leave blank for auto-generated ID"
          disabled={isSubmitting}
        />
        <p className="text-sm text-muted-foreground">
          Will be used as Session ID. If empty, a unique ID will be generated.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="jobConfig">Job Configuration</Label>
        <Textarea
          id="jobConfig"
          value={jobConfig}
          onChange={(e) => setJobConfig(e.target.value)}
          placeholder="Configuration notes (not submitted to backend)"
          disabled={isSubmitting}
          rows={4}
        />
        <p className="text-sm text-muted-foreground">
          This field is for your reference only and is not sent to the backend.
        </p>
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? "Submitting..." : "Submit Job"}
      </Button>
    </form>
  );
}

export default JobSubmissionForm;
