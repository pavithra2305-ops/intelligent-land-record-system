import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

import { Login } from './pages/Login';
import { SignUp } from './pages/SignUp';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';
import { DocumentsList } from './pages/DocumentsList';
import { DocumentDetail } from './pages/DocumentDetail';
import { Verification } from './pages/Verification';
import { GISMap } from './pages/GISMap';
import { AuditLogs } from './pages/AuditLogs';
import { Users } from './pages/Users';
import { MyLandRecords } from './pages/MyLandRecords';

import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />

            {/* Common Authenticated Routes */}
            <Route element={<ProtectedRoute roles={['VIEWER', 'VERIFIER', 'ADMIN']} />}>
              <Route element={<Layout />}>
                <Route path="/" element={<Navigate to="/my-records" replace />} />
                <Route path="/my-records" element={<MyLandRecords />} />
              </Route>
            </Route>

            {/* Verifier + Admin Protected Routes */}
            <Route element={<ProtectedRoute roles={['VERIFIER', 'ADMIN']} />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/documents" element={<DocumentsList />} />
                <Route path="/documents/:id" element={<DocumentDetail />} />
                <Route path="/gis" element={<GISMap />} />
                <Route path="/upload" element={<Upload />} />
                <Route path="/verification" element={<Verification />} />
              </Route>
            </Route>

            {/* Admin-Only Protected Routes */}
            <Route element={<ProtectedRoute roles={['ADMIN']} />}>
              <Route element={<Layout />}>
                <Route path="/audit-logs" element={<AuditLogs />} />
                <Route path="/users" element={<Users />} />
              </Route>
            </Route>

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/my-records" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
