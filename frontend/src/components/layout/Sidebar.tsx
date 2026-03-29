import { useLocation, Link } from 'react-router-dom';

const sidebarStyle: React.CSSProperties = {
  width: '220px',
  background: 'var(--bg-secondary)',
  borderRight: '1px solid var(--border)',
  padding: '20px 0',
  display: 'flex',
  flexDirection: 'column',
};

const logoStyle: React.CSSProperties = {
  padding: '0 20px 20px',
  fontSize: '20px',
  fontWeight: 700,
  color: 'var(--accent)',
  borderBottom: '1px solid var(--border)',
  marginBottom: '12px',
};

const navItems = [
  { path: '/', label: 'Dashboard' },
  { path: '/upload', label: 'Upload Video' },
  { path: '/jobs', label: 'Jobs' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <nav style={sidebarStyle}>
      <div style={logoStyle}>ClipperHand</div>
      {navItems.map(({ path, label }) => (
        <Link
          key={path}
          to={path}
          style={{
            padding: '10px 20px',
            color: location.pathname === path ? 'var(--accent)' : 'var(--text-secondary)',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: location.pathname === path ? 600 : 400,
            background: location.pathname === path ? 'rgba(59,130,246,0.1)' : 'transparent',
            borderLeft: location.pathname === path ? '3px solid var(--accent)' : '3px solid transparent',
          }}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
}
