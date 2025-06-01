import { useState, useEffect, useCallback, useRef } from "react";

// Custom hook for optimized job polling
export function useJobPolling(interval = 2000) {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pollingEnabled, setPollingEnabled] = useState(true);
  const intervalRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Helper function to fetch tree data for a session
  const fetchTreeData = useCallback(async (sessionId, signal) => {
    try {
      const response = await fetch(`/api/tree/${sessionId}`, {
        signal,
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        console.warn(
          `Failed to fetch tree data for session ${sessionId}: ${response.status}`
        );
        return null;
      }

      return await response.json();
    } catch (err) {
      if (err.name !== "AbortError") {
        console.warn(`Error fetching tree data for session ${sessionId}:`, err);
      }
      return null;
    }
  }, []);

  // Optimized fetch function with abort controller
  const fetchJobs = useCallback(async () => {
    // Abort previous request if it's still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("/api/status", {
        signal: abortControllerRef.current.signal,
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Transform the status response into jobs array format
      let jobsArray = [];

      if (data && typeof data === "object") {
        if (Array.isArray(data)) {
          // If it's already an array, use it
          jobsArray = data;
        } else if (data.message === "No tasks to report") {
          // Empty state - no jobs
          jobsArray = [];
        } else if (data.tasks || data.jobs) {
          // If the response has a tasks or jobs property, use that
          jobsArray = data.tasks || data.jobs || [];
        } else {
          // Convert the status data to job array format
          jobsArray = Object.keys(data).map((taskId) => {
            const taskData = data[taskId];
            // Determine overall status from phases
            let overallStatus = "unknown";
            if (taskData.phases) {
              const phaseStatuses = Object.values(taskData.phases).map(
                (p) => p.status
              );
              if (phaseStatuses.some((s) => s === "running")) {
                overallStatus = "running";
              } else if (phaseStatuses.some((s) => s === "cancelled")) {
                overallStatus = "cancelled";
              } else if (phaseStatuses.every((s) => s === "completed")) {
                overallStatus = "completed";
              } else if (phaseStatuses.some((s) => s === "error")) {
                overallStatus = "error";
              } else {
                overallStatus = "pending";
              }
            }

            return {
              sessionId: taskData.session_id || taskId,
              taskId: taskId,
              status: overallStatus,
              jobName: taskData.name || `Job ${taskId.slice(0, 8)}`,
              treeData: null, // Will be fetched separately
              statusInfo: taskData || {},
            };
          });
        }
      }

      // Fetch tree data for each job
      if (jobsArray.length > 0) {
        const jobsWithTreeData = await Promise.all(
          jobsArray.map(async (job) => {
            if (job.sessionId && job.sessionId !== job.taskId) {
              const treeData = await fetchTreeData(
                job.sessionId,
                abortControllerRef.current.signal
              );
              return { ...job, treeData };
            }
            return job;
          })
        );

        setJobs((prevJobs) => {
          // Only update if data has actually changed
          const hasChanged =
            JSON.stringify(prevJobs) !== JSON.stringify(jobsWithTreeData);
          return hasChanged ? jobsWithTreeData : prevJobs;
        });
      } else {
        setJobs((prevJobs) => {
          // Only update if data has actually changed
          const hasChanged =
            JSON.stringify(prevJobs) !== JSON.stringify(jobsArray);
          return hasChanged ? jobsArray : prevJobs;
        });
      }

      setError(null);
    } catch (err) {
      // Ignore abort errors
      if (err.name !== "AbortError") {
        console.error("Error fetching jobs:", err);
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, [fetchTreeData]);

  // Start polling
  const startPolling = useCallback(() => {
    if (intervalRef.current) return; // Already polling

    setPollingEnabled(true);
    fetchJobs(); // Initial fetch

    intervalRef.current = setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchJobs();
      }
    }, interval);
  }, [fetchJobs, interval]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setPollingEnabled(false);
  }, []);

  // Refresh jobs manually
  const refreshJobs = useCallback(() => {
    setIsLoading(true);
    fetchJobs();
  }, [fetchJobs]);

  // Job actions
  const performJobAction = useCallback(
    async (action, jobId) => {
      try {
        // Handle supported actions
        if (action === "refresh") {
          refreshJobs();
          return { success: true };
        }

        if (action === "stop" || action === "cancel") {
          console.log(`Attempting to stop job: ${jobId}`);

          // Find the job to get the correct task ID
          const job = jobs.find(
            (j) => j.sessionId === jobId || j.taskId === jobId
          );
          const taskId = job?.taskId || jobId;

          console.log(`Found job:`, job);
          console.log(`Using taskId: ${taskId}`);

          try {
            const response = await fetch(`/api/stop/${taskId}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
            });

            console.log(`Stop API response status: ${response.status}`);

            if (!response.ok) {
              const errorData = await response.json().catch(() => ({}));
              const errorMessage =
                errorData.detail || `HTTP error! status: ${response.status}`;
              console.error(`Stop API error:`, errorMessage);
              throw new Error(errorMessage);
            }

            const result = await response.json();
            console.log(`Stop API result:`, result);

            // Trigger a refresh to update the job status
            setTimeout(refreshJobs, 500);

            return {
              success: true,
              message: result.message || "Job stopped successfully",
            };
          } catch (fetchError) {
            console.error(`Fetch error for stop action:`, fetchError);
            throw new Error(`Failed to stop job: ${fetchError.message}`);
          }
        }

        // For other actions, show that they're not yet implemented
        console.log(
          `Action '${action}' requested for job ${jobId} - not supported`
        );
        return {
          success: false,
          error: `${action} action is not supported. Only 'refresh' and 'stop' actions are available.`,
        };
      } catch (err) {
        console.error(`Error performing ${action} on job ${jobId}:`, err);
        setError(err.message);
        return { success: false, error: err.message };
      }
    },
    [refreshJobs, jobs]
  );

  // Initialize polling on mount
  useEffect(() => {
    startPolling();

    // Handle visibility change for performance
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && pollingEnabled) {
        startPolling();
      } else {
        stopPolling();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);

      // Cleanup abort controller
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [startPolling, stopPolling, pollingEnabled]);

  return {
    jobs,
    isLoading,
    error,
    pollingEnabled,
    startPolling,
    stopPolling,
    refreshJobs,
    performJobAction,
  };
}
