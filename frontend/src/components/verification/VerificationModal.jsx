import React, { useState } from 'react';
import { X, CheckCircle2, XCircle, Save, AlertTriangle, Copy, ShieldAlert } from 'lucide-react';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { ValidationBadge } from '../common/ValidationBadge';

export const VerificationModal = ({ record, extraction, onClose, onApprove, onReject, onUpdate }) => {
  const [formData, setFormData] = useState({
    owner_name: record?.owner_name || '',
    survey_number: record?.survey_number || '',
    khasra_number: record?.khasra_number || '',
    khata_number: record?.khata_number || '',
    plot_area: record?.plot_area || '',
    district_name: record?.district_name || '',
    tehsil_name: record?.tehsil_name || '',
    village_name: record?.village_name || '',
    land_classification: record?.land_classification || '',
    mutation_number: record?.mutation_number || ''
  });

  const [comments, setComments] = useState('');
  const [editing, setEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSubmitting(true);
    await onUpdate(record.id, formData);
    setSubmitting(false);
    setEditing(false);
  };

  const handleApprove = async () => {
    setSubmitting(true);
    await onApprove(record.id, comments || 'Approved by verifier');
    setSubmitting(false);
  };

  const handleReject = async () => {
    if (!comments.trim()) {
      alert('Rejection requires a comment detailing the reason.');
      return;
    }
    setSubmitting(true);
    await onReject(record.id, comments);
    setSubmitting(false);
  };

  const validationInfo = extraction?.validation || {};

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-border shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-slate-50">
          <div>
            <h2 className="text-lg font-bold text-navy-900 flex items-center gap-2">
              <span>Human Verification: Record #{record.id}</span>
              <ValidationBadge status={record.validation_status} />
            </h2>
            <p className="text-xs text-muted">Review document, correct errors, and approve/reject record into DB</p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-navy-900 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content - 2 Column Layout */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Left Column: Original Document */}
          <div className="bg-slate-900 rounded-xl p-3 flex flex-col items-center justify-center min-h-[450px]">
            <img
              src={`/api/documents/${record.document_id}/file`}
              alt="Document"
              className="max-h-[500px] object-contain bg-white rounded shadow-md"
              onError={(e) => {
                e.target.src = "https://placehold.co/600x800/f8fafc/0f172a?text=Document+Preview";
              }}
            />
          </div>

          {/* Right Column: Editable Fields & Validation Alerts */}
          <div className="space-y-5 flex flex-col">
            
            {/* Validation Warnings Box */}
            {(validationInfo.warnings?.length > 0 || validationInfo.errors?.length > 0 || validationInfo.duplicate_detected) && (
              <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 space-y-2 text-xs">
                <div className="font-bold text-amber-800 flex items-center gap-1.5 text-sm">
                  <ShieldAlert className="w-4 h-4 text-amber-600" />
                  <span>Validation & Duplicate Flags</span>
                </div>
                {validationInfo.errors?.map((err, idx) => (
                  <p key={idx} className="text-error-600 font-medium">✕ {err}</p>
                ))}
                {validationInfo.warnings?.map((warn, idx) => (
                  <p key={idx} className="text-amber-700">⚠ {warn}</p>
                ))}
                {validationInfo.duplicate_detected && (
                  <div className="p-2 bg-purple-100 rounded text-purple-800 font-semibold flex items-center gap-1">
                    <Copy className="w-4 h-4" />
                    <span>Fuzzy Duplicate Match: Record #{validationInfo.duplicate_record_id} ({int(validationInfo.similarity_score * 100)}% match)</span>
                  </div>
                )}
              </div>
            )}

            {/* Editable Fields Form */}
            <div className="space-y-3 flex-1">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-bold text-navy-900">Extracted Data Fields</h3>
                <ConfidenceBadge score={record.confidence_score} level={record.confidence_level} />
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="font-medium text-slate-700 block mb-1">Owner Name</label>
                  <input
                    type="text"
                    value={formData.owner_name}
                    onChange={(e) => handleInputChange('owner_name', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 font-semibold"
                  />
                </div>

                <div>
                  <label className="font-medium text-slate-700 block mb-1">Survey Number</label>
                  <input
                    type="text"
                    value={formData.survey_number}
                    onChange={(e) => handleInputChange('survey_number', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 font-mono font-semibold"
                  />
                </div>

                <div>
                  <label className="font-medium text-slate-700 block mb-1">Plot Area (Acres)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.plot_area}
                    onChange={(e) => handleInputChange('plot_area', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 font-mono"
                  />
                </div>

                <div>
                  <label className="font-medium text-slate-700 block mb-1">District</label>
                  <input
                    type="text"
                    value={formData.district_name}
                    onChange={(e) => handleInputChange('district_name', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="font-medium text-slate-700 block mb-1">Tehsil</label>
                  <input
                    type="text"
                    value={formData.tehsil_name}
                    onChange={(e) => handleInputChange('tehsil_name', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="font-medium text-slate-700 block mb-1">Village</label>
                  <input
                    type="text"
                    value={formData.village_name}
                    onChange={(e) => handleInputChange('village_name', e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  onClick={handleSave}
                  disabled={submitting}
                  className="px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium flex items-center gap-1"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>Save Edits</span>
                </button>
              </div>

              {/* Verifier Comments */}
              <div className="pt-2">
                <label className="font-medium text-slate-700 block mb-1 text-xs">
                  Verifier Comments / Rejection Reason <span className="text-error-500">* (Mandatory for rejection)</span>
                </label>
                <textarea
                  rows="2"
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  placeholder="Enter notes or audit justification..."
                  className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 border-t border-border flex items-center justify-end gap-3">
              <button
                onClick={handleReject}
                disabled={submitting}
                className="px-4 py-2 bg-error-50 text-error-600 hover:bg-error-100 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors"
              >
                <XCircle className="w-4 h-4" />
                <span>Reject Record</span>
              </button>

              <button
                onClick={handleApprove}
                disabled={submitting}
                className="px-5 py-2 bg-success-600 text-white hover:bg-success-700 font-bold text-xs rounded-xl flex items-center gap-1.5 shadow-sm transition-colors"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve Record</span>
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
