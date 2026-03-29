import { useState, useCallback } from 'react';
import { initUpload, uploadChunk, completeUpload } from '../api/videos';

interface UploadState {
  uploading: boolean;
  progress: number;
  error: string | null;
  videoId: string | null;
  jobId: string | null;
}

export function useVideoUpload() {
  const [state, setState] = useState<UploadState>({
    uploading: false,
    progress: 0,
    error: null,
    videoId: null,
    jobId: null,
  });

  const upload = useCallback(async (file: File) => {
    setState({ uploading: true, progress: 0, error: null, videoId: null, jobId: null });

    try {
      // Step 1: Init upload
      const { upload_id, chunk_size, total_chunks } = await initUpload(file.name, file.size);

      // Step 2: Upload chunks
      for (let i = 0; i < total_chunks; i++) {
        const start = i * chunk_size;
        const end = Math.min(start + chunk_size, file.size);
        const chunk = file.slice(start, end);

        await uploadChunk(upload_id, i, chunk);

        const progress = Math.round(((i + 1) / total_chunks) * 90);
        setState((prev) => ({ ...prev, progress }));
      }

      // Step 3: Complete upload
      const { video_id, job_id } = await completeUpload(upload_id);

      setState({
        uploading: false,
        progress: 100,
        error: null,
        videoId: video_id,
        jobId: job_id,
      });

      return { videoId: video_id, jobId: job_id };
    } catch (err: any) {
      const error = err.response?.data?.error || err.message || 'Upload failed';
      setState((prev) => ({ ...prev, uploading: false, error }));
      throw err;
    }
  }, []);

  return { ...state, upload };
}
