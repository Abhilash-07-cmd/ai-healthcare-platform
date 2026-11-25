import React from 'react';

export const StatCard = ({ title, value, subtitle, icon: Icon, color = 'var(--primary)', bgColor }) => {
  const iconBg = bgColor || (color === 'var(--secondary)' || color === 'var(--accent)' ? 'var(--light-teal)' : color === 'var(--warning)' ? '#FEF3C7' : color === 'var(--danger)' ? '#FEE2E2' : 'var(--light-blue)');

  return (
    <div
      className="glass-panel"
      style={{
        padding: '1.4rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem'
      }}
    >
      <div style={{ minWidth: 0 }}>
        <span style={{ fontSize: '0.84rem', color: 'var(--text-muted)', fontWeight: 600 }}>{title}</span>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--text-main)', lineHeight: 1.2 }}>
          {value}
        </h2>
        {subtitle && (
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.3rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {subtitle}
          </p>
        )}
      </div>
      {Icon && (
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '14px',
            background: iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}
        >
          <Icon size={24} color={color} />
        </div>
      )}
    </div>
  );
};
