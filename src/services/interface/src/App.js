import React, { useCallback } from "react";
import JobSubmissionForm from "./components/JobSubmissionForm";
import JobList from "./components/JobList";
import { useJobPolling } from "./hooks/useJobPolling";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";

function App() {
  const { jobs, isLoading, error, refreshJobs, performJobAction } =
    useJobPolling(3000);

  const handleJobSubmitted = useCallback(
    ({ taskId, sessionId, jobName }) => {
      // Trigger immediate refresh to pick up the new job
      setTimeout(refreshJobs, 500);
    },
    [refreshJobs]
  );

  // Enhanced job action handler
  const handleJobAction = useCallback(
    async (action, jobId) => {
      const result = await performJobAction(action, jobId);

      if (!result.success) {
        // Show user-friendly error message
        alert(`Failed to ${action} job: ${result.error}`);
      } else {
        // Show success message for stop action
        if (action === "stop") {
          alert(result.message || "Job stopped successfully!");
        }
      }

      return result;
    },
    [performJobAction]
  );

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">
                  PS
                </span>
              </div>
              <h1 className="text-2xl font-bold">PrismSynth</h1>
            </div>
            <div className="text-sm text-muted-foreground">
              MCTS Job Monitoring Interface
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Global Error Display */}
        {error && (
          <Card className="border-destructive bg-destructive/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-destructive text-lg">
                System Error
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-destructive">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {isLoading && jobs.length === 0 && (
          <Card className="border-dashed">
            <CardContent className="pt-6 text-center">
              <div className="animate-pulse">
                <div className="w-8 h-8 bg-muted rounded-full mx-auto mb-2" />
                <p className="text-muted-foreground">Loading jobs...</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Job Submission Section */}
        <Card>
          <CardHeader>
            <CardTitle>Submit New Job</CardTitle>
            <CardDescription>
              Create and monitor new MCTS search jobs for mathematical problem
              solving.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <JobSubmissionForm onJobSubmitted={handleJobSubmitted} />
          </CardContent>
        </Card>

        {/* Job List Section */}
        <Card>
          <CardHeader>
            <CardTitle>Active Jobs</CardTitle>
            <CardDescription>
              Monitor the progress and results of your submitted jobs.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <JobList jobs={jobs} onJobAction={handleJobAction} />
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

export default App;
