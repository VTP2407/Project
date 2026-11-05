import React, { useEffect, useState } from 'react';
import { FileText, Printer, Download, CheckCircle, Activity, Heart, Shield } from 'lucide-react';
import api from '../api/client';

export const HealthReports: React.FC = () => {
  const [report, setReport] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReportData = async () => {
      try {
        const [dashRes, profRes] = await Promise.all([
          api.get('/patients/dashboard'),
          api.get('/patients/profile')
        ]);
        setReport(dashRes.data);
        setProfile(profRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadReportData();
  }, []);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang khởi tạo báo cáo...</div>;
  }

  const summary = report?.metrics_summary || {};
  const measurements = report?.measurements_chart || [];
  const assessments = report?.recent_assessments || [];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Báo Cáo Sức Khỏe & Tóm Tắt Lâm Sàng</h1>
          <p className="text-sm text-slate-500 mt-1">
            Tổng hợp dữ liệu theo dõi sức khỏe và lịch sử sàng lọc nguy cơ bởi Report Agent.
          </p>
        </div>
        <button
          onClick={handlePrint}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center gap-1.5 self-start"
        >
          <Printer className="w-4 h-4" /> In / Lưu PDF
        </button>
      </div>

      {/* Printable Report Document Sheet */}
      <div className="bg-white p-8 sm:p-10 rounded-2xl border border-slate-200/80 shadow-sm space-y-6 print:border-none print:shadow-none print:p-0">
        {/* Document Header */}
        <div className="border-b-2 border-slate-900 pb-5 flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold text-slate-900 uppercase tracking-tight">
              Báo Cáo Tóm Tắt Theo Dõi Đái Tháo Đường
            </h2>
            <p className="text-xs text-teal-700 font-semibold mt-0.5">
              Hệ thống AI Đa Tác Nhân (Diabetes Multi-Agent System)
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Ngày xuất báo cáo: {new Date().toLocaleDateString('vi-VN')}
            </p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold text-base">
            <Activity className="w-6 h-6" />
          </div>
        </div>

        {/* Patient Info */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100 text-xs">
          <div>
            <span className="text-slate-400 font-medium block">Bệnh nhân:</span>
            <span className="font-bold text-slate-800 text-sm">Demo Patient</span>
          </div>
          <div>
            <span className="text-slate-400 font-medium block">Giới tính:</span>
            <span className="font-semibold text-slate-800">{profile?.gender === 'Female' ? 'Nữ' : 'Nam'}</span>
          </div>
          <div>
            <span className="text-slate-400 font-medium block">Chỉ số BMI:</span>
            <span className="font-bold text-slate-800">{profile?.bmi || '--'} kg/m²</span>
          </div>
          <div>
            <span className="text-slate-400 font-medium block">Huyết áp / Tim mạch:</span>
            <span className="font-semibold text-slate-800">
              {profile?.hypertension ? 'Tăng huyết áp' : 'Bình thường'}
            </span>
          </div>
        </div>

        {/* Statistical Summary */}
        <div>
          <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider mb-3">
            1. Thống Kê Chuỗi Thời Gian Đường Huyết (20 lần đo gần nhất)
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs text-slate-500 block">Số lượt đo</span>
              <span className="text-xl font-bold text-slate-800">{summary.total_measurements || 0}</span>
            </div>
            <div className="p-3 bg-teal-50 rounded-xl border border-teal-100">
              <span className="text-xs text-teal-700 block">Đường huyết trung bình</span>
              <span className="text-xl font-bold text-teal-800">{summary.average_glucose || '--'} mg/dL</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs text-slate-500 block">Số lần bất thường</span>
              <span className="text-xl font-bold text-amber-600">{summary.unread_alerts || 0}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-xs text-slate-500 block">Mục tiêu kiểm soát</span>
              <span className="text-xs font-bold text-slate-800 mt-1 block">
                {profile?.target_glucose_min}-{profile?.target_glucose_max} mg/dL
              </span>
            </div>
          </div>
        </div>

        {/* Recent AI Assessments */}
        <div>
          <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider mb-3">
            2. Kết Quả Sàng Lọc Nguy Cơ Học Máy (XGBoost)
          </h3>
          {assessments.length === 0 ? (
            <p className="text-xs text-slate-400 italic">Chưa có kết quả sàng lọc mô hình AI.</p>
          ) : (
            <div className="space-y-2">
              {assessments.map((a: any) => (
                <div key={a.id} className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 text-xs flex justify-between items-center">
                  <div>
                    <span className="font-bold text-slate-800">{a.predicted_class}</span>
                    <span className="text-slate-500 ml-2">
                      (Xác suất: {(a.probability * 100).toFixed(1)}% - Phân nhóm: {a.risk_category})
                    </span>
                    <p className="text-slate-600 text-[11px] mt-1">{a.clinical_explanation}</p>
                  </div>
                  <span className="text-[10px] text-slate-400 shrink-0 font-mono">
                    {new Date(a.created_at).toLocaleDateString('vi-VN')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Doctor Signature Block */}
        <div className="pt-8 border-t border-slate-200 grid grid-cols-2 text-center text-xs text-slate-600">
          <div>
            <p className="font-bold text-slate-800">XÁC NHẬN CỦA BỆNH NHÂN</p>
            <p className="text-[10px] text-slate-400 mt-0.5">(Ký và ghi rõ họ tên)</p>
            <div className="h-16"></div>
          </div>
          <div>
            <p className="font-bold text-slate-800">BÁC SĨ ĐIỀU TRỊ / TƯ VẤN</p>
            <p className="text-[10px] text-slate-400 mt-0.5">(Ký, đóng dấu và cho ý kiến lâm sàng)</p>
            <div className="h-16"></div>
          </div>
        </div>

        <p className="text-[10px] text-slate-400 text-center italic pt-4">
          Báo cáo này được tự động tạo từ ứng dụng Diabetes Multi-Agent System nhằm mục đích hỗ trợ theo dõi cá nhân.
        </p>
      </div>
    </div>
  );
};
