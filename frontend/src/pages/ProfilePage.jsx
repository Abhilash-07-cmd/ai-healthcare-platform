import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { CheckCircle2 } from 'lucide-react';

export const ProfilePage = () => {
  const { user } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [dob, setDob] = useState('');
  const [gender, setGender] = useState('Male');
  const [bloodGroup, setBloodGroup] = useState('O+');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [medicalHistory, setMedicalHistory] = useState('');

  const [saved, setSaved] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user?.role === 'PATIENT') {
      const fetchPatientProfile = async () => {
        try {
          const res = await api.get('/patients/me');
          const data = res.data;
          if (data.date_of_birth) setDob(data.date_of_birth);
          if (data.gender) setGender(data.gender);
          if (data.blood_group) setBloodGroup(data.blood_group);
          if (data.emergency_contact) setEmergencyContact(data.emergency_contact);
          if (data.medical_history_summary) setMedicalHistory(data.medical_history_summary);
        } catch (err) {
          console.error('Error fetching patient profile:', err);
        }
      };
      fetchPatientProfile();
    }
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (user?.role === 'PATIENT') {
        await api.put('/patients/me', {
          full_name: fullName,
          phone: phone,
          date_of_birth: dob || null,
          gender: gender,
          blood_group: bloodGroup,
          emergency_contact: emergencyContact,
          medical_history_summary: medicalHistory
        });
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Error updating profile:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto' }}>
      <div className="page-header">
        <h1>Profile &amp; Personal Information</h1>
        <p>Manage your account settings, medical history summary, and emergency contacts.</p>
      </div>

      {saved && (
        <div className="alert alert-success">
          <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
          <span>Profile information updated successfully!</span>
        </div>
      )}

      <form className="glass-panel" style={{ padding: '2rem' }} onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Full Name</label>
          <input
            type="text"
            className="form-input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Email Address (Read-only)</label>
          <input
            type="email"
            className="form-input"
            value={user?.email || ''}
            disabled
          />
        </div>

        <div className="form-group">
          <label className="form-label">Phone Number</label>
          <input
            type="text"
            className="form-input"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        {user?.role === 'PATIENT' && (
          <>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Date of Birth</label>
                <input
                  type="date"
                  className="form-input"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Gender</label>
                <select className="form-select" value={gender} onChange={(e) => setGender(e.target.value)}>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Blood Group</label>
                <select className="form-select" value={bloodGroup} onChange={(e) => setBloodGroup(e.target.value)}>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Emergency Contact</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Relative Name & Phone"
                  value={emergencyContact}
                  onChange={(e) => setEmergencyContact(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Medical History Summary</label>
              <textarea
                className="form-textarea"
                rows="3"
                placeholder="Chronic conditions, allergies, or past surgeries..."
                value={medicalHistory}
                onChange={(e) => setMedicalHistory(e.target.value)}
              />
            </div>
          </>
        )}

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.85rem', marginTop: '0.5rem' }} disabled={submitting}>
          <span>{submitting ? 'Saving Changes...' : 'Save Profile Changes'}</span>
        </button>
      </form>
    </div>
  );
};
