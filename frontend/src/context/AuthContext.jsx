import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/login', { email, password });
      const { access_token, user: userData } = res.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      return { success: true, user: userData };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed. Please check credentials.';
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const switchDemoRole = async (role) => {
    const roleMap = {
      ADMIN: { email: 'admin@landgov.in', password: 'admin123' },
      VERIFIER: { email: 'verifier@landgov.in', password: 'verifier123' },
      VIEWER: { email: 'viewer@landgov.in', password: 'viewer123' }
    };
    if (roleMap[role]) {
      return await login(roleMap[role].email, roleMap[role].password);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      logout,
      switchDemoRole,
      isAuthenticated: !!token && !!user,
      isAdmin: user?.role === 'ADMIN',
      isVerifier: user?.role === 'VERIFIER' || user?.role === 'ADMIN',
      isViewer: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
