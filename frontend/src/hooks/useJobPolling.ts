import { useState, useEffect, useCallback, useRef } from 'react';
import { getJob } from '../api/jobs';
import type { Job } from '../types';

export function useJobPolling(jobId: string | null, interval = 2000) {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!jobId) return;

    setLoading(true);

    const poll = async () => {
      try {
        const data = await getJob(jobId);
        setJob(data);
        setLoading(false);

        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          stopPolling();
        }
      } catch {
        setLoading(false);
        stopPolling();
      }
    };

    poll();
    intervalRef.current = setInterval(poll, interval);

    return stopPolling;
  }, [jobId, interval, stopPolling]);

  return { job, loading, stopPolling };
}
