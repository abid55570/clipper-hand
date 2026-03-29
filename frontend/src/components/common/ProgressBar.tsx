interface Props {
  progress: number;
  color?: string;
}

export default function ProgressBar({ progress, color }: Props) {
  return (
    <div className="progress-bar">
      <div
        className="progress-bar-fill"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%`, background: color }}
      />
    </div>
  );
}
