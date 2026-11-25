import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal } from '../components/Modal';
import { Building2, Plus, Edit2, Trash2 } from 'lucide-react';

export const AdminDepartmentsPage = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showAddModal, setShowAddModal] = useState(false);
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [icon, setIcon] = useState('stethoscope');

  const fetchDepartments = async () => {
    try {
      const res = await api.get('/departments?include_inactive=true');
      setDepartments(res.data);
    } catch (err) {
      console.error('Error fetching departments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDepartments();
  }, []);

  const handleCreateDepartment = async (e) => {
    e.preventDefault();
    try {
      await api.post('/departments', {
        name,
        code,
        description,
        icon
      });
      setShowAddModal(false);
      setName('');
      setCode('');
      setDescription('');
      fetchDepartments();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create department.');
    }
  };

  const handleDeactivate = async (id) => {
    try {
      await api.delete(`/departments/${id}`);
      fetchDepartments();
    } catch (err) {
      alert('Failed to deactivate department.');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Hospital Departments</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Manage clinical specialties and medical department units.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          <Plus size={18} />
          <span>Add Department</span>
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading departments...</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Dept ID</th>
                  <th>Name</th>
                  <th>Code</th>
                  <th>Description</th>
                  <th>Doctors Assigned</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {departments.map(d => (
                  <tr key={d.id}>
                    <td><span className="badge badge-info">#{d.id}</span></td>
                    <td style={{ fontWeight: 600 }}>{d.name}</td>
                    <td><span className="badge badge-warning">{d.code}</span></td>
                    <td style={{ maxWidth: '260px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {d.description || 'N/A'}
                    </td>
                    <td>{d.doctor_count || 0} Doctors</td>
                    <td>
                      <span className={`badge ${d.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {d.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      {d.is_active && (
                        <button className="btn btn-danger" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }} onClick={() => handleDeactivate(d.id)}>
                          <Trash2 size={14} />
                          <span>Deactivate</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      <Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Create New Department">
        <form onSubmit={handleCreateDepartment}>
          <div className="form-group">
            <label className="form-label">Department Name</label>
            <input type="text" className="form-input" required placeholder="e.g. Oncology" value={name} onChange={(e) => setName(e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label">Department Code</label>
            <input type="text" className="form-input" required placeholder="e.g. ONCO" value={code} onChange={(e) => setCode(e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-textarea" rows="3" placeholder="Department description..." value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.8rem', marginTop: '1.5rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create Department</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
