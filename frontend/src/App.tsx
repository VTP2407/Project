import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { GlucoseTracking } from './pages/GlucoseTracking';
import { RiskAssessment } from './pages/RiskAssessment';
import { ChatAssistant } from './pages/ChatAssistant';
import { HealthProfilePage } from './pages/HealthProfile';
import { HealthReports } from './pages/HealthReports';
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminAgents } from './pages/AdminAgents';
import { AdminRules } from './pages/AdminRules';
import { AdminKnowledge } from './pages/AdminKnowledge';
import { AdminModels } from './pages/AdminModels';
import { AdminRL } from './pages/AdminRL';

// Protected Route Wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({ children, adminOnly }) => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return <Layout>{children}</Layout>;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Patient Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/glucose" element={<ProtectedRoute><GlucoseTracking /></ProtectedRoute>} />
        <Route path="/assessment" element={<ProtectedRoute><RiskAssessment /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><ChatAssistant /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><HealthProfilePage /></ProtectedRoute>} />
        <Route path="/reports" element={<ProtectedRoute><HealthReports /></ProtectedRoute>} />

        {/* Admin Routes */}
        <Route path="/admin" element={<ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/agents" element={<ProtectedRoute adminOnly><AdminAgents /></ProtectedRoute>} />
        <Route path="/admin/rules" element={<ProtectedRoute adminOnly><AdminRules /></ProtectedRoute>} />
        <Route path="/admin/knowledge" element={<ProtectedRoute adminOnly><AdminKnowledge /></ProtectedRoute>} />
        <Route path="/admin/models" element={<ProtectedRoute adminOnly><AdminModels /></ProtectedRoute>} />
        <Route path="/admin/rl" element={<ProtectedRoute adminOnly><AdminRL /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;

