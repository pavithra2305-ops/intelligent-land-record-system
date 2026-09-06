import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, CheckCircle2, AlertTriangle, Clock, ShieldCheck, Activity, ArrowUpRight, BarChart3
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import api from '../services/api';
import { StatCard } from '../components/common/StatCard';
import { ConfidenceBadge } from '../components/common/ConfidenceBadge';
import { ValidationBadge } from '../components/common/ValidationBadge';
import { MasterDatabaseTable } from '../components/common/MasterDatabaseTable';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const res = await api.get('/dashboard/statistics');
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load statistics", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Page Title & Controls */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-navy-900">Land Record Digitization Analytics</h1>
          <p className="text-sm text-muted">Real-time database statistics & AI validation metrics</p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="px-4 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-bold text-sm rounded-xl shadow-md flex items-center gap-2 transition-all"
        >
          <FileText className="w-4 h-4" />
          <span>Upload New Record</span>
        </button>
      </div>

      {/* Top 6 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard title="Total Docs" value={stats.total_documents} icon={FileText} color="blue" trend="+12% this wk" />
        <StatCard title="Processed" value={stats.processed_documents} icon={CheckCircle2} color="green" trend="100% complete" />
        <StatCard title="Verified" value={stats.verified_records} icon={ShieldCheck} color="purple" trend="Passed QA" />
        <StatCard title="Pending Verif" value={stats.pending_verification} icon={Clock} color="amber" trend="Action required" />
        <StatCard title="Errors" value={stats.validation_errors} icon={AlertTriangle} color="red" trend="Format warnings" />
        <StatCard title="Avg Confidence" value={`${Math.round(stats.average_confidence * 100)}%`} icon={Activity} color="blue" trend="HIGH quality" />
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Processing Time Series */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-navy-900">Documents Processed Over Time</h3>
            <span className="text-xs font-mono text-muted">Weekly Volume</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.time_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Area type="monotone" dataKey="processed" stroke="#2563EB" fill="#DBEAFE" name="Processed" />
                <Area type="monotone" dataKey="verified" stroke="#16A34A" fill="#DCFCE7" name="Verified" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Verification Status Pie */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-navy-900">Verification & Validation Breakdown</h3>
            <span className="text-xs font-mono text-muted">Status Ratio</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.verification_breakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {stats.verification_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend layout="horizontal" verticalAlign="bottom" align="center" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Document Type Distribution */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-navy-900">Document Type Distribution</h3>
            <span className="text-xs font-mono text-muted">By Category</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.document_type_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: District-wise Progress */}
        <div className="bg-white p-5 rounded-xl border border-border shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-navy-900">District-wise Digitization Progress</h3>
            <span className="text-xs font-mono text-muted">District Volume</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.district_distribution} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="district" type="category" tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#16A34A" radius={[0, 6, 6, 0]} name="Land Records" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Master Database Section */}
      <MasterDatabaseTable />

      {/* Recent Processing Activity Table */}
      <div className="bg-white rounded-xl border border-border overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-border flex items-center justify-between">
          <h3 className="text-sm font-bold text-navy-900">Recent Processing Activity</h3>
          <button
            onClick={() => navigate('/documents')}
            className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1"
          >
            <span>View All Documents</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-100/70 text-slate-700 text-xs font-semibold uppercase font-mono border-b border-border">
              <tr>
                <th className="p-3.5">Document Name</th>
                <th className="p-3.5">Type</th>
                <th className="p-3.5">District</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Confidence</th>
                <th className="p-3.5">Processed Date</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {stats.recent_activity.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-3.5 font-semibold text-navy-900">{item.document}</td>
                  <td className="p-3.5 text-xs text-muted">{item.type}</td>
                  <td className="p-3.5 text-xs font-mono">{item.district}</td>
                  <td className="p-3.5">
                    <ValidationBadge status={item.status} />
                  </td>
                  <td className="p-3.5">
                    <ConfidenceBadge score={item.confidence / 100} level={item.confidence_level} />
                  </td>
                  <td className="p-3.5 text-xs font-mono text-muted">{item.processed_date}</td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => navigate(`/documents/${item.id}`)}
                      className="px-2.5 py-1 text-xs bg-primary-50 text-primary-600 hover:bg-primary-100 rounded-md font-semibold transition-colors"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
