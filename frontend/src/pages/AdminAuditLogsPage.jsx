import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ShieldAlert, Clock, Filter } from 'lucide-react';

export const AdminAuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get('/admin/audit-logs');
        setLogs(res.data);
      } catch (err) {
        console.error('Error fetching audit logs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>System Security Audit Logs</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Immutable event tracking for logins, appointments, profile updates, and administrative changes.</p>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading audit logs...</p>
        ) : logs.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>No audit records found.</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Log ID</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>User ID</th>
                  <th>IP Address</th>
                  <th>Timestamp</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id}>
                    <td><span className="badge badge-info">#{log.id}</span></td>
                    <td><span className="badge badge-success">{log.action}</span></td>
                    <td style={{ fontWeight: 600 }}>{log.resource}</td>
                    <td>{log.user_id ? `User #${log.user_id}` : 'System'}</td>
                    <td>{log.ip_address || '127.0.0.1'}</td>
                    <td>{new Date(log.created_at).toLocaleString()}</td>
                    <td style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontStyle: 'italic', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {log.details_json ? JSON.stringify(log.details_json) : 'N/A'}
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
