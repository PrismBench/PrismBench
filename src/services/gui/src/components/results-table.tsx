"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Job } from "@/lib/types";
import { TreePreview } from "./tree-preview";
import { Eye } from "lucide-react";
import { getStatusVariant } from "@/lib/utils";

interface ResultsTableProps {
  jobs: Job[];
  onViewResults?: (job: Job) => void;
}

export function ResultsTable({ jobs, onViewResults }: ResultsTableProps) {
  if (jobs.length === 0) {
    return null;
  }


  const formatDuration = (start: Date, end?: Date) => {
    if (!end) return "-";
    const duration = end.getTime() - start.getTime();
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Completed Jobs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Table for basic info */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Task ID</TableHead>
                <TableHead>Session ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobs.map((job) => (
                <TableRow key={job.id}>
                  <TableCell className="font-mono text-sm">
                    {job.id.substring(0, 8)}...
                  </TableCell>
                  <TableCell className="font-mono text-sm">
                    {job.sessionId}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusVariant(job.status)}>
                      {job.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {job.createdAt.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-sm">
                    {formatDuration(job.createdAt, job.completedAt)}
                  </TableCell>
                  <TableCell>
                    {job.status === "completed" && onViewResults && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onViewResults(job)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Results
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Tree previews for completed jobs */}
          {jobs.filter((job) => job.status === "completed").length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Tree Previews</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {jobs
                  .filter((job) => job.status === "completed")
                  .slice(0, 6) // Show max 6 previews
                  .map((job) => (
                    <TreePreview
                      key={job.id}
                      sessionId={job.sessionId}
                      onViewResults={
                        onViewResults ? () => onViewResults(job) : undefined
                      }
                    />
                  ))}
              </div>
              {jobs.filter((job) => job.status === "completed").length > 6 && (
                <p className="text-xs text-muted-foreground text-center">
                  Showing 6 of{" "}
                  {jobs.filter((job) => job.status === "completed").length}{" "}
                  completed jobs
                </p>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
