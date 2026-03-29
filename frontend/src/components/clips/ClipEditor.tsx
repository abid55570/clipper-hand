import React, { useState } from 'react';
import type { Clip } from '../../types';
import { useClipEditor } from '../../hooks/useClipEditor';

interface Props {
  clip: Clip;
  onTrimComplete?: () => void;
}

export default function ClipEditor({ clip, onTrimComplete }: Props) {
  const [newStart, setNewStart] = useState(clip.start_time);
  const [newEnd, setNewEnd] = useState(clip.end_time);
  const { handleTrim, trimming, error } = useClipEditor();

  const onTrim = async () => {
    await handleTrim(clip.id, newStart, newEnd);
    onTrimComplete?.();
  };

  return (
    <div className="card">
      <h4 style={{ marginBottom: '12px' }}>Trim Clip: {clip.label}</h4>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'end' }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>New Start (s)</label>
          <input
            className="input"
            type="number"
            step="0.1"
            value={newStart}
            onChange={(e) => setNewStart(Number(e.target.value))}
            style={{ width: '120px' }}
          />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>New End (s)</label>
          <input
            className="input"
            type="number"
            step="0.1"
            value={newEnd}
            onChange={(e) => setNewEnd(Number(e.target.value))}
            style={{ width: '120px' }}
          />
        </div>
        <button className="btn btn-primary" onClick={onTrim} disabled={trimming}>
          {trimming ? 'Trimming...' : 'Trim'}
        </button>
      </div>
      {error && <p style={{ color: 'var(--error)', fontSize: '13px', marginTop: '8px' }}>{error}</p>}
    </div>
  );
}
