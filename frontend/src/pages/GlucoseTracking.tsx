import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Plus, 
  Trash2, 
  AlertCircle, 
  Calendar, 
  Clock, 
  CheckCircle, 
  AlertTriangle 
} from 'lucide-react';
import api from '../api/client';
import { GlucoseMeasurement } from '../types';

export const GlucoseTracking: React.FC = () => {
  const [measurements, setMeasurements] = useState<GlucoseMeasurement[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Form state
  const [value, setValue] = useState('');
  const [type, setType] = useState('fasting');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchMeasurements = async () => {
    try {
      const res = await api.get('/measurements/glucose');
      setMeasurements(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeasurements();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);
    try {
      const valNum = parseFloat(value);
      if (isNaN(valNum) || valNum < 20 || valNum > 600) {
        setError('Vui lòng nhập giá trị đường huyết hợp lệ (20 - 600 mg/dL).');
        setSubmitting(false);
        return;
      }
      await api.post('/measurements/glucose', {
        value: valNum,
        measurement_type: type,
        notes: notes || undefined
      });
      setValue('');
      setNotes('');
      setSuccess('Đã lưu kết quả đo thành công.');
      fetchMeasurements();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Không thể lưu kết quả.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa bản ghi này?')) return;
    try {
      await api.delete(`/measurements/glucose/${id}`);
      fetchMeasurements();
    } catch (err) {
      console.error(err);
    }
  };

  const getBadge = (m: GlucoseMeasurement) => {
    if (m.alert_level === 'HYPO') {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-100 text-red-800">Hạ đường huyết (&lt;70)</span>;
    }
    if (m.alert_level === 'HYPER_EMERGENCY') {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-600 text-white">Khẩn cấp (&gt;=250)</span>;
    }
    if (m.alert_level === 'DIABETES') {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800">Ngưỡng ĐTĐ (ADA)</span>;
    }
    if (m.alert_level === 'PREDIABETES') {
      return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-100 text-blue-800">Tiền đái tháo đường</span>;
    }
    return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800">Bình thường</span>;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Nhật Ký & Theo Dõi Đường Huyết</h1>
        <p className="text-sm text-slate-500 mt-1">
          Theo dõi diễn biến đường huyết cá nhân theo tiêu chuẩn lâm sàng ADA. Tích hợp Rule Engine tự động phát hiện bất thường.
        </p>
      </div>

      {/* Input Form & Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="w-4 h-4 text-teal-600" /> Ghi Nhận Số Đo Mới
          </h3>

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

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Chỉ số đường huyết (mg/dL) *
                </label>
                <div className="relative">
                  <Activity className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder="Ví dụ: 115"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Thời điểm đo *
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
                >
                  <option value="fasting">Đói (Fasting - nhịn ăn &gt;= 8h)</option>
                  <option value="postprandial">Sau ăn 2h (Postprandial)</option>
                  <option value="bedtime">Trước khi ngủ (Bedtime)</option>
                  <option value="random">Ngẫu nhiên (Random)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Ghi chú (bữa ăn, triệu chứng, vận động)
              </label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Ví dụ: Sau khi chạy bộ 30 phút..."
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm rounded-xl shadow-sm transition disabled:opacity-50"
            >
              {submitting ? 'Đang lưu...' : 'Lưu chỉ số'}
            </button>
          </form>
        </div>

        {/* Clinical Guidelines Card */}
        <div className="bg-gradient-to-br from-teal-50 to-cyan-50 p-6 rounded-2xl border border-teal-100 flex flex-col justify-between">
          <div>
            <h4 className="font-bold text-teal-900 mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-teal-600" />
              Ngưỡng Chuẩn ADA (mg/dL)
            </h4>
            <div className="space-y-2 text-xs text-teal-950 mt-3">
              <div className="p-2.5 bg-white/70 rounded-lg">
                <span className="font-semibold text-emerald-700">Đói bình thường:</span> 70 - 99 mg/dL
              </div>
              <div className="p-2.5 bg-white/70 rounded-lg">
                <span className="font-semibold text-blue-700">Tiền đái tháo đường:</span> 100 - 125 mg/dL
              </div>
              <div className="p-2.5 bg-white/70 rounded-lg">
                <span className="font-semibold text-red-700">Đái tháo đường:</span> &gt;= 126 mg/dL
              </div>
              <div className="p-2.5 bg-white/70 rounded-lg">
                <span className="font-semibold text-amber-700">Sau ăn 2h an toàn:</span> &lt; 140 mg/dL
              </div>
            </div>
          </div>
          <p className="text-[11px] text-teal-700 mt-4 italic">
            * Cảnh báo: Đường huyết &lt; 70 mg/dL là mức hạ đường huyết nguy hiểm cần nạp đường ngay.
          </p>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-800">Lịch Sử Các Lần Đo Gần Đây</h3>
          <span className="text-xs text-slate-500 font-medium">
            Tổng cộng: {measurements.length} lần ghi
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400">Đang tải dữ liệu...</div>
        ) : measurements.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">
            Chưa có số đo nào được ghi.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="px-5 py-3.5">Thời gian</th>
                  <th className="px-5 py-3.5">Chỉ số (mg/dL)</th>
                  <th className="px-5 py-3.5">Thời điểm</th>
                  <th className="px-5 py-3.5">Phân loại lâm sàng</th>
                  <th className="px-5 py-3.5">Ghi chú</th>
                  <th className="px-5 py-3.5 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {measurements.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/60 transition">
                    <td className="px-5 py-3.5 font-medium flex items-center gap-1.5 text-slate-600">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {new Date(m.measured_at).toLocaleString('vi-VN')}
                    </td>
                    <td className="px-5 py-3.5 font-bold text-sm text-slate-900">
                      {m.value}
                    </td>
                    <td className="px-5 py-3.5 capitalize text-slate-600">
                      {m.measurement_type === 'fasting' ? 'Lúc đói' : m.measurement_type === 'postprandial' ? 'Sau ăn 2h' : m.measurement_type}
                    </td>
                    <td className="px-5 py-3.5">
                      {getBadge(m)}
                    </td>
                    <td className="px-5 py-3.5 text-slate-500 italic max-w-xs truncate">
                      {m.notes || '--'}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={() => handleDelete(m.id)}
                        className="text-slate-400 hover:text-red-600 p-1 rounded transition"
                        title="Xóa"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

