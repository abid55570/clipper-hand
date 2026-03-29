import type { Clip } from '../../types';
import { getClipDownloadUrl } from '../../api/clips';
import { formatTime } from '../video/TimestampInput';

interface Props {
  clip: Clip;
  onDownload?: () => void;
  onDelete?: () => void;
  onExport?: () => void;
}

export default function ClipCard({ clip, onDownload, onDelete, onExport }: Props) {
  const statusClass = `badge badge-${clip.status}`;

  return (
    <div className="card" style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <strong>{clip.label || 'Untitled Clip'}</strong>
          <span className={statusClass}>{clip.status}</span>
        </div>
        <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
          {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
          {clip.duration_secs && ` (${clip.duration_secs.toFixed(1)}s)`}
          {clip.file_size_bytes && ` | ${(clip.file_size_bytes / 1024 / 1024).toFixed(1)} MB`}
        </span>
      </div>
      <div style={{ display: 'flex', gap: '6px' }}>
        {clip.status === 'ready' && (
          <>
            <a href={getClipDownloadUrl(clip.id)} className="btn btn-primary" style={{ textDecoration: 'none', fontSize: '13px' }}>
              Download
            </a>
            <button className="btn btn-outline" onClick={onExport} style={{ fontSize: '13px' }}>
              Export
            </button>
          </>
        )}
        <button className="btn btn-danger" onClick={onDelete} style={{ fontSize: '13px' }}>
          Delete
        </button>
      </div>
    </div>
  );
}
