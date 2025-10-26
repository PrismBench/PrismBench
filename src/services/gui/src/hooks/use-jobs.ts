import { useState, useEffect, useCallback } from "react";
import { Job, JobFormData, JobTemplate } from "@/lib/types";
import { api } from "@/lib/api";

const TEMPLATES_STORAGE_KEY = "prism-job-templates";

function getDefaultTemplates(): JobTemplate[] {
  return [
    {
      id: "quick-start",
      name: "Quick Start",
      description: "Default configuration for quick testing",
      config: {
        sessionId: "session-quick-start",
        experimentConfig: "default",
        phaseSequence: ["phase_1"],
      },
      createdAt: new Date(0),
      isDefault: true,
    },
    {
      id: "full-pipeline",
      name: "Full Pipeline",
      description: "Complete 3-phase pipeline execution",
      config: {
        sessionId: "session-full-pipeline",
        experimentConfig: "comprehensive",
        phaseSequence: ["phase_1", "phase_2", "phase_3"],
      },
      createdAt: new Date(0),
      isDefault: true,
    },
  ];
}

function loadTemplatesFromStorage(): JobTemplate[] {
  if (typeof window === "undefined") return getDefaultTemplates();
  try {
    const stored = localStorage.getItem(TEMPLATES_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored).map((t: any) => ({
        ...t,
        createdAt: t.createdAt ? new Date(t.createdAt) : new Date(),
      }));
    }
  } catch (e) {
    // ignore
  }
  return getDefaultTemplates();
}

function saveTemplatesToStorage(templates: JobTemplate[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TEMPLATES_STORAGE_KEY, JSON.stringify(templates));
}

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [templates, setTemplates] = useState<JobTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch jobs from backend
  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/status");
      // Backend returns { tasks: { [task_id]: { ... } } }
      const tasksObj = res.data.tasks || {};
      const jobsArr: Job[] = Object.values(tasksObj).map((task: any) => ({
        id: task.task_id,
        sessionId: task.session_id,
        status: task.status,
        createdAt: task.phases?.phase_1?.created_at
          ? new Date(task.phases.phase_1.created_at)
          : new Date(),
        canStop: task.status === "running" || task.status === "pending",
        canRetry:
          task.status === "failed" ||
          task.status === "cancelled" ||
          task.status === "completed",
        // Add more fields as needed
      }));
      setJobs(jobsArr);
    } catch (err) {
      setError("Failed to fetch jobs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    // Optionally poll every 5s
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [fetchJobs]);

  // Load templates from storage on client only
  useEffect(() => {
    setTemplates(loadTemplatesFromStorage());
  }, []);

  const createTemplate = useCallback(
    (name: string, description: string, config: JobFormData) => {
      const template: JobTemplate = {
        id: `template-${Date.now()}`,
        name,
        description,
        config,
        createdAt: new Date(),
        isDefault: false,
      };
      setTemplates((prev) => {
        const next = [...prev, template];
        saveTemplatesToStorage(next);
        return next;
      });
      return template;
    },
    []
  );

  const deleteTemplate = useCallback((templateId: string) => {
    setTemplates((prev) => {
      const next = prev.filter((t) => t.id !== templateId && !t.isDefault);
      saveTemplatesToStorage(next);
      return next;
    });
  }, []);

  const clearError = useCallback(() => setError(null), []);

  const createJob = useCallback(async (jobData: JobFormData): Promise<Job> => {
    setLoading(true);
    setError(null);
    try {
      // Create session using the correct endpoint
      await api.post("/initialize", {
        session_id: jobData.sessionId,
      });

      // Start task using the correct endpoint
      const taskResponse = await api.post("/run", {
        session_id: jobData.sessionId,
      });

      const newJob: Job = {
        id: taskResponse.data.task_id,
        sessionId: jobData.sessionId,
        status: "pending",
        createdAt: new Date(),
        canStop: true,
        canRetry: false,
      };

      return newJob;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      setError(`Failed to create job: ${errorMessage}`);
      throw new Error(`Failed to create job: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const stopJob = useCallback(async (taskId: string): Promise<void> => {
    setError(null);
    try {
      await api.post(`/tasks/${taskId}/stop`);
      // Update job status locally if needed
      setJobs((prev) =>
        prev.map((job) =>
          job.id === taskId
            ? { ...job, status: "cancelled", canStop: false, canRetry: true }
            : job
        )
      );
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      setError(`Failed to stop job: ${errorMessage}`);
      throw new Error(`Failed to stop job: ${errorMessage}`);
    }
  }, []);

  const retryJob = useCallback(
    async (taskId: string): Promise<Job> => {
      setError(null);
      try {
        const originalJob = jobs.find((job) => job.id === taskId);
        if (!originalJob) {
          throw new Error("Job not found");
        }

        // Start a new task with the same session
        const taskResponse = await api.post("/run", {
          session_id: originalJob.sessionId,
        });

        const newJob: Job = {
          id: taskResponse.data.task_id,
          sessionId: originalJob.sessionId,
          status: "pending",
          createdAt: new Date(),
          canStop: true,
          canRetry: false,
        };

        return newJob;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";
        setError(`Failed to retry job: ${errorMessage}`);
        throw new Error(`Failed to retry job: ${errorMessage}`);
      }
    },
    [jobs]
  );

  const deleteJob = useCallback((taskId: string): void => {
    setJobs((prev) => prev.filter((job) => job.id !== taskId));
  }, []);

  return {
    jobs,
    templates,
    loading,
    error,
    activeJobs: jobs.filter(
      (job) => job.status === "pending" || job.status === "running"
    ),
    completedJobs: jobs.filter((job) => job.status === "completed"),
    failedJobs: jobs.filter((job) => job.status === "failed"),
    cancelledJobs: jobs.filter((job) => job.status === "cancelled"),
    getJob: (taskId: string) => jobs.find((job) => job.id === taskId),
    hasActiveJobs: jobs.some(
      (job) => job.status === "pending" || job.status === "running"
    ),
    createJob,
    stopJob,
    retryJob,
    deleteJob,
    createTemplate,
    deleteTemplate,
    clearError,
  };
}
