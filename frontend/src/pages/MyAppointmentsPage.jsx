import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal } from '../components/Modal';
import { Calendar, XCircle, RefreshCw } from 'lucide-react';

export const MyAppointmentsPage = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal states
  const [selectedAppt, setSelectedAppt] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);

  const [cancelReason, setCancelReason] = useState('');
  const [newDate, setNewDate] = useState('');
  const [newStartTime, setNewStartTime] = useState('10:00:00');

  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchAppointments = async () => {
    try {
      const res = await api.get('/appointments');
      setAppointments(res.data);
    } catch (err) {
      console.error('Error loading appointments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const handleCancel = async () => {
    if (!selectedAppt) return;
    setActionLoading(true);
    setActionError('');
    try {
      await api.post(`/appointments/${selectedAppt.id}/cancel?reason=${encodeURIComponent(cancelReason)}`);
      setShowCancelModal(false);
      fetchAppointments();
    } catch (err) {
      setActionError(err.response?.data?.detail || 'Cancellation failed.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReschedule = async () => {
    if (!selectedAppt) return;
    setActionLoading(true);
    setActionError('');
    try {
      await api.post(`/appointments/${selectedAppt.id}/reschedule`, {
        new_date: newDate,
        new_start_time: newStartTime,
        new_end_time: '10:30:00'
      });
      setShowRescheduleModal(false);
      fetchAppointments();
    } catch (err) {
      setActionError(err.response?.data?.detail || 'Rescheduling failed.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>My Appointments</h1>
        <p>Track, reschedule, or cancel your upcoming healthcare appointments.</p>
      </div>

      {loading ? (
        <div className="glass-panel loading-state">Loading appointment history...</div>
      ) : appointments.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <Calendar size={28} />
          </div>
          <p>You have no scheduled appointments.</p>
        </div>
      ) : (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Appointment ID</th>
                  <th>Doctor</th>
                  <th>Department</th>
                  <th>Date &amp; Time</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((a) => (
                  <tr key={a.id}>
                    <td><span className="badge badge-info">#{a.id}</span></td>
                    <td style={{ fontWeight: 600 }}>Dr. {a.doctor.user.full_name}</td>
                    <td>{a.department.name}</td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{a.appointment_date}</div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>{a.start_time} - {a.end_time}</div>
                    </td>
                    <td><span className="badge badge-teal">{a.appointment_type}</span></td>
                    <td>
                      <span className={`badge ${a.status === 'CONFIRMED' ? 'badge-success' : a.status === 'CANCELLED' ? 'badge-danger' : 'badge-warning'}`}>
                        {a.status}
                      </span>
                    </td>
                    <td>
                      {a.status === 'CONFIRMED' && (
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '0.35rem 0.7rem', fontSize: '0.78rem' }}
                            onClick={() => {
                              setSelectedAppt(a);
                              setNewDate(a.appointment_date);
                              setShowRescheduleModal(true);
                            }}
                          >
                            <RefreshCw size={13} />
                            <span>Reschedule</span>
                          </button>

                          <button
                            className="btn btn-danger"
                            style={{ padding: '0.35rem 0.7rem', fontSize: '0.78rem' }}
                            onClick={() => {
                              setSelectedAppt(a);
                              setShowCancelModal(true);
                            }}
                          >
                            <XCircle size={13} />
                            <span>Cancel</span>
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Cancel Modal */}
      <Modal isOpen={showCancelModal} onClose={() => setShowCancelModal(false)} title="Cancel Appointment">
        {actionError && (
          <div className="alert alert-danger">{actionError}</div>
        )}
        <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', marginBottom: '1rem' }}>
          Are you sure you want to cancel your appointment with <strong>Dr. {selectedAppt?.doctor.user.full_name}</strong>?
        </p>
        <div className="form-group">
          <label className="form-label">Cancellation Reason (Optional)</label>
          <input
            type="text"
            className="form-input"
            placeholder="Reason for cancellation..."
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.8rem', marginTop: '1.5rem' }}>
          <button className="btn btn-secondary" onClick={() => setShowCancelModal(false)}>Keep Appointment</button>
          <button className="btn btn-danger" onClick={handleCancel} disabled={actionLoading}>
            {actionLoading ? 'Cancelling...' : 'Confirm Cancellation'}
          </button>
        </div>
      </Modal>

      {/* Reschedule Modal */}
      <Modal isOpen={showRescheduleModal} onClose={() => setShowRescheduleModal(false)} title="Reschedule Appointment">
        {actionError && (
          <div className="alert alert-danger">{actionError}</div>
        )}
        <div className="form-group">
          <label className="form-label">Select New Date</label>
          <input
            type="date"
            className="form-input"
            min={new Date().toISOString().split('T')[0]}
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Select New Time Slot</label>
          <select className="form-select" value={newStartTime} onChange={(e) => setNewStartTime(e.target.value)}>
            <option value="09:00:00">09:00 AM</option>
            <option value="10:00:00">10:00 AM</option>
            <option value="11:00:00">11:00 AM</option>
            <option value="14:00:00">02:00 PM</option>
            <option value="15:00:00">03:00 PM</option>
          </select>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.8rem', marginTop: '1.5rem' }}>
          <button className="btn btn-secondary" onClick={() => setShowRescheduleModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleReschedule} disabled={actionLoading}>
            {actionLoading ? 'Rescheduling...' : 'Confirm Reschedule'}
          </button>
        </div>
      </Modal>
    </div>
  );
};
