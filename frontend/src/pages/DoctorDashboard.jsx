import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { StatCard } from '../components/StatCard';
import { Calendar, Users, CheckCircle2, Clock, Stethoscope, ArrowRight } from 'lucide-react';

export const DoctorDashboard = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const res = await api.get('/appointments');
        setAppointments(res.data);
      } catch (err) {
        console.error('Failed to load doctor schedule:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSchedule();
  }, []);

  const todayStr = new Date().toISOString().split('T')[0];
  const todayAppts = appointments.filter(a => a.appointment_date === todayStr);
  const completedCount = appointments.filter(a => a.status === 'COMPLETED').length;
  const confirmedCount = appointments.filter(a => a.status === 'CONFIRMED').length;

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Doctor Portal & Consultation Queue</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Manage your daily appointments, patient queue, and working hours.</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard
          title="Today's Appointments"
          value={todayAppts.length}
          subtitle={`${confirmedCount} waiting / confirmed`}
          icon={Calendar}
          color="var(--primary)"
        />
        <StatCard
          title="Completed Consultations"
          value={completedCount}
          subtitle="Total completed"
          icon={CheckCircle2}
          color="var(--accent)"
        />
        <StatCard
          title="Total Scheduled Patients"
          value={appointments.length}
          subtitle="Total bookings"
          icon={Users}
          color="var(--info)"
        />
        <StatCard
          title="Working Status"
          value="Available"
          subtitle="Click schedule to modify"
          icon={Clock}
          color="var(--warning)"
        />
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Today's Patient Queue</h3>
          <Link to="/doctor/appointments" className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
            <span>Manage Consultations</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Loading schedule...</p>
        ) : todayAppts.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No patient consultations scheduled for today.</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Queue #</th>
                  <th>Patient Name</th>
                  <th>Time Slot</th>
                  <th>Type</th>
                  <th>Reason</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {todayAppts.map((a) => (
                  <tr key={a.id}>
                    <td><span className="badge badge-warning">#{a.queue_number || '-'}</span></td>
                    <td style={{ fontWeight: 600 }}>{a.patient.user.full_name}</td>
                    <td>{a.start_time} - {a.end_time}</td>
                    <td><span className="badge badge-info">{a.appointment_type}</span></td>
                    <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {a.reason_for_visit || 'General Consultation'}
                    </td>
                    <td>
                      <span className={`badge ${a.status === 'COMPLETED' ? 'badge-success' : a.status === 'IN_PROGRESS' ? 'badge-warning' : 'badge-info'}`}>
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
