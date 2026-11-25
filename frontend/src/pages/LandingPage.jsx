import React from 'react';
import { Link } from 'react-router-dom';
import {
  Stethoscope,
  Bot,
  Clock,
  Sparkles,
  ArrowRight,
  Users,
  AlertTriangle,
  ShieldCheck,
  CalendarCheck
} from 'lucide-react';

export const LandingPage = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-main)', color: 'var(--text-main)', overflowX: 'hidden' }}>
      {/* Navigation Header */}
      <nav
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.1rem 2.5rem',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(8px)',
          borderBottom: '1px solid var(--border)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          flexWrap: 'wrap',
          gap: '1rem'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <div className="brand-mark">
            <Stethoscope size={22} color="#ffffff" />
          </div>
          <span style={{ fontSize: '1.3rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-main)' }}>
            AI Health <span style={{ color: 'var(--primary)' }}>Navigator</span>
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.85rem', alignItems: 'center' }}>
          <Link to="/login" className="btn btn-secondary">Login</Link>
          <Link to="/register" className="btn btn-primary">
            <span>Get Started</span>
            <ArrowRight size={16} />
          </Link>
        </div>
      </nav>

      {/* Hero Section with Healthcare Visual & Soft Clinical Overlay */}
      <section
        style={{
          position: 'relative',
          backgroundImage: `linear-gradient(95deg, rgba(248, 250, 252, 0.96) 0%, rgba(248, 250, 252, 0.88) 52%, rgba(219, 234, 254, 0.45) 100%), url('/images/hero-healthcare.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center right',
          borderBottom: '1px solid var(--border)'
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '5rem 2rem',
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 1.15fr) minmax(0, 0.85fr)',
            gap: '2rem',
            alignItems: 'center'
          }}
        >
          <div>
            <div className="badge badge-teal" style={{ marginBottom: '1.25rem', padding: '0.45rem 0.95rem', fontSize: '0.82rem' }}>
              <Sparkles size={15} />
              <span>AI-Powered Administrative Healthcare Navigator</span>
            </div>

            <h1
              style={{
                fontSize: 'clamp(2.1rem, 4vw, 3.25rem)',
                fontWeight: 800,
                lineHeight: 1.14,
                marginBottom: '1.25rem',
                color: 'var(--text-main)'
              }}
            >
              Next-Generation{' '}
              <span style={{ color: 'var(--primary)' }}>Smart Healthcare</span>{' '}
              &amp; <span style={{ color: 'var(--secondary)' }}>Appointment</span> Platform
            </h1>

            <p style={{ fontSize: '1.1rem', color: 'var(--text-dark)', maxWidth: '620px', marginBottom: '2rem', lineHeight: 1.65 }}>
              Streamlining hospital administration with AI Care Navigation, transparent Doctor Matching, Automated Slot Generation, Smart Waitlists, and Live Queue Tracking.
            </p>

            <div style={{ display: 'flex', gap: '0.9rem', flexWrap: 'wrap' }}>
              <Link to="/register" className="btn btn-primary" style={{ padding: '0.85rem 1.85rem', fontSize: '0.98rem' }}>
                <CalendarCheck size={18} />
                <span>Book Appointment Now</span>
              </Link>
              <Link to="/login" className="btn btn-secondary" style={{ padding: '0.85rem 1.85rem', fontSize: '0.98rem' }}>
                <Bot size={18} color="var(--secondary)" />
                <span>Try AI Assistant</span>
              </Link>
            </div>

            <div style={{ display: 'flex', gap: '1.5rem', marginTop: '2rem', flexWrap: 'wrap', color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 500 }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <ShieldCheck size={16} color="var(--secondary)" /> Role-Based Clinical Portals
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                <Clock size={16} color="var(--primary)" /> Real-Time Slot Availability
              </span>
            </div>
          </div>
          <div />
        </div>
      </section>

      {/* Disclaimer Banner */}
      <div style={{ maxWidth: '1160px', margin: '2.5rem auto 0', padding: '0 2rem' }}>
        <div className="alert alert-warning" style={{ marginBottom: 0 }}>
          <AlertTriangle size={22} color="var(--warning)" style={{ flexShrink: 0 }} />
          <p style={{ fontSize: '0.86rem', lineHeight: 1.45 }}>
            <strong>Administrative Notice:</strong> This platform is strictly an administrative healthcare navigation tool. It does NOT diagnose diseases, prescribe medication, or replace medical professionals.
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <section style={{ maxWidth: '1200px', margin: '0 auto', padding: '3.5rem 2rem 5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.75rem' }}>
          <span className="badge badge-info" style={{ marginBottom: '0.6rem' }}>Platform Capabilities</span>
          <h2 style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--text-main)' }}>Core SaaS Features</h2>
        </div>

        <div className="grid-3">
          <div className="glass-panel glass-card-interactive" style={{ padding: '2rem' }}>
            <div style={{ width: '50px', height: '50px', borderRadius: '14px', background: 'var(--light-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.2rem' }}>
              <Bot size={26} color="var(--primary)" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.6rem' }}>AI Care Navigator</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Convert natural language requests into structured department routing and specialist recommendations instantly.
            </p>
          </div>

          <div className="glass-panel glass-card-interactive" style={{ padding: '2rem' }}>
            <div style={{ width: '50px', height: '50px', borderRadius: '14px', background: 'var(--light-teal)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.2rem' }}>
              <Users size={26} color="var(--secondary)" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.6rem' }}>Smart Doctor Matching</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Match doctors based on specialty, availability, fee, and patient preferences with transparent match scores.
            </p>
          </div>

          <div className="glass-panel glass-card-interactive" style={{ padding: '2rem' }}>
            <div style={{ width: '50px', height: '50px', borderRadius: '14px', background: '#FEF3C7', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.2rem' }}>
              <Clock size={26} color="var(--warning)" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.6rem' }}>Smart Waitlist &amp; Live Queue</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Position-tracked waiting queue with automatic slot notification triggers and real-time wait estimations.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ background: 'var(--bg-card)', borderTop: '1px solid var(--border)', padding: '2rem 3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <p>© 2026 AI-Powered Smart Healthcare &amp; Appointment Platform. Production SaaS Architecture.</p>
      </footer>
    </div>
  );
};
