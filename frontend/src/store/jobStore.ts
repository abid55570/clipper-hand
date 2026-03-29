import { create } from 'zustand';
import type { Job } from '../types';
import { listJobs, getJob } from '../api/jobs';

interface JobStore {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  fetchJobs: (status?: string) => Promise<void>;
  pollJob: (jobId: string, onComplete?: (job: Job) => void) => void;
  stopPolling: () => void;
  _intervalId: ReturnType<typeof setInterval> | null;
}

export const useJobStore = create<JobStore>((set, get) => ({
  jobs: [],
  loading: false,
  error: null,
  _intervalId: null,

  fetchJobs: async (status?: string) => {
    set({ loading: true, error: null });
    try {
      const { jobs } = await listJobs(status);
      set({ jobs, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  pollJob: (jobId: string, onComplete?: (job: Job) => void) => {
    const { stopPolling } = get();
    stopPolling();

    const intervalId = setInterval(async () => {
      try {
        const job = await getJob(jobId);
        set((state) => ({
          jobs: state.jobs.map((j) => (j.id === jobId ? job : j)),
        }));
        if (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') {
          clearInterval(intervalId);
          set({ _intervalId: null });
          onComplete?.(job);
        }
      } catch {
        clearInterval(intervalId);
        set({ _intervalId: null });
      }
    }, 2000);

    set({ _intervalId: intervalId });
  },

  stopPolling: () => {
    const { _intervalId } = get();
    if (_intervalId) {
      clearInterval(_intervalId);
      set({ _intervalId: null });
    }
  },
}));
