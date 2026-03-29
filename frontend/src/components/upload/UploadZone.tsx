import React, { useCallback, useState, useRef } from 'react';

interface Props {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

const dropzoneStyle: React.CSSProperties = {
  border: '2px dashed var(--border)',
  borderRadius: '12px',
  padding: '60px 40px',
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'border-color 0.2s, background 0.2s',
};

export default function UploadZone({ onFileSelect, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('video/')) {
        onFileSelect(file);
      }
    },
    [onFileSelect, disabled]
  );

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      style={{
        ...dropzoneStyle,
        borderColor: dragOver ? 'var(--accent)' : 'var(--border)',
        background: dragOver ? 'rgba(59,130,246,0.05)' : 'transparent',
        opacity: disabled ? 0.5 : 1,
      }}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>
        {dragOver ? '+ Drop here' : 'Upload'}
      </div>
      <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>
        Drag & drop a video file here, or click to browse
      </p>
      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '8px' }}>
        Supports MP4, AVI, MKV, MOV, WebM (up to 10 GB)
      </p>
    </div>
  );
}
