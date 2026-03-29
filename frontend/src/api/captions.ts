import apiClient from './client';
import type { CaptionStyle } from '../types';

export async function transcribeVideo(videoId: string, modelSize: string = 'base') {
  const { data } = await apiClient.post(`/captions/videos/${videoId}/transcribe`, {
    model_size: modelSize,
  });
  return data as { job_id: string; caption_id: string };
}

export async function getVideoCaptions(videoId: string) {
  const { data } = await apiClient.get(`/captions/videos/${videoId}/captions`);
  return data;
}

export async function updateCaptionStyle(captionId: string, style: Partial<CaptionStyle>) {
  const { data } = await apiClient.put(`/captions/${captionId}/style`, style);
  return data;
}

export async function burnSubtitles(clipId: string, captionId: string, style?: Partial<CaptionStyle>) {
  const { data } = await apiClient.post(`/captions/clips/${clipId}/burn-subtitles`, {
    caption_id: captionId,
    style,
  });
  return data;
}
