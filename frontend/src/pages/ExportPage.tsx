import { useState } from 'react';
import { useParams } from 'react-router-dom';
import ExportPanel from '../components/export/ExportPanel';
import JobStatus from '../components/common/JobStatus';
import { useJobPolling } from '../hooks/useJobPolling';
import apiClient from '../api/client';
import type { ExportConfig } from '../types';

export default function ExportPage() {
  const { clipId } = useParams<{ clipId: string }>();
  const [jobId, setJobId] = useState<string | null>(null);
  const [exportId, setExportId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { job } = useJobPolling(jobId);

  const handleExport = async (config: ExportConfig) => {
    if (!clipId) return;
    setLoading(true);
    try {
      const { data } = await apiClient.post(`/exports/clips/${clipId}/export`, config);
      setJobId(data.job_id);
      setExportId(data.export_id);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>Export Clip</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <ExportPanel onExport={handleExport} loading={loading} />

        <div>
          {job && <JobStatus job={job} />}

          {job?.status === 'completed' && exportId && (
            <div className="card" style={{ textAlign: 'center', marginTop: '16px' }}>
              <p style={{ color: 'var(--success)', marginBottom: '12px' }}>Export complete!</p>
              <a
                href={`${API_URL}/api/v1/exports/${exportId}/download`}
                className="btn btn-success"
                style={{ textDecoration: 'none', display: 'inline-block' }}
              >
                Download Exported Video
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
