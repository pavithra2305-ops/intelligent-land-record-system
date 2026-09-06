import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, UploadCloud, FileText, CheckSquare,
  MapPin, ShieldAlert, Users, ChevronLeft, ChevronRight, LogOut, Shield
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const auth = useAuth();
  const { user, logout, switchDemoRole } = auth;

  const navItems = [
    { name: 'My Land Records', path: '/my-records', icon: FileText, roles: ['VIEWER'] },
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['VERIFIER', 'ADMIN'] },
    { name: 'Upload Document', path: '/upload', icon: UploadCloud, roles: ['VERIFIER', 'ADMIN'] },
    { name: 'Documents Library', path: '/documents', icon: FileText, roles: ['VERIFIER', 'ADMIN'] },
    { name: 'Human Verification', path: '/verification', icon: CheckSquare, roles: ['VERIFIER', 'ADMIN'] },
    { name: 'GIS Map View', path: '/gis', icon: MapPin, roles: ['VERIFIER', 'ADMIN'] },
    { name: 'Audit Logs', path: '/audit-logs', icon: ShieldAlert, roles: ['ADMIN'] },
    { name: 'User Management', path: '/users', icon: Users, roles: ['ADMIN'] }
  ];

  const visibleNavItems = navItems.filter((item) => item.roles.includes(user?.role));

  return (
    <aside className={`bg-navy-900 text-slate-300 border-r border-navy-800 transition-all duration-300 flex flex-col z-30 ${collapsed ? 'w-20' : 'w-64'}`}>
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-navy-800">
        {!collapsed && (
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold shadow-md">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-white text-sm leading-tight">LandDigitize</h1>
              <p className="text-[10px] text-slate-400 font-mono">GOVT CIVIC AI MVP</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-10 h-10 rounded-lg bg-primary-600 flex items-center justify-center text-white font-bold mx-auto">
            <Shield className="w-6 h-6" />
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-white"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {visibleNavItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-primary-600 text-white font-semibold shadow-sm'
                  : 'hover:bg-navy-800 text-slate-300 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Quick Role Switcher for Demo Mode */}
      {!collapsed && (
        <div className="px-3 py-2 border-t border-navy-800/60 bg-navy-950/40">
          <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">Quick Switch Demo Role</p>
          <div className="flex gap-1">
            {['ADMIN', 'VERIFIER', 'VIEWER'].map((role) => (
              <button
                key={role}
                onClick={() => switchDemoRole(role)}
                className={`flex-1 py-1 text-[10px] font-bold rounded border transition-colors ${
                  user?.role === role
                    ? 'bg-primary-600 text-white border-primary-500'
                    : 'bg-navy-800 text-slate-300 border-navy-700 hover:bg-navy-700'
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Logged in User Footer */}
      <div className="p-3 border-t border-navy-800 flex items-center justify-between">
        {!collapsed && (
          <div className="overflow-hidden pr-2">
            <p className="text-xs font-semibold text-white truncate">{user?.full_name}</p>
            <div className="flex items-center gap-1.5">
              <span className={`inline-block w-2 h-2 rounded-full ${user?.role === 'ADMIN' ? 'bg-error-500' : user?.role === 'VERIFIER' ? 'bg-warning-500' : 'bg-success-500'}`} />
              <span className="text-[11px] font-mono text-slate-400 uppercase">{user?.role}</span>
            </div>
          </div>
        )}
        <button
          onClick={logout}
          title="Sign out"
          className="p-2 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-error-400 transition-colors"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </aside>
  );
};
