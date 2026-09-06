import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Search, Filter, Eye, Plus } from 'lucide-react';
import api from '../services/api';
import { ValidationBadge } from '../components/common/ValidationBadge';

export const DocumentsList = () => {
  const [documents, setDocuments] = useState([]);
  const [search, setSearch] = useState('');
  const [docType, setDocType] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, [search, docType]);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents', {
        params: { search: search || undefined, doc_type: docType || undefined }
      });
      setDocuments(res.data);
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Title & Upload Button */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-900">Documents Library</h1>
          <p className="text-sm text-muted">All uploaded legacy land records, Patta extracts, and deeds</p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-sm rounded-xl shadow-md flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-border flex items-center justify-between gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-muted absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by file name..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-muted" />
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium"
          >
            <option value="">All Document Types</option>
            <option value="Ownership Record">Ownership Record</option>
            <option value="Mutation Record">Mutation Record</option>
            <option value="Sale / Registration Record">Sale / Registration Record</option>
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-muted">Loading documents library...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center text-muted space-y-3">
            <FileText className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="font-semibold text-navy-900">No documents found</p>
            <p className="text-xs text-muted">Upload a land record document to start digitization.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
                <tr>
                  <th className="p-3.5">ID</th>
                  <th className="p-3.5">Document File</th>
                  <th className="p-3.5">Category</th>
                  <th className="p-3.5">Language</th>
                  <th className="p-3.5">Pipeline Stage</th>
                  <th className="p-3.5">Uploaded Date</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3.5 font-mono text-xs text-muted">#{doc.id}</td>
                    <td className="p-3.5 font-semibold text-navy-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary-600 shrink-0" />
                      <span>{doc.original_filename}</span>
                    </td>
                    <td className="p-3.5 text-xs text-slate-700">{doc.document_type}</td>
                    <td className="p-3.5 text-xs font-mono">{doc.language}</td>
                    <td className="p-3.5 text-xs font-mono text-primary-700 font-semibold">{doc.processing_stage}</td>
                    <td className="p-3.5 text-xs font-mono text-muted">{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        className="px-3 py-1.5 bg-primary-50 text-primary-600 hover:bg-primary-100 rounded-lg text-xs font-bold transition-colors inline-flex items-center gap-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect Data</span>
                      </button>
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
