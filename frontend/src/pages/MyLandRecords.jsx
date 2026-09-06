import React, { useEffect, useState } from 'react';
import { FileText, Download, Eye, Search, CheckCircle2, AlertTriangle, ShieldCheck, MapPin, Building, Sparkles, X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ValidationBadge } from '../components/common/ValidationBadge';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';

export const MyLandRecords = () => {
  const { user } = useAuth();
  const toast = useToast();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    fetchMyRecords();
  }, []);

  const fetchMyRecords = async () => {
    setLoading(true);
    try {
      const res = await api.get('/land-records/my-records');
      setRecords(res.data);
    } catch (err) {
      console.error("Failed to load user land records", err);
      toast.error('Failed to load your land records.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async (recordId, surveyNumber) => {
    setDownloadingId(recordId);
    try {
      const res = await api.get(`/land-records/my-records/${recordId}/download`, {
        responseType: 'blob'
      });

      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Digital_Land_Record_${surveyNumber.replace('/', '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`Downloaded Digital Land Record for Survey #${surveyNumber}`);
    } catch (err) {
      toast.error('Failed to download land record PDF.');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredRecords = records.filter((r) => {
    const term = search.toLowerCase();
    return (
      (r.survey_number && r.survey_number.toLowerCase().includes(term)) ||
      (r.village_name && r.village_name.toLowerCase().includes(term)) ||
      (r.district_name && r.district_name.toLowerCase().includes(term)) ||
      (r.owner_name && r.owner_name.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Welcome Banner Header */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-xs flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-navy-900">My Land Records</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-primary-50 text-primary-700 border border-primary-200">
              {records.length} Records Owned
            </span>
          </div>
          <p className="text-sm text-slate-700 font-semibold mt-1">Welcome, {user?.full_name}</p>
          <p className="text-xs text-muted">Land records associated with your account</p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-muted absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search survey # or village..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Main Records Display */}
      {loading ? (
        <div className="p-16 bg-white rounded-2xl border border-border text-center text-muted">
          <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent mx-auto mb-3" />
          <p className="font-semibold text-sm">Loading your digital land records...</p>
        </div>
      ) : filteredRecords.length === 0 ? (
        <div className="p-16 bg-white rounded-2xl border border-border text-center space-y-3 shadow-xs">
          <FileText className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-navy-900">No land records are associated with your account.</h3>
          <p className="text-xs text-muted max-w-md mx-auto">
            If you recently submitted a deed or Patta extract, your record will appear here once registered.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredRecords.map((rec) => (
            <div key={rec.id} className="bg-white rounded-2xl border border-border p-6 shadow-xs hover:shadow-md transition-all space-y-4 flex flex-col justify-between">
              
              <div className="space-y-3">
                {/* Header Badge Row */}
                <div className="flex items-center justify-between gap-2 border-b border-border pb-3">
                  <div>
                    <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-muted block">Survey Number</span>
                    <span className="text-xl font-extrabold text-navy-900 font-mono">{rec.survey_number || '—'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ValidationBadge status={rec.validation_status} />
                    {rec.is_verified ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-success-50 text-success-700 border border-success-200">
                        <ShieldCheck className="w-3.5 h-3.5 text-success-600" />
                        <span>Verified</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-warning-50 text-warning-700 border border-warning-200">
                        <AlertTriangle className="w-3.5 h-3.5 text-warning-600" />
                        <span>Pending QA</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500 block font-medium">Registered Owner Name</span>
                    <span className="font-bold text-navy-900 text-sm block">{rec.owner_name || '—'}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block font-medium">Plot Extent Area</span>
                    <span className="font-bold text-navy-900 font-mono text-sm block">{rec.plot_area} {rec.area_unit}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block font-medium">Village & Tehsil</span>
                    <span className="font-semibold text-slate-800 block">{rec.village_name}, {rec.tehsil_name}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block font-medium">District</span>
                    <span className="font-semibold text-slate-800 block">{rec.district_name}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block font-medium">Khasra / Khata Number</span>
                    <span className="font-mono text-slate-800 block">{rec.khasra_number || '—'} / {rec.khata_number || '—'}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block font-medium">Land Classification</span>
                    <span className="font-semibold text-primary-700 block">{rec.land_classification || 'Agricultural'}</span>
                  </div>
                </div>

                {rec.ownership_details && (
                  <div className="pt-2 border-t border-slate-100 text-xs">
                    <span className="text-slate-500 block font-medium">Ownership Details</span>
                    <p className="text-slate-700 font-medium italic mt-0.5">{rec.ownership_details}</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-border flex items-center justify-end gap-3">
                <button
                  onClick={() => setSelectedRecord(rec)}
                  className="px-4 py-2 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl flex items-center gap-1.5 transition-colors"
                >
                  <Eye className="w-3.5 h-3.5 text-primary-600" />
                  <span>View Details</span>
                </button>

                <button
                  onClick={() => handleDownloadPDF(rec.id, rec.survey_number)}
                  disabled={downloadingId === rec.id}
                  className="px-4 py-2 text-xs font-bold bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-xl shadow-xs flex items-center gap-1.5 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>{downloadingId === rec.id ? 'Generating PDF...' : 'Download Record'}</span>
                </button>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Record View Detail Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-border shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-5 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <h3 className="text-lg font-bold text-navy-900">Digital Land Record Certificate</h3>
                <p className="text-xs text-muted">Survey #{selectedRecord.survey_number} • Registered to {selectedRecord.owner_name}</p>
              </div>
              <button onClick={() => setSelectedRecord(null)} className="p-1.5 text-slate-400 hover:text-navy-900 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div>
                  <span className="text-slate-500 block font-medium">Owner Name</span>
                  <span className="font-bold text-navy-900 text-sm">{selectedRecord.owner_name}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Survey Number</span>
                  <span className="font-mono font-bold text-navy-900 text-sm">{selectedRecord.survey_number}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Khasra Number</span>
                  <span className="font-mono font-semibold">{selectedRecord.khasra_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Khata Number</span>
                  <span className="font-mono font-semibold">{selectedRecord.khata_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Plot Area</span>
                  <span className="font-mono font-bold">{selectedRecord.plot_area} {selectedRecord.area_unit}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Land Classification</span>
                  <span className="font-semibold text-primary-700">{selectedRecord.land_classification}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Village</span>
                  <span className="font-semibold">{selectedRecord.village_name}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Tehsil</span>
                  <span className="font-semibold">{selectedRecord.tehsil_name}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">District</span>
                  <span className="font-semibold">{selectedRecord.district_name}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Mutation Number</span>
                  <span className="font-mono font-semibold">{selectedRecord.mutation_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Registration Number</span>
                  <span className="font-mono font-semibold">{selectedRecord.registration_number || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-medium">Validation Status</span>
                  <ValidationBadge status={selectedRecord.validation_status} />
                </div>
              </div>

              <div>
                <span className="text-slate-500 block font-medium mb-1">Ownership Details</span>
                <p className="p-3 bg-slate-50 rounded-lg text-slate-800 font-medium">
                  {selectedRecord.ownership_details || 'Sole ownership record registered in government revenue ledger.'}
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-border flex justify-end gap-3">
              <button
                onClick={() => setSelectedRecord(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl"
              >
                Close
              </button>
              <button
                onClick={() => {
                  handleDownloadPDF(selectedRecord.id, selectedRecord.survey_number);
                  setSelectedRecord(null);
                }}
                className="px-5 py-2 bg-primary-600 hover:bg-primary-700 text-white font-bold text-xs rounded-xl shadow-xs flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF</span>
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
