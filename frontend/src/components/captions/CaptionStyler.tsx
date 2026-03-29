import React, { useState } from 'react';
import type { CaptionStyle } from '../../types';

interface Props {
  onStyleChange: (style: CaptionStyle) => void;
  initialStyle?: Partial<CaptionStyle>;
}

const defaultStyle: CaptionStyle = {
  font_family: 'Arial',
  font_size: 48,
  primary_color: '#FFFFFF',
  outline_color: '#000000',
  highlight_color: '#FFFF00',
  highlight_words: [],
  position: 'bottom',
  bold: false,
  animation_type: 'none',
};

export default function CaptionStyler({ onStyleChange, initialStyle }: Props) {
  const [style, setStyle] = useState<CaptionStyle>({ ...defaultStyle, ...initialStyle });
  const [highlightInput, setHighlightInput] = useState('');

  const update = (field: string, value: any) => {
    const newStyle = { ...style, [field]: value };
    setStyle(newStyle);
    onStyleChange(newStyle);
  };

  const addHighlightWord = () => {
    if (highlightInput.trim()) {
      update('highlight_words', [...style.highlight_words, highlightInput.trim()]);
      setHighlightInput('');
    }
  };

  return (
    <div className="card">
      <h4 style={{ marginBottom: '16px' }}>Caption Style</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Font</label>
          <select className="input" value={style.font_family} onChange={(e) => update('font_family', e.target.value)}>
            <option>Arial</option>
            <option>Helvetica</option>
            <option>Impact</option>
            <option>Verdana</option>
            <option>Comic Sans MS</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Size</label>
          <input className="input" type="number" min="8" max="200" value={style.font_size}
                 onChange={(e) => update('font_size', Number(e.target.value))} />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Text Color</label>
          <input type="color" value={style.primary_color} onChange={(e) => update('primary_color', e.target.value)}
                 style={{ width: '100%', height: '36px', cursor: 'pointer' }} />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Highlight Color</label>
          <input type="color" value={style.highlight_color} onChange={(e) => update('highlight_color', e.target.value)}
                 style={{ width: '100%', height: '36px', cursor: 'pointer' }} />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Position</label>
          <select className="input" value={style.position} onChange={(e) => update('position', e.target.value)}>
            <option value="top">Top</option>
            <option value="center">Center</option>
            <option value="bottom">Bottom</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Animation</label>
          <select className="input" value={style.animation_type} onChange={(e) => update('animation_type', e.target.value)}>
            <option value="none">None</option>
            <option value="word_by_word">Word by Word</option>
            <option value="karaoke">Karaoke</option>
            <option value="fade">Fade</option>
            <option value="pop">Pop</option>
            <option value="slide">Slide</option>
          </select>
        </div>
      </div>
      <div style={{ marginTop: '12px' }}>
        <label style={{ display: 'flex', gap: '6px', alignItems: 'center', fontSize: '13px' }}>
          <input type="checkbox" checked={style.bold} onChange={(e) => update('bold', e.target.checked)} />
          Bold text
        </label>
      </div>
      <div style={{ marginTop: '12px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Highlight Words</label>
        <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
          <input className="input" value={highlightInput} onChange={(e) => setHighlightInput(e.target.value)}
                 placeholder="Add word to highlight" onKeyDown={(e) => e.key === 'Enter' && addHighlightWord()} />
          <button className="btn btn-outline" onClick={addHighlightWord}>Add</button>
        </div>
        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
          {style.highlight_words.map((w, i) => (
            <span key={i} style={{
              background: style.highlight_color + '40',
              color: style.highlight_color,
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              cursor: 'pointer',
            }} onClick={() => update('highlight_words', style.highlight_words.filter((_, j) => j !== i))}>
              {w} x
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
