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
    url: "http://localhost:8000/health",
  },
  {
    name: "node-env",
    label: "Environment Service",
    url: "http://localhost:8001/health",
  },
  {
    name: "search",
    label: "Search Service",
    url: "http://localhost:8002/health",
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
