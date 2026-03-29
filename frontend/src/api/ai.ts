import apiClient from './client';
import type { Highlight, ContentResult, HookItem } from '../types';

export async function detectHighlights(videoId: string) {
  const { data } = await apiClient.post(`/ai/videos/${videoId}/detect-highlights`);
  return data as { job_id: string };
}

export async function getHighlights(videoId: string) {
  const { data } = await apiClient.get(`/ai/videos/${videoId}/highlights`);
  return data as { highlights: Highlight[]; video_id: string };
}

export async function generateContent(clipId: string) {
  const { data } = await apiClient.post(`/ai/clips/${clipId}/generate-content`);
  return data as { job_id: string };
}

export async function getGeneratedContent(clipId: string) {
  const { data } = await apiClient.get(`/ai/clips/${clipId}/content`);
  return data as ContentResult;
}

export async function generateHook(clipId: string) {
  const { data } = await apiClient.post(`/ai/clips/${clipId}/generate-hook`);
  return data as { hooks: HookItem[] };
}

export async function detectSpeakers(videoId: string) {
  const { data } = await apiClient.post(`/ai/videos/${videoId}/detect-speakers`);
  return data as { job_id: string };
}
