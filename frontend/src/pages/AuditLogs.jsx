import React, { useEffect, useState } from 'react';
import { ShieldAlert, Search, Filter } from 'lucide-react';
import api from '../services/api';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [actionFilter, setActionFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs();
  }, [actionFilter]);

  const fetchAuditLogs = async () => {
    try {
      const res = await api.get('/audit-logs', {
        params: { action: actionFilter || undefined }
      });
      setLogs(res.data);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="text-2xl font-extrabold text-navy-900 flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-primary-600" />
          <span>System Audit Trail</span>
        </h1>
        <p className="text-sm text-muted">Immutable log of document uploads, AI extractions, field edits, and verifications</p>
      </div>

      {/* Action Filter */}
      <div className="bg-white p-4 rounded-xl border border-border flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-muted" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium"
          >
            <option value="">All System Actions</option>
            <option value="DOCUMENT_UPLOADED">DOCUMENT_UPLOADED</option>
            <option value="OCR_COMPLETED">OCR_COMPLETED</option>
            <option value="RECORD_EXTRACTED">RECORD_EXTRACTED</option>
            <option value="RECORD_EDITED">RECORD_EDITED</option>
            <option value="RECORD_APPROVED">RECORD_APPROVED</option>
            <option value="RECORD_REJECTED">RECORD_REJECTED</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-muted">Loading audit records...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
                <tr>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">User</th>
                  <th className="p-3.5">Action Event</th>
                  <th className="p-3.5">Target Entity</th>
                  <th className="p-3.5">Entity ID</th>
                  <th className="p-3.5">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3.5 font-mono text-xs text-muted">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3.5 font-semibold text-navy-900">{log.user_email || 'System'}</td>
                    <td className="p-3.5">
                      <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-200">
                        {log.action}
                      </span>
                    </td>
                    <td className="p-3.5 text-xs text-slate-700">{log.entity}</td>
                    <td className="p-3.5 font-mono text-xs">#{log.entity_id || '—'}</td>
                    <td className="p-3.5 text-xs font-mono text-slate-600 max-w-xs truncate">
                      {log.new_values ? JSON.stringify(log.new_values) : '—'}
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
