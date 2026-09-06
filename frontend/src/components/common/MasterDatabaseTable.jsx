import React, { useEffect, useState } from 'react';
import { Database, ShieldCheck, RefreshCw } from 'lucide-react';
import api from '../../services/api';

export const MasterDatabaseTable = () => {
  const [masterRecords, setMasterRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMasterRecords = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/master/records');
      setMasterRecords(res.data);
    } catch (err) {
      console.error('Failed to load master database records:', err);
      setError('Failed to load Master Database records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMasterRecords();
  }, []);

  return (
    <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
      <div className="p-4 bg-slate-50 border-b border-border flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-primary-600" />
          <h3 className="text-sm font-bold text-navy-900">Authoritative Master Database Records</h3>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-mono font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            {masterRecords.length} Authoritative Records
          </span>
        </div>
        <button
          onClick={fetchMasterRecords}
          className="text-xs font-semibold text-slate-600 hover:text-primary-600 flex items-center gap-1 transition-colors"
          title="Refresh Master DB"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-muted">Loading Master Database records...</div>
      ) : error ? (
        <div className="p-6 text-center text-xs text-red-500">{error}</div>
      ) : masterRecords.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted">No Master Database records found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">Owner Name</th>
                <th className="p-3.5">Survey No.</th>
                <th className="p-3.5">Khata / Khasra</th>
                <th className="p-3.5">Area</th>
                <th className="p-3.5">Village</th>
                <th className="p-3.5">Tehsil</th>
                <th className="p-3.5">District</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {masterRecords.map((record) => (
                <tr key={record.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3.5 font-mono text-xs text-muted">#{record.id}</td>
                  <td className="p-3.5 font-semibold text-navy-900">{record.owner_name}</td>
                  <td className="p-3.5 font-mono text-xs font-semibold text-primary-700">{record.survey_number}</td>
                  <td className="p-3.5 font-mono text-xs text-slate-600">
                    {record.khata_number ? `Khata: ${record.khata_number}` : ''}
                    {record.khasra_number ? ` / Khasra: ${record.khasra_number}` : ''}
                  </td>
                  <td className="p-3.5 text-xs font-medium text-slate-700">
                    {record.plot_area} {record.area_unit || 'Acres'}
                  </td>
                  <td className="p-3.5 text-xs text-slate-800">{record.village_name}</td>
                  <td className="p-3.5 text-xs text-slate-800">{record.tehsil_name}</td>
                  <td className="p-3.5 text-xs font-semibold text-slate-900">{record.district_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
