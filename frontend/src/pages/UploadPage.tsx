import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadZone from '../components/upload/UploadZone';
import UploadProgress from '../components/upload/UploadProgress';
import JobStatus from '../components/common/JobStatus';
import { useVideoUpload } from '../hooks/useVideoUpload';
import { useJobPolling } from '../hooks/useJobPolling';

export default function UploadPage() {
  const navigate = useNavigate();
  const { uploading, progress, error, videoId, jobId, upload } = useVideoUpload();
  const { job } = useJobPolling(jobId);
  const [filename, setFilename] = useState('');

  const handleFileSelect = async (file: File) => {
    setFilename(file.name);
    try {
      const result = await upload(file);
      // Job polling will track metadata extraction
    } catch {
      // Error displayed via state
    }
  };

  // Navigate to editor when metadata extraction completes
  if (job?.status === 'completed' && videoId) {
    setTimeout(() => navigate(`/editor/${videoId}`), 1000);
  }

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>Upload Video</h1>

      <UploadZone onFileSelect={handleFileSelect} disabled={uploading} />

      {(uploading || filename) && (
        <div style={{ marginTop: '20px' }}>
          <UploadProgress progress={progress} filename={filename} error={error} />
        </div>
      )}

      {jobId && (
        <div style={{ marginTop: '12px' }}>
          <JobStatus job={job} loading={!job} />
          {job?.status === 'completed' && (
            <p style={{ color: 'var(--success)', marginTop: '8px' }}>
              Video ready! Redirecting to editor...
            </p>
          )}
        </div>
      )}
    </div>
  );
}
