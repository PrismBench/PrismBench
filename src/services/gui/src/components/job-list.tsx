"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { useJobs } from "@/hooks/use-jobs";
import { Job } from "@/lib/types";
import {
  MoreHorizontal,
  Play,
  Square,
  RotateCcw,
  Trash2,
  Eye,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { JobPerformanceSummary } from "./job-performance-summary";
import { JobTreePreview } from "./job-tree-preview";
import { getStatusVariant } from "@/lib/utils";

interface JobListProps {
  showCompleted?: boolean;
  maxItems?: number;
}

export function JobList({ showCompleted = true, maxItems }: JobListProps) {
  const {
    jobs,
    activeJobs,
    loading,
    stopJob,
    retryJob,
    deleteJob,
    clearError,
  } = useJobs();
  const { toast } = useToast();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    job: Job | null;
  }>({
    open: false,
    job: null,
  });
  const router = useRouter();
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);

  const displayJobs = showCompleted
    ? jobs.slice(0, maxItems)
    : activeJobs.slice(0, maxItems);

  const handleStopJob = async (job: Job) => {
    if (!job.canStop) return;

    setActionLoading(job.id);
    try {
      await stopJob(job.id);
      toast({
        title: "Job Stopped",
        description: `Job ${job.id} has been stopped successfully.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to stop job",
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleRetryJob = async (job: Job) => {
    if (!job.canRetry) return;

    setActionLoading(job.id);
    try {
      const newJob = await retryJob(job.id);
      toast({
        title: "Job Retried",
        description: `New job ${newJob.id} has been created.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to retry job",
        variant: "destructive",
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteJob = (job: Job) => {
    setDeleteDialog({ open: true, job });
  };

  const confirmDeleteJob = () => {
    if (!deleteDialog.job) return;

    try {
      deleteJob(deleteDialog.job.id);
      toast({
        title: "Job Deleted",
        description: `Job ${deleteDialog.job.id} has been deleted.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete job",
        variant: "destructive",
      });
    } finally {
      setDeleteDialog({ open: false, job: null });
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const getJobDuration = (job: Job) => {
    const endTime = job.completedAt || new Date();
    const duration = endTime.getTime() - job.createdAt.getTime();
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);

    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  };

  if (loading && displayJobs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Jobs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-32" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>
              {showCompleted ? "All Jobs" : "Active Jobs"}
              {displayJobs.length > 0 && (
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  ({displayJobs.length})
                </span>
              )}
            </CardTitle>
            {activeJobs.length > 0 && (
              <Badge variant="default">{activeJobs.length} active</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {displayJobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {showCompleted ? "No jobs found" : "No active jobs"}
            </div>
          ) : (
            <div className="space-y-3">
              {displayJobs.map((job) => (
                <div key={job.id}>
                  <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm truncate">
                          {job.sessionId}
                        </span>
                        <Badge
                          variant={getStatusVariant(job.status)}
                          className="text-xs"
                        >
                          {job.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground space-y-1">
                        <div>ID: {job.id}</div>
                        <div className="flex items-center gap-3">
                          <span>Created: {formatDate(job.createdAt)}</span>
                          {job.completedAt && (
                            <span>Duration: {getJobDuration(job)}</span>
                          )}
                        </div>
                      </div>
                      {job.error && (
                        <div className="text-xs text-red-600 mt-1 truncate">
                          Error: {job.error}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          setExpandedJobId(
                            expandedJobId === job.id ? null : job.id
                          )
                        }
                        aria-label={
                          expandedJobId === job.id ? "Collapse" : "Expand"
                        }
                        className="h-8 w-8 p-0"
                      >
                        {expandedJobId === job.id ? "-" : "+"}
                      </Button>

                      {job.status === "running" && job.canStop && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStopJob(job)}
                          disabled={actionLoading === job.id}
                          className="h-8 w-8 p-0"
                        >
                          <Square className="h-3 w-3" />
                        </Button>
                      )}

                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          router.push(
                            `/tree/${encodeURIComponent(job.sessionId)}`
                          )
                        }
                        className="h-8 w-8 p-0"
                        aria-label="View Tree"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-8 w-8 p-0"
                            disabled={actionLoading === job.id}
                          >
                            <MoreHorizontal className="h-3 w-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {job.canRetry && (
                            <DropdownMenuItem
                              onClick={() => handleRetryJob(job)}
                            >
                              <RotateCcw className="mr-2 h-4 w-4" />
                              Retry Job
                            </DropdownMenuItem>
                          )}

                          {job.canStop && job.status === "running" && (
                            <DropdownMenuItem
                              onClick={() => handleStopJob(job)}
                            >
                              <Square className="mr-2 h-4 w-4" />
                              Stop Job
                            </DropdownMenuItem>
                          )}

                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => handleDeleteJob(job)}
                            className="text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>

                  {/* Show tree preview when NOT expanded */}
                  {expandedJobId !== job.id && job.sessionId && (
                    <div className="p-4 bg-gray-50 border-l border-r border-b rounded-b-lg">
                      <JobTreePreview
                        sessionId={job.sessionId}
                        jobStatus={job.status}
                      />
                    </div>
                  )}

                  {/* Show performance summary when expanded */}
                  {expandedJobId === job.id && job.sessionId && (
                    <div className="p-4 bg-muted rounded-b-lg">
                      <JobPerformanceSummary sessionId={job.sessionId} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog
        open={deleteDialog.open}
        onOpenChange={(open) => setDeleteDialog({ open, job: null })}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Job</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete job "{deleteDialog.job?.sessionId}
              "? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteJob}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
