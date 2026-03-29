import type { HookItem } from '../../types';

interface Props {
  hooks: HookItem[];
  loading: boolean;
  onGenerate: () => void;
}

export default function HookGenerator({ hooks, loading, onGenerate }: Props) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h4>Hook Generator</h4>
        <button className="btn btn-primary" onClick={onGenerate} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Hooks'}
        </button>
      </div>
      {hooks.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {hooks.map((hook, i) => (
            <div key={i} style={{
              padding: '12px',
              background: 'var(--bg-card)',
              borderRadius: '6px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <span style={{ fontWeight: hook.style === 'bold' ? 700 : 400, fontStyle: hook.style === 'fade' ? 'italic' : 'normal' }}>
                "{hook.text}"
              </span>
              <span className="badge badge-ready" style={{ fontSize: '11px' }}>{hook.style}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
