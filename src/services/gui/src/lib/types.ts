export interface JobProgress {
  taskId: string;
  status: "pending" | "running" | "completed" | "failed";
  currentPhase?: string;
  progress?: {
    phase: string;
    iteration: number;
    maxIterations: number;
    nodesEvaluated: number;
  };
  error?: string;
  phases?: Record<string, any>;
}

export interface JobFormData {
  sessionId: string;
  experimentConfig?: string;
  phaseSequence?: string[];
  customParams?: Record<string, any>;
}

export interface Job {
  id: string;
  sessionId: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  progress?: JobProgress;
  canRetry?: boolean;
  canStop?: boolean;
}

export interface JobTemplate {
  id: string;
  name: string;
  description: string;
  config: JobFormData;
  createdAt: Date;
  isDefault?: boolean;
}

