import type { Caption, CaptionSegment } from '../../types';

interface Props {
  caption: Caption;
}

export default function CaptionEditor({ caption }: Props) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h4>Transcript</h4>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className={`badge badge-${caption.status}`}>{caption.status}</span>
          {caption.language && <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Language: {caption.language}</span>}
        </div>
      </div>

      {caption.segments.length > 0 ? (
        <div style={{ maxHeight: '400px', overflow: 'auto' }}>
          {caption.segments.map((seg) => (
            <div key={seg.id} style={{
              padding: '8px 12px',
              borderBottom: '1px solid var(--border)',
              display: 'flex',
              gap: '12px',
            }}>
              <span style={{
                color: 'var(--accent)',
                fontSize: '12px',
                minWidth: '80px',
                fontFamily: 'monospace',
              }}>
                {seg.start_time.toFixed(1)}s
              </span>
              <span>{seg.text}</span>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ color: 'var(--text-secondary)' }}>
          {caption.status === 'pending' ? 'Transcription in progress...' : 'No segments available.'}
        </p>
      )}
    </div>
  );
}
