import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Bot,
  Search,
  CalendarCheck,
  Clock,
  Bell,
  User,
  Users,
  Building2,
  ShieldAlert,
  Stethoscope,
  LogOut,
  X
} from 'lucide-react';

export const Sidebar = ({ isOpen = false, onClose }) => {
  const { user, logout } = useAuth();
  if (!user) return null;

  const role = user.role;

  const patientLinks = [
    { to: '/patient/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/patient/ai-assistant', label: 'AI Assistant', icon: Bot },
    { to: '/patient/doctors', label: 'Find Doctors', icon: Search },
    { to: '/patient/appointments', label: 'My Appointments', icon: CalendarCheck },
    { to: '/patient/waitlist', label: 'Waitlist', icon: Clock },
    { to: '/patient/notifications', label: 'Notifications', icon: Bell },
    { to: '/patient/profile', label: 'Profile', icon: User },
  ];

  const doctorLinks = [
    { to: '/doctor/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/doctor/appointments', label: 'Patient Queue', icon: Stethoscope },
    { to: '/doctor/availability', label: 'Schedule & Leave', icon: Clock },
    { to: '/doctor/profile', label: 'Doctor Profile', icon: User },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Analytics', icon: LayoutDashboard },
    { to: '/admin/users', label: 'User Directory', icon: Users },
    { to: '/admin/departments', label: 'Departments', icon: Building2 },
    { to: '/admin/audit-logs', label: 'Audit Logs', icon: ShieldAlert },
  ];

  let links = patientLinks;
  if (role === 'DOCTOR') links = doctorLinks;
  if (role === 'ADMIN') links = adminLinks;

  return (
    <>
      <div
        className={`sidebar-backdrop ${isOpen ? 'open' : ''}`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div
          style={{
            padding: '1.25rem 1.4rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border)'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <div className="brand-mark">
              <Stethoscope size={22} color="#ffffff" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.08rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.2 }}>
                AI Health
              </h2>
              <span
                style={{
                  fontSize: '0.7rem',
                  color: 'var(--secondary)',
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  fontWeight: 700
                }}
              >
                Care Navigator
              </span>
            </div>
          </div>

          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="mobile-menu-btn"
              style={{ marginRight: 0, width: '32px', height: '32px' }}
              aria-label="Close navigation menu"
            >
              <X size={18} />
            </button>
          )}
        </div>

        <nav style={{ padding: '1rem 0.85rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '0.3rem', overflowY: 'auto' }}>
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={onClose}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                  background: isActive ? 'var(--light-blue)' : 'transparent',
                  borderLeft: isActive ? '3px solid var(--secondary)' : '3px solid transparent',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.9rem',
                  textDecoration: 'none',
                  transition: 'all 0.2s ease'
                })}
              >
                <Icon size={18} />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div style={{ padding: '1rem', borderTop: '1px solid var(--border)' }}>
          <button
            onClick={logout}
            className="btn btn-secondary"
            style={{ width: '100%', justifyContent: 'flex-start', color: 'var(--text-dark)' }}
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};
