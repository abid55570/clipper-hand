interface Props {
  value: string;
  onChange: (ratio: string) => void;
}

const ratios = [
  { value: '16:9', label: '16:9', desc: 'Landscape', w: 80, h: 45 },
  { value: '9:16', label: '9:16', desc: 'Portrait', w: 45, h: 80 },
  { value: '1:1', label: '1:1', desc: 'Square', w: 60, h: 60 },
  { value: '4:5', label: '4:5', desc: 'Portrait', w: 52, h: 65 },
];

export default function AspectRatioSelector({ value, onChange }: Props) {
  return (
    <div>
      <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
        Aspect Ratio
      </label>
      <div style={{ display: 'flex', gap: '12px' }}>
        {ratios.map((ratio) => (
          <div
            key={ratio.value}
            onClick={() => onChange(ratio.value)}
            style={{
              cursor: 'pointer',
              padding: '12px',
              borderRadius: '8px',
              border: value === ratio.value ? '2px solid var(--accent)' : '2px solid var(--border)',
              background: value === ratio.value ? 'rgba(59,130,246,0.1)' : 'transparent',
              textAlign: 'center',
              flex: 1,
            }}
          >
            <div style={{
              width: ratio.w,
              height: ratio.h,
              background: value === ratio.value ? 'var(--accent)' : 'var(--bg-card)',
              margin: '0 auto 8px',
              borderRadius: '4px',
            }} />
            <div style={{ fontWeight: 500, fontSize: '14px' }}>{ratio.label}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{ratio.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
