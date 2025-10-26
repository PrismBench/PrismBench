import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { VariantProps } from "class-variance-authority";
import { badgeVariants } from "@/components/ui/badge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}


export const PHASE_COLORS = {
  1: "#fbbf24", // yellow
  2: "#10b981", // green
  3: "#3b82f6", // blue
} as const;

export type BadgeVariant = VariantProps<typeof badgeVariants>["variant"];

export function getStatusVariant(status: string): BadgeVariant {
  switch (status) {
    case "running":
      return "default";
    case "completed":
      return "secondary";
    case "failed":
      return "destructive";
    case "cancelled":
      return "outline";
    default:
      return "outline";
  }
}

