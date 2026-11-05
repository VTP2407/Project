import React, { useEffect, useState } from 'react';
import { Heart, Save, AlertCircle, CheckCircle, Scale, Ruler, Activity } from 'lucide-react';
import api from '../api/client';
import { HealthProfile } from '../types';

export const HealthProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<HealthProfile>({
    gender: 'Female',
    height_cm: 165,
    weight_kg: 65,
    bmi: 23.88,
    hypertension: 0,
    heart_disease: 0,
    smoking_history: 'never',
    target_glucose_min: 70,
    target_glucose_max: 140,
    health_goals: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const fetchProfile = async () => {
    try {
      const res = await api.get('/patients/profile');
      if (res.data) {
        setProfile(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleChange = (field: keyof HealthProfile, val: any) => {
    setProfile((prev) => {
      const updated = { ...prev, [field]: val };
      if ((field === 'height_cm' || field === 'weight_kg') && updated.height_cm > 0) {
        const h_m = updated.height_cm / 100.0;
        updated.bmi = Math.round((updated.weight_kg / (h_m * h_m)) * 100) / 100;
      }
      return updated;
    });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await api.put('/patients/profile', profile);
      setProfile(res.data);
      setSuccess('Hồ sơ sức khỏe đã được cập nhật thành công.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lỗi khi cập nhật hồ sơ.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang tải hồ sơ...</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Hồ Sơ Sức Khỏe & Chỉ Số Cá Nhân</h1>
        <p className="text-sm text-slate-500 mt-1">
          Dữ liệu này được Patient Context Agent nạp vào để cá nhân hóa toàn bộ quy trình sàng lọc và tư vấn.
        </p>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs rounded-xl flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0" /> {success}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Giới tính</label>
              <select
                value={profile.gender}
                onChange={(e) => handleChange('gender', e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
              >
                <option value="Female">Nữ (Female)</option>
                <option value="Male">Nam (Male)</option>
                <option value="Other">Khác (Other)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Ngày sinh (hoặc năm sinh)
              </label>
              <input
                type="date"
                value={profile.date_of_birth || ''}
                onChange={(e) => handleChange('date_of_birth', e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Chiều cao (cm)
              </label>
              <div className="relative">
                <Ruler className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="number"
                  step="0.5"
                  required
                  value={profile.height_cm}
                  onChange={(e) => handleChange('height_cm', parseFloat(e.target.value) || 0)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Cân nặng (kg)
              </label>
              <div className="relative">
                <Scale className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="number"
                  step="0.5"
                  required
                  value={profile.weight_kg}
                  onChange={(e) => handleChange('weight_kg', parseFloat(e.target.value) || 0)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>

            {/* Calculated BMI */}
            <div className="sm:col-span-2 p-3.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-700">Chỉ số khối cơ thể (BMI):</span>
                <span className="ml-2 text-lg font-extrabold text-teal-700">{profile.bmi} kg/m²</span>
              </div>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                profile.bmi >= 25.0 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
              }`}>
                {profile.bmi < 18.5 ? 'Thiếu cân' : profile.bmi < 23.0 ? 'Bình thường (Chuẩn Á)' : profile.bmi < 25.0 ? 'Thừa cân nhẹ' : 'Thừa cân / Béo phì'}
              </span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Tăng huyết áp
              </label>
              <select
                value={profile.hypertension}
                onChange={(e) => handleChange('hypertension', parseInt(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
              >
                <option value={0}>Không có tiền sử</option>
                <option value={1}>Có tiền sử tăng huyết áp</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Bệnh tim mạch
              </label>
              <select
                value={profile.heart_disease}
                onChange={(e) => handleChange('heart_disease', parseInt(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
              >
                <option value={0}>Không có tiền sử</option>
                <option value={1}>Có tiền sử bệnh tim mạch</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Mục tiêu đường huyết thấp nhất (mg/dL)
              </label>
              <input
                type="number"
                value={profile.target_glucose_min}
                onChange={(e) => handleChange('target_glucose_min', parseFloat(e.target.value) || 0)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Mục tiêu đường huyết cao nhất (mg/dL)
              </label>
              <input
                type="number"
                value={profile.target_glucose_max}
                onChange={(e) => handleChange('target_glucose_max', parseFloat(e.target.value) || 0)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Mục tiêu sức khỏe & Chế độ mong muốn
              </label>
              <textarea
                rows={3}
                value={profile.health_goals || ''}
                onChange={(e) => handleChange('health_goals', e.target.value)}
                placeholder="Ví dụ: Giảm 4kg, duy trì mức đường huyết ổn định dưới 120 mg/dL, tập thể dục 30 phút mỗi ngày..."
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm rounded-xl shadow-sm transition disabled:opacity-50 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Đang lưu hồ sơ...' : 'Cập nhật hồ sơ'}
          </button>
        </form>
      </div>
    </div>
  );
};
