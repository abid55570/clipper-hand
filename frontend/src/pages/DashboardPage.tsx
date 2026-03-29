import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useVideoStore, useJobStore } from '../store';
import { formatTime } from '../components/video/TimestampInput';

export default function DashboardPage() {
  const { videos, loading, fetchVideos } = useVideoStore();
  const { jobs, fetchJobs } = useJobStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchVideos();
    fetchJobs();
  }, [fetchVideos, fetchJobs]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px' }}>Dashboard</h1>
        <Link to="/upload" className="btn btn-primary" style={{ textDecoration: 'none' }}>
          Upload Video
        </Link>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--accent)' }}>{videos.length}</div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Videos</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--success)' }}>
            {jobs.filter(j => j.status === 'completed').length}
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Completed Jobs</div>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: 700, color: 'var(--warning)' }}>
            {jobs.filter(j => j.status === 'running' || j.status === 'pending').length}
          </div>
          <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Active Jobs</div>
        </div>
      </div>

      {/* Videos list */}
      <h2 style={{ fontSize: '18px', marginBottom: '12px' }}>Recent Videos</h2>
      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
      ) : videos.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>No videos uploaded yet.</p>
          <Link to="/upload" className="btn btn-primary" style={{ textDecoration: 'none' }}>Upload Your First Video</Link>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Duration</th>
              <th>Resolution</th>
              <th>Size</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {videos.map((video) => (
              <tr key={video.id}>
                <td style={{ fontWeight: 500 }}>{video.original_name}</td>
                <td>{video.duration_secs ? formatTime(video.duration_secs) : '-'}</td>
                <td>{video.width && video.height ? `${video.width}x${video.height}` : '-'}</td>
                <td>{(video.file_size_bytes / 1024 / 1024).toFixed(1)} MB</td>
                <td><span className={`badge badge-${video.status}`}>{video.status}</span></td>
                <td>
                  <button className="btn btn-primary" style={{ fontSize: '12px', padding: '4px 10px' }}
                          onClick={() => navigate(`/editor/${video.id}`)} disabled={video.status !== 'ready'}>
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
