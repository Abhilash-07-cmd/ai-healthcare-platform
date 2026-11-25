import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Shield, Stethoscope, HeartPulse, Menu } from 'lucide-react';

export const Navbar = ({ onToggleSidebar }) => {
  const { user } = useAuth();
  if (!user) return null;

  const roleColors = {
    PATIENT: 'badge-info',
    DOCTOR: 'badge-teal',
    ADMIN: 'badge-warning'
  };

  const roleIcons = {
    PATIENT: HeartPulse,
    DOCTOR: Stethoscope,
    ADMIN: Shield
  };

  const RoleIcon = roleIcons[user.role] || User;

  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
        {onToggleSidebar && (
          <button
            type="button"
            className="mobile-menu-btn"
            onClick={onToggleSidebar}
            aria-label="Open navigation menu"
          >
            <Menu size={20} />
          </button>
        )}
        <div style={{ minWidth: 0 }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            Welcome back, <span style={{ color: 'var(--primary)' }}>{user.full_name}</span>
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Smart Healthcare Care Navigation Platform
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexShrink: 0 }}>
        <div className={`badge ${roleColors[user.role] || 'badge-info'}`} style={{ padding: '0.42rem 0.85rem' }}>
          <RoleIcon size={14} />
          <span>{user.role}</span>
        </div>

        <div
          style={{
            width: '38px',
            height: '38px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--light-blue), var(--light-teal))',
            border: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            color: 'var(--primary)'
          }}
        >
          {user.full_name.charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  );
};
