import React, { useState } from 'react';
import type { ExportConfig } from '../../types';
import AspectRatioSelector from './AspectRatioSelector';

interface Props {
  onExport: (config: ExportConfig) => void;
  loading?: boolean;
}

export default function ExportPanel({ onExport, loading }: Props) {
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [platform, setPlatform] = useState('');
  const [zoom, setZoom] = useState(false);
  const [jumpCut, setJumpCut] = useState(false);
  const [textAnimation, setTextAnimation] = useState('');
  const [textContent, setTextContent] = useState('');

  const handleExport = () => {
    const config: ExportConfig = {
      aspect_ratio: aspectRatio,
      platform: platform || undefined,
      effects: {
        zoom,
        jump_cut: jumpCut,
        text_animation: textAnimation || undefined,
        text_content: textContent || undefined,
      },
    };
    onExport(config);
  };

  return (
    <div className="card">
      <h4 style={{ marginBottom: '16px' }}>Export Settings</h4>

      <AspectRatioSelector value={aspectRatio} onChange={setAspectRatio} />

      <div style={{ marginTop: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Platform Preset</label>
        <select className="input" value={platform} onChange={(e) => {
          setPlatform(e.target.value);
          if (e.target.value === 'tiktok' || e.target.value === 'instagram' || e.target.value === 'youtube_shorts') {
            setAspectRatio('9:16');
          } else if (e.target.value === 'twitter') {
            setAspectRatio('16:9');
          }
        }}>
          <option value="">Custom</option>
          <option value="tiktok">TikTok</option>
          <option value="instagram">Instagram Reels</option>
          <option value="youtube_shorts">YouTube Shorts</option>
          <option value="twitter">Twitter/X</option>
        </select>
      </div>

      <div style={{ marginTop: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px', display: 'block' }}>Effects</label>
        <label style={{ display: 'flex', gap: '6px', alignItems: 'center', fontSize: '13px', marginBottom: '6px' }}>
          <input type="checkbox" checked={zoom} onChange={(e) => setZoom(e.target.checked)} />
          Zoom-in effect
        </label>
        <label style={{ display: 'flex', gap: '6px', alignItems: 'center', fontSize: '13px', marginBottom: '6px' }}>
          <input type="checkbox" checked={jumpCut} onChange={(e) => setJumpCut(e.target.checked)} />
          Jump cuts (remove silence)
        </label>
      </div>

      <div style={{ marginTop: '12px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Text Animation</label>
        <select className="input" value={textAnimation} onChange={(e) => setTextAnimation(e.target.value)}>
          <option value="">None</option>
          <option value="fade">Fade</option>
          <option value="pop">Pop</option>
          <option value="slide">Slide</option>
          <option value="typewriter">Typewriter</option>
        </select>
        {textAnimation && (
          <input className="input" style={{ marginTop: '8px' }} placeholder="Text to overlay..."
                 value={textContent} onChange={(e) => setTextContent(e.target.value)} />
        )}
      </div>

      <button className="btn btn-primary" style={{ width: '100%', marginTop: '20px' }}
              onClick={handleExport} disabled={loading}>
        {loading ? 'Exporting...' : 'Export Video'}
      </button>
    </div>
  );
}
