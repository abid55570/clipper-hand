const headerStyle: React.CSSProperties = {
  background: 'var(--bg-secondary)',
  borderBottom: '1px solid var(--border)',
  padding: '12px 24px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
};

export default function Header() {
  return (
    <header style={headerStyle}>
      <h2 style={{ fontSize: '18px', fontWeight: 600 }}>ClipperHand</h2>
      <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
        AI Video Clipping Platform v1.0
      </span>
    </header>
  );
}
