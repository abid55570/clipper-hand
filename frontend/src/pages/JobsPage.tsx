import { useEffect } from 'react';
import { useJobStore } from '../store';
import { cancelJob, retryJob } from '../api/jobs';

export default function JobsPage() {
  const { jobs, loading, fetchJobs } = useJobStore();

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [fetchJobs]);

  const handleCancel = async (jobId: string) => {
    await cancelJob(jobId);
    fetchJobs();
  };

  const handleRetry = async (jobId: string) => {
    await retryJob(jobId);
    fetchJobs();
  };

  return (
    <div>
      <h1 style={{ fontSize: '24px', marginBottom: '24px' }}>Jobs</h1>

      {loading && jobs.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          No jobs yet.
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Status</th>
              <th>Progress</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td style={{ fontWeight: 500 }}>{job.job_type.replace(/_/g, ' ')}</td>
                <td><span className={`badge badge-${job.status}`}>{job.status}</span></td>
                <td>
                  {(job.status === 'running' || job.status === 'pending') ? (
                    <div className="progress-bar" style={{ width: '120px' }}>
                      <div className="progress-bar-fill" style={{ width: `${job.progress_pct}%` }} />
                    </div>
                  ) : (
                    `${job.progress_pct}%`
                  )}
                </td>
                <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  {new Date(job.created_at).toLocaleString()}
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {(job.status === 'running' || job.status === 'pending') && (
                      <button className="btn btn-danger" style={{ fontSize: '11px', padding: '2px 8px' }}
                              onClick={() => handleCancel(job.id)}>Cancel</button>
                    )}
                    {job.status === 'failed' && (
                      <button className="btn btn-outline" style={{ fontSize: '11px', padding: '2px 8px' }}
                              onClick={() => handleRetry(job.id)}>Retry</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
