import React, { useEffect, useState } from 'react';
import { Users as UsersIcon, UserPlus, Shield, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import { useToast } from '../context/ToastContext';

export const Users = () => {
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'VIEWER'
  });

  const toast = useToast();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users');
      setUsers(res.data);
    } catch (err) {
      console.error("Failed to load users", err);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await api.post('/users', formData);
      toast.success(`User '${formData.email}' created successfully!`);
      setShowModal(false);
      setFormData({ email: '', full_name: '', password: '', role: 'VIEWER' });
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'User creation failed');
    }
  };

  return (
    <div className="space-y-6">
      
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-900 flex items-center gap-2">
            <UsersIcon className="w-6 h-6 text-primary-600" />
            <span>User Management & RBAC Roles</span>
          </h1>
          <p className="text-sm text-muted">Manage system administrators, document verifiers, and portal viewers</p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-sm rounded-xl shadow-md flex items-center gap-2"
        >
          <UserPlus className="w-4 h-4" />
          <span>Add New User</span>
        </button>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">Full Name</th>
                <th className="p-3.5">Email Address</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Created Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3.5 font-mono text-xs text-muted">#{u.id}</td>
                  <td className="p-3.5 font-bold text-navy-900">{u.full_name}</td>
                  <td className="p-3.5 font-mono text-xs text-slate-700">{u.email}</td>
                  <td className="p-3.5">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold ${
                      u.role === 'ADMIN' ? 'bg-error-50 text-error-600 border border-error-200' :
                      u.role === 'VERIFIER' ? 'bg-warning-50 text-warning-700 border border-warning-200' :
                      'bg-success-50 text-success-700 border border-success-200'
                    }`}>
                      <Shield className="w-3 h-3" />
                      <span>{u.role}</span>
                    </span>
                  </td>
                  <td className="p-3.5 text-xs">
                    <span className="inline-flex items-center gap-1 text-success-600 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Active</span>
                    </span>
                  </td>
                  <td className="p-3.5 text-xs font-mono text-muted">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-border shadow-2xl max-w-md w-full p-6 space-y-4">
            <h2 className="text-lg font-bold text-navy-900">Create New System Account</h2>

            <form onSubmit={handleCreateUser} className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="e.g. Ramesh Kumar"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="user@landgov.in"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">System Role</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg font-semibold"
                >
                  <option value="VIEWER">VIEWER (Read-only)</option>
                  <option value="VERIFIER">VERIFIER (Can verify & edit)</option>
                  <option value="ADMIN">ADMIN (Full permissions)</option>
                </select>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-primary-600 hover:bg-primary-700 text-white font-bold text-xs rounded-xl shadow-xs"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
