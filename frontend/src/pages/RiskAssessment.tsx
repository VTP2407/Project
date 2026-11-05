import React, { useState } from 'react';
import { 
  ClipboardCheck, 
  BrainCircuit, 
  ShieldAlert, 
  HelpCircle, 
  ArrowRight, 
  BarChart2, 
  CheckCircle,
  AlertTriangle 
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from 'recharts';
import api from '../api/client';
import { PredictionRequest, HealthAssessment } from '../types';

export const RiskAssessment: React.FC = () => {
  const [formData, setFormData] = useState<PredictionRequest>({
    gender: 'Female',
    age: 45,
    hypertension: 0,
    heart_disease: 0,
    smoking_history: 'never',
    bmi: 24.5,
    HbA1c_level: 5.6,
    blood_glucose_level: 110.0,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HealthAssessment | null>(null);
  const [error, setError] = useState('');

  const handleChange = (field: keyof PredictionRequest, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePreset = (type: 'normal' | 'high_risk') => {
    if (type === 'normal') {
      setFormData({
        gender: 'Female',
        age: 32,
        hypertension: 0,
        heart_disease: 0,
        smoking_history: 'never',
        bmi: 21.8,
        HbA1c_level: 5.2,
        blood_glucose_level: 90.0,
      });
    } else {
      setFormData({
        gender: 'Male',
        age: 62,
        hypertension: 1,
        heart_disease: 1,
        smoking_history: 'former',
        bmi: 31.5,
        HbA1c_level: 7.4,
        blood_glucose_level: 185.0,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.post('/ai/predictions', formData);
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Không thể tính toán dự báo.');
    } finally {
      setLoading(false);
    }
  };

  // Convert SHAP feature importance dictionary to sorted array for Recharts
  const shapChartData = result?.feature_importance
    ? Object.entries(result.feature_importance)
        .map(([feature, value]) => ({
          feature,
          importance: Math.round(Number(value) * 100) / 100,
        }))
        .sort((a, b) => b.importance - a.importance)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Sàng Lọc Nguy Cơ Đái Tháo Đường (AI Assessment)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Ứng dụng mô hình học máy (XGBoost) huấn luyện trên 100,000 hồ sơ bệnh nhân thực tế, tích hợp giải thích SHAP theo từng chỉ số sinh học.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form Column */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <ClipboardCheck className="w-5 h-5 text-teal-600" />
              Chỉ Số Đầu Vào
            </h3>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handlePreset('normal')}
                className="px-2.5 py-1 text-xs font-medium bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition"
              >
                Mẫu Khỏe Mạnh
              </button>
              <button
                type="button"
                onClick={() => handlePreset('high_risk')}
                className="px-2.5 py-1 text-xs font-medium bg-rose-50 text-rose-700 rounded-lg hover:bg-rose-100 transition"
              >
                Mẫu Nguy Cơ Cao
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Giới tính</label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  <option value="Female">Nữ (Female)</option>
                  <option value="Male">Nam (Male)</option>
                  <option value="Other">Khác (Other)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Tuổi</label>
                <input
                  type="number"
                  min="1"
                  max="120"
                  required
                  value={formData.age}
                  onChange={(e) => handleChange('age', parseFloat(e.target.value) || 0)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Chỉ số BMI (kg/m²)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="10"
                  max="90"
                  required
                  value={formData.bmi}
                  onChange={(e) => handleChange('bmi', parseFloat(e.target.value) || 0)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Tiền sử hút thuốc
                </label>
                <select
                  value={formData.smoking_history}
                  onChange={(e) => handleChange('smoking_history', e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  <option value="never">Không bao giờ (never)</option>
                  <option value="No Info">Không có thông tin (No Info)</option>
                  <option value="current">Đang hút thuốc (current)</option>
                  <option value="former">Đã từng hút (former)</option>
                  <option value="ever">Thỉnh thoảng (ever)</option>
                  <option value="not current">Hiện không hút (not current)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Chỉ số HbA1c (%) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="3.5"
                  max="15.0"
                  required
                  value={formData.HbA1c_level}
                  onChange={(e) => handleChange('HbA1c_level', parseFloat(e.target.value) || 0)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <span className="text-[10px] text-slate-400">Ngưỡng ADA: &lt;5.7% bình thường, &gt;=6.5% ĐTĐ</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Đường huyết máu (mg/dL) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="40"
                  max="400"
                  required
                  value={formData.blood_glucose_level}
                  onChange={(e) => handleChange('blood_glucose_level', parseFloat(e.target.value) || 0)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <span className="text-[10px] text-slate-400">Ngưỡng ADA đói: &lt;100 bình thường, &gt;=126 ĐTĐ</span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Tăng huyết áp (Hypertension)
                </label>
                <select
                  value={formData.hypertension}
                  onChange={(e) => handleChange('hypertension', parseInt(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  <option value={0}>Không (0)</option>
                  <option value={1}>Có tiền sử tăng huyết áp (1)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Bệnh tim mạch (Heart Disease)
                </label>
                <select
                  value={formData.heart_disease}
                  onChange={(e) => handleChange('heart_disease', parseInt(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  <option value={0}>Không (0)</option>
                  <option value={1}>Có tiền sử bệnh tim (1)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <BrainCircuit className="w-5 h-5" />
              {loading ? 'Đang phân tích mô hình...' : 'Thực Hiện Đánh Giá Nguy Cơ Ngay'}
            </button>
          </form>
        </div>

        {/* Prediction Results Column */}
        <div className="lg:col-span-5 space-y-4">
          {!result && !loading && (
            <div className="bg-white p-8 rounded-2xl border border-dashed border-slate-200 text-center h-full flex flex-col items-center justify-center">
              <div className="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center mb-3">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h4 className="font-bold text-slate-700">Chưa có kết quả phân tích</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-xs">
                Vui lòng điền đủ 8 thông số sinh học hoặc chọn nút mẫu phía trên để chạy dự báo mô hình AI.
              </p>
            </div>
          )}

          {loading && (
            <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center flex flex-col items-center justify-center space-y-3">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-teal-600"></div>
              <p className="text-sm font-semibold text-slate-700">Đang chạy suy luận mô hình XGBoost & SHAP...</p>
            </div>
          )}

          {result && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
              {/* Header result */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Mô hình: {result.model_name} (v{result.model_version})
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  result.prediction === 1 ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'
                }`}>
                  {result.predicted_class}
                </span>
              </div>

              {/* Probability Meter */}
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span>Xác suất nguy cơ:</span>
                  <span className="text-teal-700 font-bold">{(result.probability * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      result.probability >= 0.5 ? 'bg-red-500' : result.probability >= 0.2 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.max(5, Math.min(100, result.probability * 100))}%` }}
                  />
                </div>
                <p className="text-xs text-slate-500 mt-1.5 font-medium">
                  Phân nhóm: <strong className="text-slate-800">{result.risk_category}</strong>
                </p>
              </div>

              {/* Clinical Explanation */}
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-xs text-slate-700 leading-relaxed">
                <p className="font-semibold text-slate-900 mb-1 flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4 text-teal-600" /> Luận Giải Y Khoa:
                </p>
                {result.clinical_explanation}
              </div>

              {/* SHAP Feature Importance */}
              <div>
                <p className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <BarChart2 className="w-4 h-4 text-cyan-600" /> Trọng Số Ảnh Hưởng (SHAP Values)
                </p>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={shapChartData.slice(0, 5)} layout="vertical" margin={{ top: 0, right: 10, left: 45, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="2 2" stroke="#f1f5f9" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis dataKey="feature" type="category" tick={{ fontSize: 10, fill: '#64748b' }} width={80} />
                      <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '8px' }} />
                      <Bar dataKey="importance" fill="#0d9488" radius={[0, 4, 4, 0]}>
                        {shapChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={index === 0 ? '#ef4444' : index === 1 ? '#f59e0b' : '#0d9488'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Medical Disclaimer */}
              <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-[11px] text-amber-900 leading-tight">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 inline mr-1" />
                <strong>Tuyên bố miễn trừ:</strong> {result.limitations}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
