import type { ClipTimestamp } from '../../types';

interface Props {
  duration: number;
  clips: ClipTimestamp[];
  currentTime?: number;
  onSeek?: (time: number) => void;
}

const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

export default function Timeline({ duration, clips, currentTime = 0, onSeek }: Props) {
  if (duration <= 0) return null;

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    onSeek?.(pct * duration);
  };

  return (
    <div
      style={{
        position: 'relative',
        height: '60px',
        background: 'var(--bg-card)',
        borderRadius: '6px',
        cursor: 'pointer',
        overflow: 'hidden',
        marginTop: '12px',
      }}
      onClick={handleClick}
    >
      {/* Clip ranges */}
      {clips.map((clip, i) => (
        <div
          key={i}
          title={`${clip.label}: ${clip.start}s - ${clip.end}s`}
          style={{
            position: 'absolute',
            left: `${(clip.start / duration) * 100}%`,
            width: `${((clip.end - clip.start) / duration) * 100}%`,
            top: '8px',
            height: '28px',
            background: colors[i % colors.length] + '80',
            border: `1px solid ${colors[i % colors.length]}`,
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '11px',
            color: 'white',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            padding: '0 4px',
          }}
        >
          {clip.label}
        </div>
      ))}

      {/* Playhead */}
      <div
        style={{
          position: 'absolute',
          left: `${(currentTime / duration) * 100}%`,
          top: 0,
          bottom: 0,
          width: '2px',
          background: 'var(--error)',
          zIndex: 10,
        }}
      />

      {/* Time labels */}
      <div style={{
        position: 'absolute',
        bottom: '4px',
        left: '8px',
        fontSize: '11px',
        color: 'var(--text-secondary)',
      }}>
        0:00
      </div>
      <div style={{
        position: 'absolute',
        bottom: '4px',
        right: '8px',
        fontSize: '11px',
        color: 'var(--text-secondary)',
      }}>
        {Math.floor(duration / 60)}:{String(Math.floor(duration % 60)).padStart(2, '0')}
      </div>
    </div>
  );
}
