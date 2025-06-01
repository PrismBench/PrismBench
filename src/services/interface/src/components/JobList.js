import React from "react";
import JobProgressTree from "./JobProgressTree";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Button } from "./ui/button";
import { MoreVertical, Square, RefreshCw } from "lucide-react";

// Status color mapping
const getStatusVariant = (status) => {
  switch (status) {
    case "completed":
      return "default"; // Green
    case "running":
      return "secondary"; // Blue
    case "error":
      return "destructive"; // Red
    case "pending":
      return "outline"; // Gray
    case "cancelled":
      return "outline"; // Gray with different styling
    case "phase1_completed":
      return "secondary"; // Blue
    default:
      return "outline";
  }
};

const getStatusLabel = (status) => {
  switch (status) {
    case "completed":
      return "Completed";
    case "running":
      return "Running";
    case "error":
      return "Error";
    case "pending":
      return "Pending";
    case "cancelled":
      return "Cancelled";
    case "phase1_completed":
      return "Phase 1 Complete";
    default:
      return "Unknown";
  }
};

// Job Actions Component
function JobActions({ job, onAction }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreVertical className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Actions</DropdownMenuLabel>
        <DropdownMenuItem onClick={() => onAction("refresh", job.sessionId)}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </DropdownMenuItem>
        {job.status === "running" && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onAction("stop", job.sessionId)}>
              <Square className="mr-2 h-4 w-4" />
              Stop Job
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// Job Card Component
function JobCard({ job, onAction }) {
  return (
    <Card key={job.sessionId} className="relative">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">
              {job.jobName || job.sessionId}
            </CardTitle>
            <CardDescription>
              Session ID: {job.sessionId}
              {job.taskId && ` • Task ID: ${job.taskId}`}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={getStatusVariant(job.status)}>
              {getStatusLabel(job.status)}
            </Badge>
            <JobActions job={job} onAction={onAction} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <JobProgressTree
          jobId={job.sessionId}
          jobName={job.jobName || job.sessionId}
          treeData={job.treeData}
          status={job.status}
          statusInfo={job.statusInfo}
        />
      </CardContent>
    </Card>
  );
}

function JobList({ jobs, onJobAction }) {
  // Filter jobs by status
  const runningJobs = jobs?.filter((job) => job.status === "running") || [];
  const completedJobs = jobs?.filter((job) => job.status === "completed") || [];
  const errorJobs = jobs?.filter((job) => job.status === "error") || [];
  const pendingJobs =
    jobs?.filter(
      (job) =>
        job.status === "pending" ||
        job.status === "phase1_completed" ||
        job.status === "cancelled"
    ) || [];
  const allJobs = jobs || [];

  const handleJobAction = (action, jobId) => {
    if (onJobAction) {
      onJobAction(action, jobId);
    } else {
      // Default action handling
      console.log(`Action: ${action} on job: ${jobId}`);

      switch (action) {
        case "refresh":
          // Trigger a refresh for this specific job
          window.location.reload();
          break;
        case "stop":
          alert("Stop action requires backend integration");
          break;
        default:
          console.log(`Unsupported action: ${action}`);
      }
    }
  };

  if (!jobs || jobs.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No jobs submitted yet.</p>
        <p className="text-sm text-muted-foreground mt-2">
          Submit a new job above to get started.
        </p>
      </div>
    );
  }

  const renderJobList = (jobList, emptyMessage) => {
    if (jobList.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-muted-foreground">{emptyMessage}</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {jobList.map((job) => (
          <JobCard key={job.sessionId} job={job} onAction={handleJobAction} />
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">All ({allJobs.length})</TabsTrigger>
          <TabsTrigger value="running">
            Running ({runningJobs.length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({completedJobs.length})
          </TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({pendingJobs.length})
          </TabsTrigger>
          <TabsTrigger value="error">Error ({errorJobs.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {renderJobList(allJobs, "No jobs found.")}
        </TabsContent>

        <TabsContent value="running" className="space-y-4">
          {renderJobList(runningJobs, "No running jobs.")}
        </TabsContent>

        <TabsContent value="completed" className="space-y-4">
          {renderJobList(completedJobs, "No completed jobs.")}
        </TabsContent>

        <TabsContent value="pending" className="space-y-4">
          {renderJobList(pendingJobs, "No pending jobs.")}
        </TabsContent>

        <TabsContent value="error" className="space-y-4">
          {renderJobList(errorJobs, "No jobs with errors.")}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default JobList;
