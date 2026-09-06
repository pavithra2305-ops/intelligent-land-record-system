import React from 'react';
import { Bell, ShieldCheck, Database } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Header = () => {
  const { user } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-border px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-mono bg-slate-100 px-3 py-1.5 rounded-md border border-slate-200 text-slate-700">
          <Database className="w-3.5 h-3.5 text-primary-600" />
          <span>DB: SQLite Local (PostgreSQL Ready)</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-success-50 px-3 py-1.5 rounded-md border border-success-200 text-success-700">
          <ShieldCheck className="w-3.5 h-3.5 text-success-600" />
          <span>AI Engine: Active</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-semibold text-navy-900">{user?.full_name}</p>
          <p className="text-xs text-muted font-mono">{user?.email}</p>
        </div>
        <div className="w-9 h-9 rounded-full bg-primary-100 text-primary-700 font-bold text-sm flex items-center justify-center border border-primary-200">
          {user?.full_name ? user.full_name.charAt(0) : 'U'}
        </div>
      </div>
    </header>
  );
};
