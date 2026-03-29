import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

const layoutStyle: React.CSSProperties = {
  display: 'flex',
  minHeight: '100vh',
};

const mainStyle: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
};

const contentStyle: React.CSSProperties = {
  flex: 1,
  padding: '24px',
  maxWidth: '1400px',
  width: '100%',
  margin: '0 auto',
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={layoutStyle}>
      <Sidebar />
      <div style={mainStyle}>
        <Header />
        <main style={contentStyle}>{children}</main>
      </div>
    </div>
  );
}
