import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';

// Public Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

// Patient Pages
import { PatientDashboard } from './pages/PatientDashboard';
import { PatientAiAssistantPage } from './pages/PatientAiAssistantPage';
import { DoctorSearchPage } from './pages/DoctorSearchPage';
import { AppointmentBookingPage } from './pages/AppointmentBookingPage';
import { MyAppointmentsPage } from './pages/MyAppointmentsPage';
import { WaitlistPage } from './pages/WaitlistPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ProfilePage } from './pages/ProfilePage';

// Doctor Pages
import { DoctorDashboard } from './pages/DoctorDashboard';
import { DoctorAppointmentsPage } from './pages/DoctorAppointmentsPage';
import { DoctorAvailabilityPage } from './pages/DoctorAvailabilityPage';

// Admin Pages
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminUsersPage } from './pages/AdminUsersPage';
import { AdminDepartmentsPage } from './pages/AdminDepartmentsPage';
import { AdminAuditLogsPage } from './pages/AdminAuditLogsPage';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-main)', color: 'var(--text-muted)' }}>Loading session...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === 'PATIENT') return <Navigate to="/patient/dashboard" replace />;
    if (user.role === 'DOCTOR') return <Navigate to="/doctor/dashboard" replace />;
    if (user.role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
  }

  return children;
};

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Patient Portal */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['PATIENT']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/patient/dashboard" element={<PatientDashboard />} />
            <Route path="/patient/ai-assistant" element={<PatientAiAssistantPage />} />
            <Route path="/patient/doctors" element={<DoctorSearchPage />} />
            <Route path="/patient/book" element={<AppointmentBookingPage />} />
            <Route path="/patient/appointments" element={<MyAppointmentsPage />} />
            <Route path="/patient/waitlist" element={<WaitlistPage />} />
            <Route path="/patient/notifications" element={<NotificationsPage />} />
            <Route path="/patient/profile" element={<ProfilePage />} />
          </Route>

          {/* Protected Doctor Portal */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['DOCTOR']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
            <Route path="/doctor/appointments" element={<DoctorAppointmentsPage />} />
            <Route path="/doctor/availability" element={<DoctorAvailabilityPage />} />
            <Route path="/doctor/profile" element={<ProfilePage />} />
          </Route>

          {/* Protected Admin Portal */}
          <Route
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsersPage />} />
            <Route path="/admin/departments" element={<AdminDepartmentsPage />} />
            <Route path="/admin/audit-logs" element={<AdminAuditLogsPage />} />
          </Route>

          {/* Fallback Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
