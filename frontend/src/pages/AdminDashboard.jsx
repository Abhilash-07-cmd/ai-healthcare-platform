import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { StatCard } from '../components/StatCard';
import { Users, Stethoscope, Calendar, Building2, ShieldAlert, Activity } from 'lucide-react';

export const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [uRes, dRes, deptRes, apptRes] = await Promise.all([
          api.get('/admin/users'),
          api.get('/doctors'),
          api.get('/departments'),
          api.get('/appointments')
        ]);
        setUsers(uRes.data);
        setDoctors(dRes.data);
        setDepartments(deptRes.data);
        setAppointments(apptRes.data);
      } catch (err) {
        console.error('Failed to load admin analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  const totalPatients = users.filter(u => u.role === 'PATIENT').length;
  const totalDoctors = doctors.length;
  const completedAppts = appointments.filter(a => a.status === 'COMPLETED').length;
  const cancelledAppts = appointments.filter(a => a.status === 'CANCELLED').length;

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Admin Analytics & System Operations</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Real-time healthcare platform performance, user management, and audit tracking.</p>
      </div>

      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        <StatCard
          title="Total Registered Patients"
          value={totalPatients}
          subtitle="Active patient profiles"
          icon={Users}
          color="var(--primary)"
        />
        <StatCard
          title="Active Doctors"
          value={totalDoctors}
          subtitle="Across all departments"
          icon={Stethoscope}
          color="var(--accent)"
        />
        <StatCard
          title="Hospital Departments"
          value={departments.length}
          subtitle="Clinical specialties"
          icon={Building2}
          color="var(--warning)"
        />
        <StatCard
          title="Total Appointments"
          value={appointments.length}
          subtitle={`${completedAppts} completed, ${cancelledAppts} cancelled`}
          icon={Calendar}
          color="var(--info)"
        />
      </div>

      {/* Analytics Visualization Section */}
      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} color="var(--primary)" />
            <span>Department Breakdown</span>
          </h3>
          {departments.map(d => (
            <div key={d.id} style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                <span>{d.name} ({d.code})</span>
                <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{d.doctor_count} Doctors</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${Math.min(100, (d.doctor_count || 1) * 25)}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)' }} />
              </div>
            </div>
          ))}
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={18} color="var(--accent)" />
            <span>System Health Overview</span>
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)' }}>
              <span>Database Sync</span>
              <span className="badge badge-success">MySQL / SQLite Live</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)' }}>
              <span>JWT Authentication Engine</span>
              <span className="badge badge-success">OAuth2 Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)' }}>
              <span>AI Care Navigator Agent</span>
              <span className="badge badge-info">Tool Calling Ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
