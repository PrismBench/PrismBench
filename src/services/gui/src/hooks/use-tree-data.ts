import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export interface TreeNode {
  id: string;
  difficulty: string;
  concepts: string[];
  challenge_description: string;
  problem_statement: any;
  solution_code: any;
  test_cases: any;
  problem_fixer: any;
  depth: number;
  visits: number;
  successes: number;
  failures: number;
  score: number;
  phase: number;
  run_results: any[];
  value: number;
  children: string[];
  parents: string[];
}

export interface TreeData {
  nodes: TreeNode[];
  concepts: string[];
  difficulties: string[];
}

export interface TreeStats {
  totalNodes: number;
  maxDepth: number;
  phaseDistribution: Record<number, number>;
  avgNodeValue: number;
  conceptDistribution: Record<string, number>;
  conceptCombinations: Record<string, number>;
  difficultyDistribution: Record<string, number>;
}

interface UseTreeDataOptions {
  enablePolling?: boolean;
  pollingInterval?: number;
  jobStatus?: string; // 'running', 'completed', etc.
}


export function useTreeData(
  sessionId: string | null,
  options: UseTreeDataOptions = {}
) {
  const { enablePolling = false, pollingInterval = 5000, jobStatus } = options;

  const [data, setData] = useState<TreeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const { toast } = useToast();

  const fetchTreeData = useCallback(
    async (showToastOnError = true) => {
      if (!sessionId) {
        setData(null);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await api.get(`/tree/${sessionId}`);
        setData(response.data);
        setLastUpdate(new Date());
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.detail || "Failed to fetch tree data";
        setError(errorMessage);

        // Only show toast for errors on manual refresh or initial load
        if (showToastOnError) {
          toast({
            title: "Error",
            description: errorMessage,
            variant: "destructive",
          });
        }
      } finally {
        setLoading(false);
      }
    },
    [sessionId, toast]
  );

  // Initial fetch and manual refetch
  useEffect(() => {
    if (sessionId) {
      fetchTreeData(true);
    }
  }, [sessionId, fetchTreeData]);

  // Polling effect
  useEffect(() => {
    if (
      !enablePolling ||
      !sessionId ||
      jobStatus === "completed" ||
      jobStatus === "failed"
    ) {
      return;
    }

    // Start polling immediately, then continue at intervals
    const pollInterval = setInterval(() => {
      fetchTreeData(false); // Don't show toast on polling errors
    }, pollingInterval);

    // Initial poll right away for immediate feedback
    fetchTreeData(false);

    return () => clearInterval(pollInterval);
  }, [enablePolling, sessionId, pollingInterval, jobStatus, fetchTreeData]);

  const refetch = () => {
    if (sessionId) {
      fetchTreeData(true);
    }
  };

  // Calculate tree statistics
  const stats: TreeStats | null = data
    ? {
        totalNodes: data.nodes.length,
        maxDepth: Math.max(...data.nodes.map((n) => n.depth), 0),
        phaseDistribution: data.nodes.reduce((acc, node) => {
          acc[node.phase] = (acc[node.phase] || 0) + 1;
          return acc;
        }, {} as Record<number, number>),
        avgNodeValue:
          data.nodes.length > 0
            ? data.nodes.reduce((sum, node) => sum + node.value, 0) /
              data.nodes.length
            : 0,
        conceptDistribution: data.nodes.reduce((acc, node) => {
          node.concepts.forEach((concept) => {
            acc[concept] = (acc[concept] || 0) + 1;
          });
          return acc;
        }, {} as Record<string, number>),
        conceptCombinations: data.nodes.reduce((acc, node) => {
          // Create a sorted combination string for consistent keys
          if (node.concepts.length > 0) {
            const combination = node.concepts.sort().join(" + ");
            acc[combination] = (acc[combination] || 0) + 1;
          }
          return acc;
        }, {} as Record<string, number>),
        difficultyDistribution: data.nodes.reduce((acc, node) => {
          acc[node.difficulty] = (acc[node.difficulty] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
      }
    : null;

  return {
    data,
    stats,
    loading,
    error,
    lastUpdate,
    refetch,
  };
}
