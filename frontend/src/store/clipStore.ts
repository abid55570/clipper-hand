import { create } from 'zustand';
import type { Clip, ClipTimestamp } from '../types';
import { listClips, createClips } from '../api/clips';

interface ClipStore {
  clips: Clip[];
  loading: boolean;
  error: string | null;
  timestamps: ClipTimestamp[];
  fetchClips: (videoId?: string) => Promise<void>;
  addTimestamp: (ts: ClipTimestamp) => void;
  removeTimestamp: (index: number) => void;
  clearTimestamps: () => void;
  submitClips: (videoId: string) => Promise<{ job_id: string; clip_ids: string[] }>;
}

export const useClipStore = create<ClipStore>((set, get) => ({
  clips: [],
  loading: false,
  error: null,
  timestamps: [],

  fetchClips: async (videoId?: string) => {
    set({ loading: true, error: null });
    try {
      const { clips } = await listClips(videoId);
      set({ clips, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  addTimestamp: (ts) => set((state) => ({ timestamps: [...state.timestamps, ts] })),
  removeTimestamp: (index) =>
    set((state) => ({ timestamps: state.timestamps.filter((_, i) => i !== index) })),
  clearTimestamps: () => set({ timestamps: [] }),

  submitClips: async (videoId: string) => {
    const { timestamps } = get();
    set({ loading: true, error: null });
    try {
      const result = await createClips(videoId, timestamps);
      set({ loading: false, timestamps: [] });
      return result;
    } catch (err: any) {
      set({ error: err.message, loading: false });
      throw err;
    }
  },
}));
