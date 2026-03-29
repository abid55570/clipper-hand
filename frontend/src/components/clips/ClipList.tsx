import type { Clip } from '../../types';
import ClipCard from './ClipCard';

interface Props {
  clips: Clip[];
  onDownload?: (clipId: string) => void;
  onDelete?: (clipId: string) => void;
  onExport?: (clipId: string) => void;
}

export default function ClipList({ clips, onDownload, onDelete, onExport }: Props) {
  if (clips.length === 0) {
    return (
      <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '40px' }}>
        No clips yet. Add timestamps and generate clips.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {clips.map((clip) => (
        <ClipCard
          key={clip.id}
          clip={clip}
          onDownload={() => onDownload?.(clip.id)}
          onDelete={() => onDelete?.(clip.id)}
          onExport={() => onExport?.(clip.id)}
        />
      ))}
    </div>
  );
}
