import apiClient from './client';
import type { Clip, ClipTimestamp } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function createClips(videoId: string, clips: ClipTimestamp[]) {
  const { data } = await apiClient.post(`/clips/video/${videoId}`, { clips });
  return data as { job_id: string; clip_ids: string[] };
}

export async function listClips(videoId?: string) {
  const params = videoId ? { video_id: videoId } : {};
  const { data } = await apiClient.get('/clips', { params });
  return data as { clips: Clip[]; total: number };
}

export async function getClip(clipId: string) {
  const { data } = await apiClient.get(`/clips/${clipId}`);
  return data as Clip;
}

export function getClipDownloadUrl(clipId: string) {
  return `${API_URL}/api/v1/clips/${clipId}/download`;
}

export async function trimClip(clipId: string, newStart: number, newEnd: number) {
  const { data } = await apiClient.post(`/clips/${clipId}/trim`, {
    new_start: newStart,
    new_end: newEnd,
  });
  return data;
}

export async function mergeClips(clipIds: string[], label?: string) {
  const { data } = await apiClient.post('/clips/merge', { clip_ids: clipIds, label });
  return data;
}

export async function deleteClip(clipId: string) {
  await apiClient.delete(`/clips/${clipId}`);
}
