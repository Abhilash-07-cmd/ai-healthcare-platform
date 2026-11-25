import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Clock, Calendar, Plus, Trash2, CheckCircle2 } from 'lucide-react';

export const DoctorAvailabilityPage = () => {
  const [availability, setAvailability] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);

  // Leave form state
  const [leaveStart, setLeaveStart] = useState('');
  const [leaveEnd, setLeaveEnd] = useState('');
  const [leaveReason, setLeaveReason] = useState('');
  const [submittingLeave, setSubmittingLeave] = useState(false);

  const fetchDoctorScheduleData = async () => {
    try {
      const [availRes, leaveRes] = await Promise.all([
        api.get('/doctors/me/availability'),
        api.get('/doctors/me/leave')
      ]);
      setAvailability(availRes.data);
      setLeaves(leaveRes.data);
    } catch (err) {
      console.error('Error fetching doctor schedule data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctorScheduleData();
  }, []);

  const handleAddLeave = async (e) => {
    e.preventDefault();
    setSubmittingLeave(true);
    try {
      await api.post('/doctors/me/leave', {
        start_date: leaveStart,
        end_date: leaveEnd,
        reason: leaveReason
      });
      setLeaveStart('');
      setLeaveEnd('');
      setLeaveReason('');
      fetchDoctorScheduleData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add leave.');
    } finally {
      setSubmittingLeave(false);
    }
  };

  const handleDeleteLeave = async (leaveId) => {
    try {
      await api.delete(`/doctors/me/leave/${leaveId}`);
      fetchDoctorScheduleData();
    } catch (err) {
      alert('Failed to delete leave.');
    }
  };

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Schedule & Leave Management</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Configure weekly shift windows and record holiday leave periods.</p>
      </div>

      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        {/* Weekly Working Schedule */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={18} color="var(--primary)" />
            <span>Configured Weekly Shift Windows</span>
          </h3>

          {loading ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading working hours...</p>
          ) : availability.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Standard Mon-Fri (09:00 - 17:00, 30m slots) active by default.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              {availability.map(a => (
                <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem', background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)' }}>
                  <span style={{ fontWeight: 600 }}>{daysOfWeek[a.day_of_week]}</span>
                  <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{a.start_time} - {a.end_time} ({a.slot_duration_minutes}m slots)</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Leave Management */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Calendar size={18} color="var(--warning)" />
            <span>Mark Holiday / Leave Period</span>
          </h3>

          <form onSubmit={handleAddLeave} style={{ marginBottom: '1.5rem' }}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Start Date</label>
                <input type="date" className="form-input" required value={leaveStart} onChange={(e) => setLeaveStart(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">End Date</label>
                <input type="date" className="form-input" required value={leaveEnd} onChange={(e) => setLeaveEnd(e.target.value)} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Reason</label>
              <input type="text" className="form-input" placeholder="Medical conference / personal holiday..." value={leaveReason} onChange={(e) => setLeaveReason(e.target.value)} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={submittingLeave}>
              <Plus size={16} />
              <span>{submittingLeave ? 'Saving Leave...' : 'Add Leave Record'}</span>
            </button>
          </form>

          {/* Active Leaves List */}
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.8rem' }}>Recorded Leaves</h4>
          {leaves.length === 0 ? (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No leave records logged.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {leaves.map(l => (
                <div key={l.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0.8rem', background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{l.start_date} to {l.end_date}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{l.reason || 'Leave'}</div>
                  </div>
                  <button className="btn btn-danger" style={{ padding: '0.2rem 0.5rem' }} onClick={() => handleDeleteLeave(l.id)}>
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
