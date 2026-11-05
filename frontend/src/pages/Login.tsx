import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import api from '../api/client';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('patient@diabetes.ai');
  const [password, setPassword] = useState('Patient@123456');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [apiUrl, setApiUrl] = useState(localStorage.getItem('custom_api_url') || '');

  const handleSaveApiUrl = () => {
    if (apiUrl.trim()) {
      localStorage.setItem('custom_api_url', apiUrl.trim());
    } else {
      localStorage.removeItem('custom_api_url');
    }
    window.location.reload();
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login', { email, password });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify({
        id: res.data.user_id,
        email: res.data.email,
        full_name: res.data.full_name,
        role: res.data.role
      }));
      if (res.data.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      let msg = 'Đăng nhập không thành công. Vui lòng kiểm tra lại.';
      if (err.response?.data?.detail) {
        msg = err.response.data.detail;
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        msg = `Không thể kết nối tới Backend API (${api.defaults.baseURL}). Vui lòng đảm bảo Backend server đang chạy hoặc kiểm tra đường dẫn API.`;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const setDemoAccount = (role: 'patient' | 'admin') => {
    if (role === 'patient') {
      setEmail('patient@diabetes.ai');
      setPassword('Patient@123456');
    } else {
      setEmail('admin@diabetes.ai');
      setPassword('Admin@123456');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 mx-auto flex items-center justify-center text-white shadow-md mb-3">
            <Activity className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800">Đăng Nhập Hệ Thống</h2>
          <p className="text-sm text-slate-500 mt-1">Diabetes Multi-Agent AI Support System</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="name@diabetes.ai"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Mật khẩu</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'} <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Access Buttons */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider text-center mb-2.5">
            Tài Khoản Thử Nghiệm Sẵn Có
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setDemoAccount('patient')}
              className="px-3 py-2 bg-slate-50 hover:bg-teal-50 border border-slate-200 text-slate-700 text-xs font-medium rounded-lg text-center transition"
            >
              👤 Bệnh Nhân Demo
            </button>
            <button
              type="button"
              onClick={() => setDemoAccount('admin')}
              className="px-3 py-2 bg-slate-50 hover:bg-amber-50 border border-slate-200 text-slate-700 text-xs font-medium rounded-lg text-center transition"
            >
              🛡️ Quản Trị Viên (Admin)
            </button>
          </div>

          <div className="mt-3 text-center">
            <button
              type="button"
              onClick={() => setShowConfig(!showConfig)}
              className="text-[11px] text-slate-400 hover:text-slate-600 underline"
            >
              {showConfig ? '▲ Ẩn cấu hình Backend API' : '⚙️ Cấu hình địa chỉ Backend API'}
            </button>
            {showConfig && (
              <div className="mt-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-left space-y-2">
                <label className="text-[11px] font-medium text-slate-600 block">
                  Đang dùng: <span className="font-mono text-teal-700">{api.defaults.baseURL}</span>
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="https://diabetes-backend.onrender.com"
                  className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 font-mono"
                />
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={handleSaveApiUrl}
                    className="px-3 py-1 bg-teal-600 text-white text-xs rounded-md hover:bg-teal-700"
                  >
                    Lưu & Tải lại
                  </button>
                  <button
                    type="button"
                    onClick={() => { localStorage.removeItem('custom_api_url'); window.location.reload(); }}
                    className="px-3 py-1 bg-slate-200 text-slate-700 text-xs rounded-md hover:bg-slate-300"
                  >
                    Khôi phục mặc định
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 mt-6">
          Chưa có tài khoản?{' '}
          <Link to="/register" className="text-teal-600 font-medium hover:underline">
            Đăng ký tài khoản mới
          </Link>
        </p>
      </div>
    </div>
  );
};

