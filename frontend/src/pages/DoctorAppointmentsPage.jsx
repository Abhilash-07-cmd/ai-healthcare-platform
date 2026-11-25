import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal } from '../components/Modal';
import { Stethoscope, CheckCircle2, Clock, FileText, User } from 'lucide-react';

export const DoctorAppointmentsPage = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [selectedAppt, setSelectedAppt] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('IN_PROGRESS');
  const [notes, setNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchSchedule = async () => {
    try {
      const res = await api.get('/appointments');
      setAppointments(res.data);
    } catch (err) {
      console.error('Error fetching doctor schedule:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedule();
  }, []);

  const handleUpdateStatus = async () => {
    if (!selectedAppt) return;
    setActionLoading(true);
    try {
      await api.put(`/appointments/${selectedAppt.id}`, {
        status: newStatus,
        notes: notes
      });
      setShowStatusModal(false);
      fetchSchedule();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update consultation.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Patient Consultations & Queue</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Review authorized patient appointment details, advance queue status, and add clinical notes.</p>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading patient queue...</p>
        ) : appointments.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '2rem', textAlign: 'center' }}>No patient consultations found.</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Queue #</th>
                  <th>Patient Info</th>
                  <th>Date & Time</th>
                  <th>Type</th>
                  <th>Reason</th>
                  <th>Notes</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((a) => (
                  <tr key={a.id}>
                    <td><span className="badge badge-warning">#{a.queue_number || '-'}</span></td>
                    <td>
                      <div style={{ fontWeight: 600 }}>{a.patient.user.full_name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{a.patient.gender || 'Patient'} • DOB: {a.patient.date_of_birth || 'N/A'}</div>
                    </td>
                    <td>
                      <div>{a.appointment_date}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{a.start_time} - {a.end_time}</div>
                    </td>
                    <td><span className="badge badge-info">{a.appointment_type}</span></td>
                    <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {a.reason_for_visit || 'General'}
                    </td>
                    <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                      {a.notes || 'None'}
                    </td>
                    <td>
                      <span className={`badge ${a.status === 'COMPLETED' ? 'badge-success' : a.status === 'IN_PROGRESS' ? 'badge-warning' : 'badge-info'}`}>
                        {a.status}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        onClick={() => {
                          setSelectedAppt(a);
                          setNewStatus(a.status);
                          setNotes(a.notes || '');
                          setShowStatusModal(true);
                        }}
                      >
                        <Stethoscope size={12} />
                        <span>Update</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Status Modal */}
      <Modal isOpen={showStatusModal} onClose={() => setShowStatusModal(false)} title="Update Patient Consultation">
        <div className="form-group">
          <label className="form-label">Consultation Queue Status</label>
          <select className="form-select" value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
            <option value="CONFIRMED">CONFIRMED (Waiting)</option>
            <option value="IN_PROGRESS">IN_PROGRESS (In Consultation)</option>
            <option value="COMPLETED">COMPLETED (Finished)</option>
            <option value="NO_SHOW">NO_SHOW (Patient Missed)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Clinical Doctor Notes</label>
          <textarea
            className="form-textarea"
            rows="4"
            placeholder="Add clinical observations, follow-up instructions, or administrative notes..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.8rem', marginTop: '1.5rem' }}>
          <button className="btn btn-secondary" onClick={() => setShowStatusModal(false)}>Cancel</button>
          <button className="btn btn-primary" onClick={handleUpdateStatus} disabled={actionLoading}>
            {actionLoading ? 'Saving...' : 'Save Consultation Record'}
          </button>
        </div>
      </Modal>
    </div>
  );
};
