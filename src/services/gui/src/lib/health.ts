const llmInterfaceUrl = process.env.NEXT_PUBLIC_LLM_INTERFACE_URL || "http://localhost:8000";
const nodeEnvUrl = process.env.NEXT_PUBLIC_NODE_ENV_URL || "http://localhost:8001";
const searchUrl = process.env.NEXT_PUBLIC_SEARCH_URL || "http://localhost:8002";

export interface ServiceConfig {
  name: string;
  label: string;
  url: string;
}

export type ServiceHealthStatus =
  | "healthy"
  | "unhealthy"
  | "unreachable"
  | "loading";

export interface ServiceHealth {
  name: string;
  label: string;
  status: ServiceHealthStatus;
}

export const SERVICES: ServiceConfig[] = [
  {
    name: "llm-interface",
    label: "LLM Interface",
    url: llmInterfaceUrl + "health",
  },
  {
    name: "node-env",
    label: "Environment Service",
    url: nodeEnvUrl + "health",
  },
  {
    name: "search",
    label: "Search Service",
    url: searchUrl + "health",
  },
];

export async function pollServiceHealth(
  services: ServiceConfig[]
): Promise<ServiceHealth[]> {
  return Promise.all(
    services.map(async (service) => {
      try {
        const res = await fetch(service.url, { cache: "no-store" });
        if (!res.ok) return { ...service, status: "unhealthy" as const };
        const data = await res.json().catch(() => ({}));
        if (
          data.status === "ok" ||
          data.status === "healthy" ||
          data === "ok" ||
          data === "healthy"
        )
          return { ...service, status: "healthy" as const };
        return { ...service, status: "unhealthy" as const };
      } catch {
        return { ...service, status: "unreachable" as const };
      }
    })
  );
}
