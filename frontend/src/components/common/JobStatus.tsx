import type { Job } from '../../types';

interface Props {
  job: Job | null;
  loading?: boolean;
}

export default function JobStatus({ job, loading }: Props) {
  if (!job && !loading) return null;

  if (loading && !job) {
    return <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Loading job status...</div>;
  }

  if (!job) return null;

  return (
    <div className="card" style={{ padding: '12px 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <span style={{ fontWeight: 500 }}>{job.job_type.replace(/_/g, ' ')}</span>
        <span className={`badge badge-${job.status}`}>{job.status}</span>
      </div>
      {(job.status === 'running' || job.status === 'pending') && (
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{ width: `${job.progress_pct}%` }} />
        </div>
      )}
      {job.error_message && (
        <p style={{ color: 'var(--error)', fontSize: '13px', marginTop: '8px' }}>{job.error_message}</p>
      )}
    </div>
  );
}
