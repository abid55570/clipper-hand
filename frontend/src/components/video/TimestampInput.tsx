import React, { useState } from 'react';
import type { ClipTimestamp } from '../../types';

interface Props {
  onAdd: (ts: ClipTimestamp) => void;
  videoDuration?: number;
}

function parseTime(value: string): number {
  const parts = value.split(':').map(Number);
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return Number(value) || 0;
}

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
               : `${m}:${String(s).padStart(2, '0')}`;
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  gap: '10px',
  alignItems: 'end',
  marginBottom: '12px',
};

const fieldStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
};

export default function TimestampInput({ onAdd, videoDuration }: Props) {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [label, setLabel] = useState('');
  const [error, setError] = useState('');

  const handleAdd = () => {
    const startSec = parseTime(start);
    const endSec = parseTime(end);

    if (endSec <= startSec) {
      setError('End time must be after start time');
      return;
    }
    if (videoDuration && endSec > videoDuration) {
      setError(`End time exceeds video duration (${formatTime(videoDuration)})`);
      return;
    }

    setError('');
    onAdd({ start: startSec, end: endSec, label: label || `Clip ${Date.now()}` });
    setStart('');
    setEnd('');
    setLabel('');
  };

  return (
    <div>
      <div style={rowStyle}>
        <div style={fieldStyle}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Start (H:MM:SS)</label>
          <input className="input" value={start} onChange={(e) => setStart(e.target.value)}
                 placeholder="0:00" style={{ width: '120px' }} />
        </div>
        <div style={fieldStyle}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>End (H:MM:SS)</label>
          <input className="input" value={end} onChange={(e) => setEnd(e.target.value)}
                 placeholder="0:30" style={{ width: '120px' }} />
        </div>
        <div style={{ ...fieldStyle, flex: 1 }}>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Label</label>
          <input className="input" value={label} onChange={(e) => setLabel(e.target.value)}
                 placeholder="Clip name" />
        </div>
        <button className="btn btn-primary" onClick={handleAdd}>Add Clip</button>
      </div>
      {error && <p style={{ color: 'var(--error)', fontSize: '13px' }}>{error}</p>}
    </div>
  );
}

export { formatTime };
