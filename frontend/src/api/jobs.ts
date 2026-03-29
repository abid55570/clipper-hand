import apiClient from './client';
import type { Job } from '../types';

export async function getJob(jobId: string) {
  const { data } = await apiClient.get(`/jobs/${jobId}`);
  return data as Job;
}

export async function listJobs(status?: string) {
  const params = status ? { status } : {};
  const { data } = await apiClient.get('/jobs', { params });
  return data as { jobs: Job[]; total: number };
}

export async function cancelJob(jobId: string) {
  const { data } = await apiClient.post(`/jobs/${jobId}/cancel`);
  return data;
}

export async function retryJob(jobId: string) {
  const { data } = await apiClient.post(`/jobs/${jobId}/retry`);
  return data;
}
