import type { ContentResult } from '../../types';

interface Props {
  content: ContentResult | null;
  loading: boolean;
  onGenerate: () => void;
}

export default function ContentGenerator({ content, loading, onGenerate }: Props) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h4>Auto-Generated Content</h4>
        <button className="btn btn-primary" onClick={onGenerate} disabled={loading}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>
      {content && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Title</label>
            <p style={{ fontWeight: 500 }}>{content.title}</p>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Description</label>
            <p>{content.description}</p>
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Hashtags</label>
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '4px' }}>
              {content.hashtags.map((tag, i) => (
                <span key={i} style={{
                  background: 'var(--accent)',
                  color: 'white',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                }}>
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
