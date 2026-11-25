import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Search, Stethoscope, Star, Calendar } from 'lucide-react';

export const DoctorSearchPage = () => {
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docRes, deptRes] = await Promise.all([
          api.get('/doctors'),
          api.get('/departments')
        ]);
        setDoctors(docRes.data);
        setDepartments(deptRes.data);
      } catch (err) {
        console.error('Error fetching doctors:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredDoctors = doctors.filter(doc => {
    const matchesSearch = doc.user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          doc.qualification.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = !selectedDept || doc.department_id === parseInt(selectedDept);
    return matchesSearch && matchesDept;
  });

  return (
    <div>
      <div className="page-header">
        <h1>Find Doctors &amp; Specialists</h1>
        <p>Search verified medical specialists with transparent availability and consultation fees.</p>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel" style={{ padding: '1.15rem', marginBottom: '1.75rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search doctor by name or qualification..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '2.6rem' }}
          />
          <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
        </div>

        <select
          className="form-select"
          style={{ width: '240px' }}
          value={selectedDept}
          onChange={(e) => setSelectedDept(e.target.value)}
        >
          <option value="">All Departments</option>
          {departments.map(d => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
      </div>

      {/* Doctor Cards Grid */}
      {loading ? (
        <div className="glass-panel loading-state">Loading doctor directory...</div>
      ) : filteredDoctors.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <Stethoscope size={28} />
          </div>
          <p>No doctors found matching your criteria.</p>
        </div>
      ) : (
        <div className="grid-3">
          {filteredDoctors.map(doc => (
            <div key={doc.id} className="glass-panel glass-card-interactive" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', gap: '0.9rem', alignItems: 'center' }}>
                    <div
                      style={{
                        width: '50px',
                        height: '50px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, var(--light-blue), var(--light-teal))',
                        color: 'var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.2rem',
                        fontWeight: 800,
                        flexShrink: 0
                      }}
                    >
                      {doc.user.full_name.charAt(0)}
                    </div>
                    <div>
                      <h3 style={{ fontSize: '1.08rem', fontWeight: 700, color: 'var(--text-main)' }}>Dr. {doc.user.full_name}</h3>
                      <span className="badge badge-teal" style={{ marginTop: '0.25rem' }}>{doc.department.name}</span>
                    </div>
                  </div>

                  <div className="badge badge-warning" style={{ fontWeight: 700 }}>
                    <Star size={13} fill="#D97706" color="#D97706" />
                    <span>{doc.rating}</span>
                  </div>
                </div>

                <p style={{ fontSize: '0.86rem', color: 'var(--text-dark)', marginBottom: '0.75rem', fontWeight: 500 }}>
                  {doc.qualification} • {doc.experience_years} Years Experience
                </p>

                {doc.bio && (
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {doc.bio}
                  </p>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', padding: '0.7rem 0', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', marginBottom: '1.1rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Consultation Fee:</span>
                  <span style={{ fontWeight: 700, color: 'var(--primary)' }}>₹{doc.consultation_fee}</span>
                </div>
              </div>

              <button
                className="btn btn-primary"
                style={{ width: '100%' }}
                onClick={() => navigate(`/patient/book?doctor_id=${doc.id}&department_id=${doc.department_id}`)}
              >
                <Calendar size={16} />
                <span>Book Appointment</span>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
