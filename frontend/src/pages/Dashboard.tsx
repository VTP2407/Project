import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  TrendingUp, 
  AlertTriangle, 
  ShieldCheck, 
  PlusCircle, 
  Bot, 
  ArrowRight,
  Clock,
  CheckCircle2
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine,
  CartesianGrid 
} from 'recharts';
import api from '../api/client';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      const res = await api.get('/patients/dashboard');
      setData(res.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  const summary = data?.metrics_summary || {};
  const chartData = data?.measurements_chart || [];
  const alerts = data?.active_alerts || [];
  const profile = data?.profile || {};

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-teal-700 via-teal-600 to-cyan-600 rounded-2xl p-6 text-white shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Chào mừng trở lại!</h1>
          <p className="text-teal-100 text-sm mt-1">
            Hồ sơ: {profile.gender === 'Female' ? 'Nữ' : 'Nam'} | BMI: {profile.bmi || 24.0} | Mục tiêu: {profile.target_glucose_min}-{profile.target_glucose_max} mg/dL
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/glucose"
            className="px-4 py-2 bg-white text-teal-800 font-medium text-xs rounded-xl shadow-sm hover:bg-teal-50 transition flex items-center gap-1.5"
          >
            <PlusCircle className="w-4 h-4 text-teal-600" /> Ghi số đo mới
          </Link>
          <Link
            to="/chat"
            className="px-4 py-2 bg-teal-800/60 hover:bg-teal-800 text-white font-medium text-xs rounded-xl transition flex items-center gap-1.5"
          >
            <Bot className="w-4 h-4" /> Hỏi Trợ lý AI
          </Link>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Đường huyết gần nhất</span>
            <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">
            {summary.latest_glucose ? `${summary.latest_glucose} mg/dL` : '--'}
          </p>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" /> Cập nhật tự động
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Trung bình 20 lần đo</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-50 text-cyan-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">
            {summary.average_glucose ? `${summary.average_glucose} mg/dL` : '--'}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Mục tiêu chuẩn: &lt; 140 mg/dL
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cảnh báo lâm sàng</span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-800 mt-2">
            {alerts.length}
          </p>
          <p className="text-xs text-amber-600 mt-1 font-medium">
            {alerts.length > 0 ? 'Cần chú ý theo dõi' : 'Chỉ số trong tầm kiểm soát'}
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mức nguy cơ AI</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <p className="text-lg font-bold text-slate-800 mt-2 truncate">
            {summary.latest_risk || 'Chưa đánh giá'}
          </p>
          <Link to="/assessment" className="text-xs text-teal-600 hover:underline mt-1 inline-flex items-center gap-1">
            Làm xét nghiệm AI <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Glucose Trend Chart */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="font-bold text-slate-800">Biểu Đồ Xu Hướng Đường Huyết (Chuỗi thời gian)</h3>
            <p className="text-xs text-slate-400">Các mốc đường cơ sở: 70 mg/dL (ngưỡng hạ) và 126 mg/dL (ngưỡng đái tháo đường đói theo ADA)</p>
          </div>
          <span className="text-xs font-medium px-2.5 py-1 bg-slate-100 rounded-full text-slate-600">
            {chartData.length} điểm dữ liệu
          </span>
        </div>

        {chartData.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-sm">
            <Activity className="w-8 h-8 mb-2 opacity-50" />
            Chưa có số liệu đo đường huyết. Hãy ghi số đo đầu tiên!
          </div>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis domain={[50, 220]} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <ReferenceLine y={126} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'ADA Ngưỡng ĐTĐ (126)', fill: '#ef4444', fontSize: 10, position: 'insideTopRight' }} />
                <ReferenceLine y={70} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Hạ đường (<70)', fill: '#f59e0b', fontSize: 10, position: 'insideBottomRight' }} />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#0d9488" 
                  strokeWidth={2.5} 
                  dot={{ r: 4, fill: '#0d9488', strokeWidth: 1 }} 
                  activeDot={{ r: 6 }} 
                  name="Đường huyết (mg/dL)" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Alerts and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Alerts */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            Cảnh Báo Từ Hệ Thống Giám Sát (Monitoring Agent)
          </h3>
          {alerts.length === 0 ? (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 flex items-center gap-3 text-emerald-800 text-xs">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>Không có cảnh báo bất thường nào đang kích hoạt. Chỉ số duy trì tốt!</span>
            </div>
          ) : (
            <div className="space-y-2.5">
              {alerts.map((a: any) => (
                <div key={a.id} className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900">
                  <p className="font-semibold">{a.title}</p>
                  <p className="mt-1 leading-relaxed text-amber-800">{a.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* AI Recommendations */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
            <Bot className="w-4 h-4 text-teal-600" />
            Khuyến Nghị Từ Lifestyle Advisor Agent
          </h3>
          <ul className="space-y-2.5 text-xs text-slate-600">
            <li className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              🥗 <strong>Đĩa ăn Dinh dưỡng ADA:</strong> Đảm bảo 1/2 bữa ăn là rau xanh giàu chất xơ hòa tan để làm chậm hấp thu glucose sau ăn.
            </li>
            <li className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              🚶 <strong>Vận động thể chất:</strong> Đi bộ nhẹ nhàng 15-20 phút sau các bữa chính để tăng cường hấp thu glucose độc lập với insulin.
            </li>
            <li className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              💧 <strong>Cung cấp đủ nước:</strong> Uống đủ 2 - 2.5 lít nước lọc mỗi ngày nhằm hỗ trợ thận lọc và đào thải lượng đường dư thừa.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
