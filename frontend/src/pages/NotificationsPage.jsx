import React, { useState, useEffect } from 'react';
import { Bell, CheckCircle2 } from 'lucide-react';

export const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For notification list fetching
    setLoading(false);
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Notification Center</h1>
        <p>Real-time updates regarding appointment confirmations, rescheduling, and waitlist slot alerts.</p>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div
            style={{
              padding: '1.1rem 1.25rem',
              background: '#F0FDF4',
              border: '1px solid #BBF7D0',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              gap: '1rem',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '12px',
                background: '#DCFCE7',
                color: 'var(--success)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              <CheckCircle2 size={22} />
            </div>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>Appointment Confirmed</h4>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-dark)', marginTop: '0.15rem' }}>
                Your consultation with Dr. John Smith has been booked for tomorrow at 10:00 AM.
              </p>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '0.3rem', display: 'block' }}>2 hours ago</span>
            </div>
          </div>

          <div
            style={{
              padding: '1.1rem 1.25rem',
              background: '#F0FDFA',
              border: '1px solid #99F6E4',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              gap: '1rem',
              alignItems: 'center'
            }}
          >
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: '12px',
                background: 'var(--light-teal)',
                color: 'var(--secondary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              <Bell size={22} />
            </div>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>Waitlist Slot Offer</h4>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-dark)', marginTop: '0.15rem' }}>
                A slot opened up in Dermatology! Click Waitlist in your sidebar to accept and claim the slot.
              </p>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '0.3rem', display: 'block' }}>Yesterday</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
