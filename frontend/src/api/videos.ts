import apiClient from './client';
import type { Video } from '../types';

export async function initUpload(filename: string, fileSize: number) {
  const { data } = await apiClient.post('/videos/upload/init', {
    filename,
    file_size: fileSize,
    content_type: 'video/mp4',
  });
  return data as { upload_id: string; chunk_size: number; total_chunks: number };
}

export async function uploadChunk(uploadId: string, chunkIndex: number, chunk: Blob) {
  const formData = new FormData();
  formData.append('file', chunk);
  const { data } = await apiClient.post(
    `/videos/upload/chunk/${uploadId}?chunk_index=${chunkIndex}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data;
}

export async function completeUpload(uploadId: string) {
  const { data } = await apiClient.post(`/videos/upload/complete/${uploadId}`);
  return data as { video_id: string; job_id: string };
}

export async function listVideos() {
  const { data } = await apiClient.get('/videos');
  return data as { videos: Video[]; total: number };
}

export async function getVideo(videoId: string) {
  const { data } = await apiClient.get(`/videos/${videoId}`);
  return data as Video;
}

export async function deleteVideo(videoId: string) {
  await apiClient.delete(`/videos/${videoId}`);
}
