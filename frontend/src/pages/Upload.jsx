import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ArrowRight, AlertCircle, ShieldAlert } from 'lucide-react';
import api from '../services/api';
import { useToast } from '../context/ToastContext';
import { ProcessingStepper } from '../components/document/ProcessingStepper';

export const Upload = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('English');
  const [docType, setDocType] = useState('Ownership Record');
  const [uploading, setUploading] = useState(false);
  const [currentDoc, setCurrentDoc] = useState(null);
  const [processingStage, setProcessingStage] = useState(1);
  const [processingStatus, setProcessingStatus] = useState('IDLE');
  const [errorMessage, setErrorMessage] = useState(null);
  const [isDuplicateFile, setIsDuplicateFile] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setIsDuplicateFile(false);
      setErrorMessage(null);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setIsDuplicateFile(false);
      setErrorMessage(null);
    }
  };

  const handleUploadAndProcess = async () => {
    if (!file) {
      toast.error('Please drag & drop or select a land record document to upload.');
      return;
    }

    setUploading(true);
    setProcessingStatus('PROCESSING');
    setProcessingStage(1);
    setErrorMessage(null);
    setIsDuplicateFile(false);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('language', language);
      formData.append('document_type', docType);

      const uploadRes = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const docData = uploadRes.data;

      // Handle SHA-256 Exact File Duplicate
      if (docData.status === 'DUPLICATE_DOCUMENT') {
        setIsDuplicateFile(true);
        setProcessingStatus('FAILED');
        const msg = "Duplicate document detected. This exact file has already been uploaded.";
        setErrorMessage(msg);
        toast.error("Duplicate document detected.");
        return;
      }

      setCurrentDoc(docData);
      toast.info('Document uploaded. Executing AI extraction pipeline...');
      setProcessingStage(3);

      // Trigger live backend processing endpoint
      const documentId = docData.id;
      const baseURL = api.defaults.baseURL || '/api';
      const endpoint = `/documents/${documentId}/process`;
      const url = baseURL.endsWith('/') ? `${baseURL.slice(0, -1)}${endpoint}` : `${baseURL}${endpoint}`;
      const token = localStorage.getItem('token');

      console.log("[PROCESS] START", documentId);
      console.log("[PROCESS] API URL", url);
      console.log("[PROCESS] TOKEN EXISTS", Boolean(token));
      console.log("[PROCESS] TOKEN LENGTH", token ? token.length : 0);

      const processRes = await api.post(`/documents/${documentId}/process`, {}, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log("[PROCESS] RESPONSE STATUS", processRes.status);
      console.log("[PROCESS] RESPONSE DATA", processRes.data);

      setProcessingStage(7);
      setProcessingStatus('COMPLETED');
      toast.success('Document digitized and validated successfully!');

      navigate(`/documents/${docData.id}`);

    } catch (err) {
      console.error("[PROCESS] ERROR MESSAGE", err.message);
      console.error("[PROCESS] ERROR CODE", err.code);
      console.error("[PROCESS] ERROR STATUS", err.response?.status);
      console.error("[PROCESS] ERROR DATA", err.response?.data);
      console.error("[PROCESS] ERROR HEADERS", err.response?.headers);

      setProcessingStatus('FAILED');

      let detailStr = '';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          detailStr = detail;
        } else if (typeof detail === 'object' && detail !== null) {
          if (Array.isArray(detail)) {
            detailStr = detail.map(d => d.msg || JSON.stringify(d)).join(', ');
          } else {
            detailStr = detail.error || detail.message || JSON.stringify(detail);
          }
        }
      } else if (err.response?.data?.message) {
        detailStr = err.response.data.message;
      } else if (err.response?.status) {
        detailStr = `HTTP ${err.response.status}`;
      } else if (err.message) {
        detailStr = err.message;
      } else {
        detailStr = 'Document processing failed';
      }

      const statusPrefix = err.response?.status ? `HTTP ${err.response.status} - ` : '';
      const msg = `Document processing failed: ${statusPrefix}${detailStr}`;

      setErrorMessage(msg);
      toast.error(msg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      <div>
        <h1 className="text-2xl font-extrabold text-navy-900">Upload Land Record Document</h1>
        <p className="text-sm text-muted">Upload scanned Patta, Chitta, Mutation, or Sale deed records for AI extraction & Master DB validation</p>
      </div>

      {/* SHA-256 Duplicate Document Warning Banner */}
      {isDuplicateFile && (
        <div className="p-5 rounded-2xl bg-rose-50 border-2 border-rose-300 space-y-2 shadow-sm">
          <div className="flex items-center gap-3 text-rose-900 font-extrabold text-base">
            <ShieldAlert className="w-6 h-6 text-rose-600 shrink-0" />
            <span>Duplicate Document</span>
          </div>
          <p className="text-sm text-rose-800 font-semibold pl-9">
            This exact file has already been uploaded and cannot be added again.
          </p>
          <p className="text-xs text-rose-600 font-mono pl-9">
            SHA-256 hash collision blocked duplicate creation in Master Registry and Human Verification Queue.
          </p>
        </div>
      )}

      {/* Stepper Pipeline Progress Display */}
      {processingStatus !== 'IDLE' && !isDuplicateFile && (
        <ProcessingStepper stage={processingStage} status={processingStatus} error={errorMessage} />
      )}

      {/* Upload Settings Form */}
      <div className="bg-white p-6 rounded-2xl border border-border shadow-xs space-y-6">
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Document Category</label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 font-medium"
            >
              <option value="Ownership Record">Ownership Record (Patta / Record of Rights)</option>
              <option value="Mutation Record">Mutation Record (Chitta / Transfer Order)</option>
              <option value="Sale / Registration Record">Sale / Registration Record (Deed)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Primary Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 font-medium"
            >
              <option value="English">English</option>
              <option value="Tamil">Tamil (தமிழ்)</option>
              <option value="Auto Detect">Auto Detect Language</option>
            </select>
          </div>
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
            file ? 'border-primary-500 bg-primary-50/50' : 'border-slate-300 hover:border-primary-500 hover:bg-slate-50'
          }`}
        >
          <input
            type="file"
            id="file-upload"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileSelect}
            className="hidden"
          />

          <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
            <div className="w-14 h-14 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center mx-auto shadow-xs">
              <UploadCloud className="w-8 h-8" />
            </div>
            
            <div>
              <p className="text-sm font-bold text-navy-900">
                {file ? file.name : 'Click to upload or drag and drop document'}
              </p>
              <p className="text-xs text-muted mt-1">Supports PDF, PNG, JPG, JPEG up to 15 MB</p>
            </div>

            {file && (
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white rounded-lg border text-xs font-mono font-semibold text-primary-700 shadow-xs">
                <FileText className="w-4 h-4 text-primary-600" />
                <span>{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            )}
          </label>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleUploadAndProcess}
            disabled={uploading || !file}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md flex items-center gap-2 transition-all"
          >
            <span>{uploading ? 'Processing AI Pipeline...' : 'Start Digitization & Validation'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};
