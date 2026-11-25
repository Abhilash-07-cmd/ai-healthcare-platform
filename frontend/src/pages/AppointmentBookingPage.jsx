import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export const AppointmentBookingPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [doctorId, setDoctorId] = useState(searchParams.get('doctor_id') || '');
  const [departmentId, setDepartmentId] = useState(searchParams.get('department_id') || '');
  const [appointmentDate, setAppointmentDate] = useState(new Date().toISOString().split('T')[0]);

  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);

  const [appointmentType, setAppointmentType] = useState('IN_PERSON');
  const [reasonForVisit, setReasonForVisit] = useState('');

  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [docRes, deptRes] = await Promise.all([
          api.get('/doctors'),
          api.get('/departments')
        ]);
        setDoctors(docRes.data);
        setDepartments(deptRes.data);
      } catch (err) {
        console.error('Error fetching metadata:', err);
      }
    };
    fetchMetadata();
  }, []);

  useEffect(() => {
    if (doctorId && appointmentDate) {
      const fetchSlots = async () => {
        setLoadingSlots(true);
        try {
          const res = await api.get(`/doctors/${doctorId}/slots?target_date=${appointmentDate}`);
          setAvailableSlots(res.data);
        } catch (err) {
          console.error('Error fetching slots:', err);
        } finally {
          setLoadingSlots(false);
        }
      };
      fetchSlots();
    }
  }, [doctorId, appointmentDate]);

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!selectedSlot) {
      setError('Please select an available time slot.');
      return;
    }
    setError('');
    setSubmitting(true);

    try {
      await api.post('/appointments', {
        doctor_id: parseInt(doctorId),
        department_id: parseInt(departmentId),
        appointment_date: appointmentDate,
        start_time: selectedSlot.start_time,
        end_time: selectedSlot.end_time,
        appointment_type: appointmentType,
        reason_for_visit: reasonForVisit
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/patient/appointments');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Booking failed. Double-booking detected or slot unavailable.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <div className="page-header">
        <h1>Book Appointment</h1>
        <p>Select a doctor, preferred date, and available 30-minute consultation slot.</p>
      </div>

      {success && (
        <div className="alert alert-success">
          <CheckCircle2 size={20} style={{ flexShrink: 0 }} />
          <span>Appointment successfully confirmed! Redirecting to My Appointments...</span>
        </div>
      )}

      {error && (
        <div className="alert alert-danger">
          <AlertCircle size={20} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      <form className="glass-panel" style={{ padding: '2rem' }} onSubmit={handleBooking}>
        <div className="form-group">
          <label className="form-label">Select Department</label>
          <select
            className="form-select"
            value={departmentId}
            onChange={(e) => setDepartmentId(e.target.value)}
            required
          >
            <option value="">Choose Department...</option>
            {departments.map(d => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Select Doctor</label>
          <select
            className="form-select"
            value={doctorId}
            onChange={(e) => setDoctorId(e.target.value)}
            required
          >
            <option value="">Choose Doctor...</option>
            {doctors
              .filter(doc => !departmentId || doc.department_id === parseInt(departmentId))
              .map(doc => (
                <option key={doc.id} value={doc.id}>Dr. {doc.user.full_name} ({doc.qualification}) - ₹{doc.consultation_fee}</option>
              ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Appointment Date</label>
          <input
            type="date"
            className="form-input"
            min={new Date().toISOString().split('T')[0]}
            value={appointmentDate}
            onChange={(e) => setAppointmentDate(e.target.value)}
            required
          />
        </div>

        {/* Time Slot Picker */}
        <div className="form-group">
          <label className="form-label">Available Time Slots</label>
          {loadingSlots ? (
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>Checking slot engine availability...</p>
          ) : availableSlots.length === 0 ? (
            <div className="alert alert-warning" style={{ marginTop: '0.5rem', marginBottom: 0 }}>
              No open slots available for this date. You can join the Smart Waitlist!
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))', gap: '0.6rem', marginTop: '0.5rem' }}>
              {availableSlots.map(slot => (
                <button
                  type="button"
                  key={slot.id}
                  onClick={() => setSelectedSlot(slot)}
                  className={`slot-btn ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                >
                  {slot.start_time.substring(0, 5)}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="form-group">
          <label className="form-label">Consultation Type</label>
          <select
            className="form-select"
            value={appointmentType}
            onChange={(e) => setAppointmentType(e.target.value)}
          >
            <option value="IN_PERSON">In-Person Consultation</option>
            <option value="TELECONSULTATION">Teleconsultation (Video/Audio)</option>
            <option value="FOLLOW_UP">Follow-up Visit</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Reason for Visit (Administrative Note)</label>
          <textarea
            className="form-textarea"
            rows="3"
            placeholder="Describe your general consultation topic or concern..."
            value={reasonForVisit}
            onChange={(e) => setReasonForVisit(e.target.value)}
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.85rem', marginTop: '0.5rem' }} disabled={submitting}>
          <span>{submitting ? 'Confirming Reservation...' : 'Confirm Appointment Booking'}</span>
        </button>
      </form>
    </div>
  );
};
