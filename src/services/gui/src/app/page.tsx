"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { JobForm } from "@/components/job-form";
import { JobList } from "@/components/job-list";
import { JobTemplates } from "@/components/job-templates";
import { ResultsTable } from "@/components/results-table";
import { Toaster } from "@/components/ui/toaster";
import { useJobs } from "@/hooks/use-jobs";
import { Job, JobTemplate } from "@/lib/types";
import { Plus, Activity, History, Zap, BarChart3, Circle } from "lucide-react";
import { useServiceHealth } from "@/hooks/use-service-health";
import { SERVICES } from "@/lib/health";

export default function Dashboard() {
  const router = useRouter();
  const { jobs, activeJobs, completedJobs, hasActiveJobs, error, clearError } =
    useJobs();

  const [showJobForm, setShowJobForm] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<JobTemplate | null>(
    null
  );

  const handleUseTemplate = (template: JobTemplate) => {
    setSelectedTemplate(template);
    setShowJobForm(true);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">PrismBench GUI</h1>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="text-red-800">
                <strong>Error:</strong> {error}
              </div>
              <Button size="sm" variant="ghost" onClick={clearError}>
                Dismiss
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Job Management */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Form */}
          {showJobForm && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Create New Job</CardTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setShowJobForm(false);
                      setSelectedTemplate(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <JobForm
                  onJobStart={() => {}}
                  initialTemplate={selectedTemplate}
                />
              </CardContent>
            </Card>
          )}

          {/* Job List with integrated tree visualization */}
          <JobList showCompleted={true} maxItems={10} />

          {/* Results Table for completed jobs */}
          {completedJobs.length > 0 && <ResultsTable jobs={completedJobs} />}
        </div>

        {/* Right Column - Templates and Quick Stats */}
        <div className="space-y-6">
          <JobTemplates
            onUseTemplate={handleUseTemplate}
            showCreateDialog={true}
          />
          {/* Quick Stats + System Status */}
          <Card>
            <CardContent className="flex flex-col gap-4 p-4">
              <div className="flex gap-8">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {activeJobs.length}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Active Jobs
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <History className="h-4 w-4 text-green-600" />
                  <div>
                    <div className="text-2xl font-bold">
                      {completedJobs.length}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Completed
                    </div>
                  </div>
                </div>
              </div>
              {/* Service status pills stacked vertically */}
              <div className="flex flex-col gap-3 mt-2">
                {useServiceHealth(SERVICES).map((service) => {
                  let color = "text-gray-400";
                  if (service.status === "healthy") color = "text-green-500";
                  else if (service.status === "unhealthy")
                    color = "text-yellow-400";
                  else if (service.status === "unreachable")
                    color = "text-red-500";
                  return (
                    <span
                      key={service.name}
                      className="inline-flex items-center px-4 py-2 rounded-full bg-white border border-gray-300 shadow-sm text-base font-semibold gap-2"
                    >
                      <Circle
                        className={`h-4 w-4 ${color} drop-shadow-md`}
                        fill="currentColor"
                      />
                      <span>{service.label}</span>
                    </span>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      {/* Toast notifications */}
      <Toaster />
    </div>
  );
}
