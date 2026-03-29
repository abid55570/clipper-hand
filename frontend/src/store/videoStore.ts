import { create } from 'zustand';
import type { Video } from '../types';
import { listVideos, getVideo } from '../api/videos';

interface VideoStore {
  videos: Video[];
  currentVideo: Video | null;
  loading: boolean;
  error: string | null;
  fetchVideos: () => Promise<void>;
  fetchVideo: (id: string) => Promise<void>;
  setCurrentVideo: (video: Video | null) => void;
}

export const useVideoStore = create<VideoStore>((set) => ({
  videos: [],
  currentVideo: null,
  loading: false,
  error: null,

  fetchVideos: async () => {
    set({ loading: true, error: null });
    try {
      const { videos } = await listVideos();
      set({ videos, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  fetchVideo: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const video = await getVideo(id);
      set({ currentVideo: video, loading: false });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  setCurrentVideo: (video) => set({ currentVideo: video }),
}));
