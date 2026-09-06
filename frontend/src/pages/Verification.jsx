import React, { useEffect, useState } from 'react';
import { CheckSquare, Search, Filter, ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { ValidationBadge } from '../components/common/ValidationBadge';
import { MasterDatabaseTable } from '../components/common/MasterDatabaseTable';
import { VerificationModal } from '../components/verification/VerificationModal';

export const Verification = () => {
  const [pendingRecords, setPendingRecords] = useState([]);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [selectedExtraction, setSelectedExtraction] = useState(null);
  const [districtFilter, setDistrictFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const toast = useToast();

  useEffect(() => {
    fetchPendingRecords();
  }, [districtFilter, statusFilter]);

  const fetchPendingRecords = async () => {
    try {
      const res = await api.get('/verification/pending', {
        params: { district: districtFilter || undefined, status: statusFilter || undefined }
      });
      setPendingRecords(res.data);
    } catch (err) {
      console.error("Failed to fetch verification queue", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenVerification = async (record) => {
    try {
      const extRes = await api.get(`/documents/${record.document_id}/extraction`);
      setSelectedExtraction(extRes.data);
      setSelectedRecord(record);
    } catch (err) {
      toast.error('Could not load record details for verification.');
    }
  };

  const handleUpdateRecord = async (recordId, updatedFields) => {
    try {
      await api.put(`/verification/${recordId}/record`, updatedFields);
      toast.success('Fields updated successfully!');
      fetchPendingRecords();
      setSelectedRecord(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update fields');
    }
  };

  const handleApproveRecord = async (recordId, comments) => {
    try {
      await api.post(`/verification/${recordId}/approve`, { comments });
      toast.success(`Record #${recordId} approved and verified!`);
      fetchPendingRecords();
      setSelectedRecord(null);
    } catch (err) {
      toast.error('Approval failed');
    }
  };

  const handleRejectRecord = async (recordId, comments) => {
    try {
      await api.post(`/verification/${recordId}/reject`, { comments });
      toast.warning(`Record #${recordId} rejected.`);
      fetchPendingRecords();
      setSelectedRecord(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Rejection failed');
    }
  };

  return (
    <div className="space-y-6">
      
      <div>
        <h1 className="text-2xl font-extrabold text-navy-900 flex items-center gap-2">
          <span>Human Verification Queue</span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-warning-100 text-warning-700 font-mono font-bold">
            {pendingRecords.length} Pending
          </span>
        </h1>
        <p className="text-sm text-muted">Records with warnings, low confidence, or fuzzy duplicates requiring human QA</p>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-border flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-muted" />
          <select
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium"
          >
            <option value="">All Districts</option>
            <option value="Kancheepuram">Kancheepuram</option>
            <option value="Chengalpattu">Chengalpattu</option>
            <option value="Coimbatore">Coimbatore</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium"
          >
            <option value="">All Validation Statuses</option>
            <option value="WARNING">Needs Review (WARNING)</option>
            <option value="INVALID">Invalid Format (INVALID)</option>
            <option value="DUPLICATE">Potential Duplicate (DUPLICATE)</option>
          </select>
        </div>
      </div>

      {/* Queue Table */}
      <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-muted">Loading pending verification queue...</div>
        ) : pendingRecords.length === 0 ? (
          <div className="p-12 text-center text-muted space-y-2">
            <CheckCircle2 className="w-10 h-10 text-success-500 mx-auto" />
            <p className="font-bold text-navy-900">Verification Queue Clear!</p>
            <p className="text-xs text-muted">All digitized land records have been verified or resolved.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
                <tr>
                  <th className="p-3.5">Record ID</th>
                  <th className="p-3.5">Owner Name</th>
                  <th className="p-3.5">Survey Number</th>
                  <th className="p-3.5">District / Village</th>
                  <th className="p-3.5">Confidence</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {pendingRecords.map((rec) => (
                  <tr key={rec.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3.5 font-mono text-xs text-muted">#{rec.id}</td>
                    <td className="p-3.5 font-semibold text-navy-900">{rec.owner_name || '—'}</td>
                    <td className="p-3.5 font-mono text-xs font-semibold">{rec.survey_number || '—'}</td>
                    <td className="p-3.5 text-xs text-slate-700">
                      {rec.village_name}, {rec.district_name}
                    </td>
                    <td className="p-3.5">
                      <ConfidenceBadge score={rec.confidence_score} level={rec.confidence_level} />
                    </td>
                    <td className="p-3.5">
                      <ValidationBadge status={rec.validation_status} />
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => handleOpenVerification(rec)}
                        className="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-xs rounded-lg shadow-xs transition-all inline-flex items-center gap-1"
                      >
                        <CheckSquare className="w-3.5 h-3.5" />
                        <span>Verify & Edit</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Authoritative Master Database Section */}
      <MasterDatabaseTable />

      {/* Verification Modal */}
      {selectedRecord && (
        <VerificationModal
          record={selectedRecord}
          extraction={selectedExtraction}
          onClose={() => setSelectedRecord(null)}
          onApprove={handleApproveRecord}
          onReject={handleRejectRecord}
          onUpdate={handleUpdateRecord}
        />
      )}

    </div>
  );
};
