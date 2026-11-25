import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { StatCard } from '../components/StatCard';
import { Calendar, Bot, Clock, Search, ArrowRight, CheckCircle2 } from 'lucide-react';

export const PatientDashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [waitlist, setWaitlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [apptRes, waitlistRes] = await Promise.all([
          api.get('/appointments?limit=5'),
          api.get('/waitlist/me')
        ]);
        setAppointments(apptRes.data);
        setWaitlist(waitlistRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const upcomingAppt = appointments.find(a => a.status === 'CONFIRMED' || a.status === 'REQUESTED');
  const activeWaitlist = waitlist.find(w => w.status === 'WAITING' || w.status === 'NOTIFIED');

  return (
    <div>
      <div className="page-header">
        <h1>Patient Dashboard</h1>
        <p>Manage your appointments, AI consultations, and hospital waitlists.</p>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard
          title="Upcoming Appointment"
          value={upcomingAppt ? upcomingAppt.appointment_date : 'None'}
          subtitle={upcomingAppt ? `Dr. ${upcomingAppt.doctor.user.full_name}` : 'Book a consultation'}
          icon={Calendar}
          color="var(--primary)"
        />
        <StatCard
          title="Total Bookings"
          value={appointments.length}
          subtitle="Lifetime appointments"
          icon={CheckCircle2}
          color="var(--secondary)"
        />
        <StatCard
          title="Waitlist Position"
          value={activeWaitlist ? `#${activeWaitlist.position}` : 'None'}
          subtitle={activeWaitlist ? activeWaitlist.department.name : 'No active waitlist'}
          icon={Clock}
          color="var(--warning)"
        />
        <StatCard
          title="AI Care Navigator"
          value="Ready"
          subtitle="Click to start consultation"
          icon={Bot}
          color="var(--primary)"
        />
      </div>

      {/* Quick Action Banner with Medical Blue-to-Teal Gradient */}
      <div
        className="clinical-banner"
        style={{
          marginBottom: '2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1.25rem'
        }}
      >
        <div>
          <span
            style={{
              display: 'inline-block',
              fontSize: '0.72rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              background: 'rgba(255, 255, 255, 0.18)',
              padding: '0.25rem 0.65rem',
              borderRadius: '9999px',
              marginBottom: '0.5rem'
            }}
          >
            AI Care Assistance
          </span>
          <h3 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '0.3rem', color: '#FFFFFF' }}>
            Need to find the right doctor or book quickly?
          </h3>
          <p style={{ color: 'rgba(255, 255, 255, 0.88)', fontSize: '0.92rem' }}>
            Our AI Care Navigator extracts your preferences and recommends available doctors instantly.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link
            to="/patient/ai-assistant"
            className="btn"
            style={{ background: '#FFFFFF', color: 'var(--primary)', fontWeight: 700 }}
          >
            <Bot size={18} />
            <span>Launch AI Navigator</span>
          </Link>
          <Link
            to="/patient/doctors"
            className="btn"
            style={{ background: 'rgba(255, 255, 255, 0.16)', color: '#FFFFFF', border: '1px solid rgba(255, 255, 255, 0.35)' }}
          >
            <Search size={18} />
            <span>Search Doctor Directory</span>
          </Link>
        </div>
      </div>

      {/* Recent Appointments Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.15rem' }}>
          <h3 style={{ fontSize: '1.12rem', fontWeight: 700 }}>Recent Appointments</h3>
          <Link
            to="/patient/appointments"
            style={{
              color: 'var(--primary)',
              fontSize: '0.86rem',
              textDecoration: 'none',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            <span>View All</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {loading ? (
          <div className="loading-state">Loading appointments...</div>
        ) : appointments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <Calendar size={26} />
            </div>
            <p>No appointment records found. Book your first appointment today!</p>
            <Link to="/patient/book" className="btn btn-primary">Book Appointment</Link>
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Doctor</th>
                  <th>Department</th>
                  <th>Date &amp; Time</th>
                  <th>Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {appointments.slice(0, 5).map((a) => (
                  <tr key={a.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>Dr. {a.doctor.user.full_name}</div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>{a.doctor.qualification}</div>
                    </td>
                    <td>{a.department.name}</td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{a.appointment_date}</div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>{a.start_time} - {a.end_time}</div>
                    </td>
                    <td><span className="badge badge-info">{a.appointment_type}</span></td>
                    <td>
                      <span className={`badge ${a.status === 'CONFIRMED' ? 'badge-success' : a.status === 'CANCELLED' ? 'badge-danger' : 'badge-warning'}`}>
                        {a.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
