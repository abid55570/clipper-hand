import type { Highlight, ClipTimestamp } from '../../types';
import { formatTime } from '../video/TimestampInput';

interface Props {
  highlights: Highlight[];
  onAccept: (ts: ClipTimestamp) => void;
  onAcceptAll: () => void;
}

export default function HighlightSuggestions({ highlights, onAccept, onAcceptAll }: Props) {
  if (highlights.length === 0) {
    return (
      <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '20px' }}>
        No highlights detected yet.
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h4>{highlights.length} Highlights Found</h4>
        <button className="btn btn-primary" onClick={onAcceptAll}>Accept All</button>
      </div>
      {highlights.map((h) => (
        <div key={h.id} className="card" style={{ padding: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <strong>{formatTime(h.start_time)} - {formatTime(h.end_time)}</strong>
              {h.score && (
                <span style={{
                  background: `hsl(${h.score * 120}, 70%, 45%)`,
                  color: 'white',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  fontSize: '11px',
                }}>
                  {(h.score * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
              {h.reason} ({h.source})
            </p>
          </div>
          <button
            className="btn btn-success"
            style={{ fontSize: '13px' }}
            onClick={() => onAccept({
              start: h.start_time,
              end: h.end_time,
              label: `Highlight (${h.source})`,
            })}
          >
            Accept
          </button>
        </div>
      ))}
    </div>
  );
}
