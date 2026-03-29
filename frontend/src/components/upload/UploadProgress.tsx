interface Props {
  progress: number;
  filename: string;
  error?: string | null;
}

export default function UploadProgress({ progress, filename, error }: Props) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span style={{ fontWeight: 500 }}>{filename}</span>
        <span style={{ color: error ? 'var(--error)' : 'var(--text-secondary)' }}>
          {error ? 'Failed' : `${progress}%`}
        </span>
      </div>
      <div className="progress-bar">
        <div
          className="progress-bar-fill"
          style={{
            width: `${progress}%`,
            background: error ? 'var(--error)' : 'var(--accent)',
          }}
        />
      </div>
      {error && (
        <p style={{ color: 'var(--error)', fontSize: '13px', marginTop: '8px' }}>{error}</p>
      )}
    </div>
  );
}
