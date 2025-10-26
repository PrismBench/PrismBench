export type { TreeNode as NodeData, TreeData } from "@/hooks/use-tree-data";

// Detailed data for each attempt in a node's execution history
export interface NodeDataTrailData {
  problem_statement: string | null;
  test_cases: string | null;
  solution_code: string | null;
  success: boolean;
  output: string | null;
  tests_passed_num: number | null;
  tests_failed_num: number | null;
  tests_errored_num: number | null;
  fixed_by_problem_fixer: boolean | null;
  attempt_num: number | null;
  error_feedback: string | null;
}

// Phase helpers for color mapping in legend / nodes
export type Phase = 1 | 2 | 3;
export type PhaseColors = {
  [key in Phase]: { bg: string; border: string };
};
