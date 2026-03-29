import React from 'react';

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'danger' | 'success' | 'outline';
  loading?: boolean;
}

export default function Button({ variant = 'primary', loading, children, disabled, ...props }: Props) {
  return (
    <button className={`btn btn-${variant}`} disabled={disabled || loading} {...props}>
      {loading ? 'Loading...' : children}
    </button>
  );
}
