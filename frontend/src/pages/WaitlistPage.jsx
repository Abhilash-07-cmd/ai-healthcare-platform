import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Clock, CheckCircle2, XCircle, BellRing } from 'lucide-react';

export const WaitlistPage = () => {
  const [waitlists, setWaitlists] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Join form state
  const [departmentId, setDepartmentId] = useState('');
  const [preferredDate, setPreferredDate] = useState(new Date().toISOString().split('T')[0]);
  const [preferredTimeSlot, setPreferredTimeSlot] = useState('morning');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const fetchWaitlist = async () => {
    try {
      const [wRes, deptRes] = await Promise.all([
        api.get('/waitlist/me'),
        api.get('/departments')
      ]);
      setWaitlists(wRes.data);
      setDepartments(deptRes.data);
    } catch (err) {
      console.error('Error fetching waitlist:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWaitlist();
  }, []);

  const handleJoinWaitlist = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await api.post('/waitlist', {
        department_id: parseInt(departmentId),
        preferred_date: preferredDate,
        preferred_time_slot: preferredTimeSlot
      });
      fetchWaitlist();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join waitlist.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAcceptSlot = async (waitlistId) => {
    try {
      await api.post(`/waitlist/${waitlistId}/accept`, {
        start_time: '10:00:00',
        end_time: '10:30:00'
      });
      alert('Waitlist slot accepted! Your appointment is now confirmed.');
      fetchWaitlist();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error accepting waitlist slot.');
    }
  };

  const handleCancelWaitlist = async (waitlistId) => {
    try {
      await api.delete(`/waitlist/${waitlistId}`);
      fetchWaitlist();
    } catch (err) {
      alert('Error cancelling waitlist entry.');
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Smart Waitlist System</h1>
        <p>Join the waitlist when slots are full. Get notified automatically when a cancellation occurs.</p>
      </div>

      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        {/* Join Form */}
        <form className="glass-panel" style={{ padding: '1.75rem' }} onSubmit={handleJoinWaitlist}>
          <h3 style={{ fontSize: '1.12rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={18} color="var(--primary)" />
            <span>Join Department Waitlist</span>
          </h3>

          {error && (
            <div className="alert alert-danger">{error}</div>
          )}

          <div className="form-group">
            <label className="form-label">Department</label>
            <select
              className="form-select"
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
              required
            >
              <option value="">Select Department...</option>
              {departments.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Preferred Date</label>
            <input
              type="date"
              className="form-input"
              min={new Date().toISOString().split('T')[0]}
              value={preferredDate}
              onChange={(e) => setPreferredDate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Time Preference</label>
            <select
              className="form-select"
              value={preferredTimeSlot}
              onChange={(e) => setPreferredTimeSlot(e.target.value)}
            >
              <option value="morning">Morning (09:00 - 13:00)</option>
              <option value="afternoon">Afternoon (14:00 - 17:00)</option>
              <option value="evening">Evening (17:00 - 20:00)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
            <span>{submitting ? 'Joining...' : 'Join Waitlist Queue'}</span>
          </button>
        </form>

        {/* Active Waitlists */}
        <div className="glass-panel" style={{ padding: '1.75rem' }}>
          <h3 style={{ fontSize: '1.12rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BellRing size={18} color="var(--secondary)" />
            <span>My Active Waitlist Positions</span>
          </h3>

          {loading ? (
            <div className="loading-state">Loading waitlist entries...</div>
          ) : waitlists.length === 0 ? (
            <div className="empty-state" style={{ padding: '2rem 1rem' }}>
              <div className="empty-state-icon">
                <Clock size={24} />
              </div>
              <p>You have no active waitlist entries.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {waitlists.map(w => (
                <div
                  key={w.id}
                  style={{
                    padding: '1rem 1.1rem',
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>{w.department.name}</h4>
                    <span className="badge badge-warning">Position #{w.position}</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.8rem' }}>
                    Preferred Date: {w.preferred_date} ({w.preferred_time_slot})
                  </p>

                  {w.status === 'NOTIFIED' && (
                    <div className="alert alert-success" style={{ padding: '0.65rem 0.85rem', fontSize: '0.82rem', marginBottom: '0.8rem' }}>
                      Slot Available! A cancellation occurred. Click accept to confirm.
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {w.status === 'NOTIFIED' && (
                      <button className="btn btn-teal" style={{ padding: '0.35rem 0.8rem', fontSize: '0.78rem' }} onClick={() => handleAcceptSlot(w.id)}>
                        <CheckCircle2 size={14} />
                        <span>Accept Slot Offer</span>
                      </button>
                    )}
                    {w.status === 'WAITING' && (
                      <button className="btn btn-secondary" style={{ padding: '0.35rem 0.8rem', fontSize: '0.78rem' }} onClick={() => handleCancelWaitlist(w.id)}>
                        <XCircle size={14} />
                        <span>Leave Waitlist</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
