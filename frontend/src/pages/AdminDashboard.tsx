import React, { useEffect, useState } from 'react';
import { 
  Users, 
  Activity, 
  ShieldCheck, 
  BookOpen, 
  Cpu, 
  BrainCircuit, 
  Server,
  Database
} from 'lucide-react';
import api from '../api/client';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/admin/stats');
        setStats(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang tải dữ liệu quản trị...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Quản Trị Hệ Thống (Admin Control Panel)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Giám sát hoạt động của Multi-Agent System, Machine Learning Models, RAG Knowledge Base và Clinical Rules.
        </p>
      </div>

      {/* Grid of stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Người dùng hệ thống</span>
            <Users className="w-5 h-5 text-teal-600" />
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">{stats?.total_users || 0}</p>
          <p className="text-xs text-slate-400 mt-1">Bao gồm bệnh nhân & quản trị viên</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Lượt thực thi Agent</span>
            <BrainCircuit className="w-5 h-5 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">{stats?.total_agent_executions || 0}</p>
          <p className="text-xs text-purple-600 mt-1 font-medium">Multi-Agent Orchestrations</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Quy tắc lâm sàng</span>
            <ShieldCheck className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">{stats?.total_rules || 0}</p>
          <p className="text-xs text-slate-400 mt-1">Deterministic Rule Engine</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tài liệu RAG Y khoa</span>
            <BookOpen className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">{stats?.total_kb_documents || 0}</p>
          <p className="text-xs text-slate-400 mt-1">WHO, ADA, CDC, NIDDK</p>
        </div>
      </div>

      {/* Dataset & Model Specification Box */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-800 flex items-center gap-2">
          <Database className="w-5 h-5 text-teal-600" />
          Tập Dữ Liệu Huấn Luyện Gốc Đang Hoạt Động (Dataset Preservation)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
            <span className="text-slate-400 font-semibold block uppercase text-[10px]">Tập tin dữ liệu</span>
            <span className="font-mono font-bold text-slate-800 text-sm">diabetes_prediction_dataset.csv</span>
            <p className="text-slate-500 text-[11px]">100,000 bản ghi bệnh nhân | 9 trường đặc trưng</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
            <span className="text-slate-400 font-semibold block uppercase text-[10px]">Mã băm SHA-256 bảo toàn</span>
            <span className="font-mono text-teal-700 text-[11px] break-all">
              F233FC470E904201F35310D061CB46CA0A6BC7CA5C3E428B769FB4F87F69929B
            </span>
          </div>
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
            <span className="text-slate-400 font-semibold block uppercase text-[10px]">Mô hình chính thức (Active)</span>
            <span className="font-bold text-slate-800 text-sm">{stats?.active_model || 'XGBoost Classifier'}</span>
            <p className="text-emerald-700 font-medium text-[11px]">Độ chính xác Test: 97.25% | ROC-AUC: 97.97%</p>
          </div>
        </div>
      </div>
    </div>
  );
};
