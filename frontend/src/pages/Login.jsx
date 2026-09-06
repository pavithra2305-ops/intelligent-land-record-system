import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, ArrowRight, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, loading } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in both email and password.');
      return;
    }
    const res = await login(email, password);
    if (res.success) {
      toast.success(`Welcome back, ${res.user.full_name}!`);
      if (res.user.role === 'VIEWER') {
        navigate('/my-records');
      } else {
        navigate('/dashboard');
      }
    } else {
      toast.error(res.error);
    }
  };

  const handleDemoLogin = async (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    const res = await login(demoEmail, demoPassword);
    if (res.success) {
      toast.success(`Logged in as ${res.user.full_name} (${res.user.role})!`);
      if (res.user.role === 'VIEWER') {
        navigate('/my-records');
      } else {
        navigate('/dashboard');
      }
    }
  };

  return (
    <div className="min-h-screen w-screen bg-navy-900 flex items-center justify-center p-4 relative overflow-hidden">
      
      {/* Background Decorative Ambient Gradients */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-success-600/10 rounded-full blur-3xl" />

      <div className="max-w-md w-full bg-white rounded-2xl border border-border shadow-2xl overflow-hidden relative z-10">
        
        {/* Header Branding */}
        <div className="p-8 bg-slate-50 border-b border-border text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-primary-600 flex items-center justify-center text-white mx-auto shadow-lg shadow-primary-600/30">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-navy-900">LandRecord AI System</h1>
            <p className="text-xs text-muted font-medium mt-1">Intelligent Digitization & Validation Portal</p>
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-5 h-5 text-muted absolute left-3 top-2.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@landgov.in"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-5 h-5 text-muted absolute left-3 top-2.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl shadow-md shadow-primary-600/20 flex items-center justify-center gap-2 transition-all hover:gap-3"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Portal'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <div className="text-center pt-2">
            <p className="text-xs text-slate-600 font-medium">
              Don't have an account?{' '}
              <a href="/signup" className="text-primary-600 hover:text-primary-700 font-bold hover:underline">
                Sign Up
              </a>
            </p>
          </div>
        </form>

        {/* Quick Demo Credentials Panel (Dev Mode) */}
        <div className="p-6 bg-slate-50 border-t border-border space-y-3">
          <p className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider text-center flex items-center justify-center gap-1">
            <UserCheck className="w-3.5 h-3.5 text-primary-600" />
            <span>Development Mode: Quick Demo Login</span>
          </p>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleDemoLogin('admin@landgov.in', 'admin123')}
              className="p-2 rounded-lg bg-white border hover:border-primary-500 text-left text-xs transition-all shadow-xs"
            >
              <div className="font-bold text-navy-900">Admin</div>
              <div className="text-[10px] text-muted font-mono truncate">admin@landgov.in</div>
            </button>

            <button
              onClick={() => handleDemoLogin('verifier@landgov.in', 'verifier123')}
              className="p-2 rounded-lg bg-white border hover:border-warning-500 text-left text-xs transition-all shadow-xs"
            >
              <div className="font-bold text-navy-900">Verifier</div>
              <div className="text-[10px] text-muted font-mono truncate">verifier@landgov.in</div>
            </button>

            <button
              onClick={() => handleDemoLogin('viewer1@landgov.in', 'viewer123')}
              className="p-2 rounded-lg bg-white border hover:border-success-500 text-left text-xs transition-all shadow-xs"
            >
              <div className="font-bold text-navy-900">Viewer 1 (Ramesh)</div>
              <div className="text-[10px] text-muted font-mono truncate">viewer1@landgov.in</div>
            </button>

            <button
              onClick={() => handleDemoLogin('viewer2@landgov.in', 'viewer123')}
              className="p-2 rounded-lg bg-white border hover:border-purple-500 text-left text-xs transition-all shadow-xs"
            >
              <div className="font-bold text-navy-900">Viewer 2 (Priya)</div>
              <div className="text-[10px] text-muted font-mono truncate">viewer2@landgov.in</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
