import { useEffect, useState } from "react";
import {
  pollServiceHealth,
  SERVICES,
  ServiceHealth,
  ServiceConfig,
} from "@/lib/health";

export function useServiceHealth(services: ServiceConfig[] = SERVICES) {
  const [statuses, setStatuses] = useState<ServiceHealth[]>(
    services.map((s) => ({ ...s, status: "loading" as const }))
  );

  useEffect(() => {
    let cancelled = false;
    async function pollAll() {
      const results = await pollServiceHealth(services);
      if (!cancelled) setStatuses(results);
    }
    pollAll();
    const interval = setInterval(pollAll, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [services]);

  return statuses;
}
