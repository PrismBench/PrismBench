import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export function usePolling(url: string, interval: number = 2000) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!url) return;

    const poll = async () => {
      try {
        const response = await api.get(url);
        setData(response.data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    };

    poll(); // Initial fetch
    const intervalId = setInterval(poll, interval);

    return () => clearInterval(intervalId);
  }, [url, interval]);

  return { data, loading, error };
}
