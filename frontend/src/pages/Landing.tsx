import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ShieldCheck, BrainCircuit, Bot, LineChart, Sparkles, ArrowRight } from 'lucide-react';

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 flex items-center justify-center text-white shadow-md">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-800">Diabetes AI</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 bg-teal-50 text-teal-700 rounded-full border border-teal-200">
                Multi-Agent System
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-teal-600 transition">
              Đăng nhập
            </Link>
            <Link to="/register" className="px-4 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition">
              Đăng ký ngay
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24 flex flex-col lg:flex-row items-center gap-12">
        <div className="lg:w-1/2 space-y-6 text-center lg:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-50 border border-teal-200 text-teal-800 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            Tích hợp Học máy, Deep Learning & RAG Y khoa Chuẩn
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Hệ Thống Đa Tác Nhân AI Hỗ Trợ <span className="text-teal-600">Bệnh Tiểu Đường</span> Toàn Diện
          </h1>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            Nền tảng hỗ trợ sức khỏe thông minh kết hợp 8 chuyên gia tác nhân AI, mô hình XGBoost & PyTorch MLP được huấn luyện trên 100,000 hồ sơ bệnh nhân, công cụ suy luận RAG và bộ quy tắc an toàn lâm sàng ADA/WHO.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
            <Link to="/login" className="w-full sm:w-auto px-6 py-3.5 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-xl shadow-md flex items-center justify-center gap-2 transition">
              Bắt đầu Trải Nghiệm Demo <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/assessment" className="w-full sm:w-auto px-6 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-medium rounded-xl border border-slate-200 shadow-sm transition">
              Sàng lọc Nguy cơ Ngay
            </Link>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-6 border-t border-slate-200">
            <div>
              <p className="text-2xl font-bold text-slate-800">97.2%</p>
              <p className="text-xs text-slate-500 font-medium">Độ chính xác XGBoost</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-teal-600">100k</p>
              <p className="text-xs text-slate-500 font-medium">Dữ liệu huấn luyện thực</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-cyan-600">8 Agents</p>
              <p className="text-xs text-slate-500 font-medium">Phối hợp thời gian thực</p>
            </div>
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div className="lg:w-1/2 grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600 mb-3">
              <Bot className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">Multi-Agent System</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Orchestrator Agent điều phối 7 Agent chuyên trách: Context, Assessment, Knowledge, Lifestyle, Monitoring, Safety, Report.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-10 h-10 rounded-xl bg-cyan-50 flex items-center justify-center text-cyan-600 mb-3">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">XGBoost & PyTorch MLP</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Mô hình học máy và mạng nơ-ron sâu giải thích bằng SHAP feature importance cho từng ca lâm sàng.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 mb-3">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">Bộ Quy Tắc Lâm Sàng</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Deterministic Rule Engine chặn đơn thuốc trái phép, tự động cảnh báo hạ đường huyết (&lt;70 mg/dL) và cấp cứu.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 mb-3">
              <LineChart className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">Q-Learning Simulation</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Mô phỏng Học tăng cường (Reinforcement Learning) tìm chính sách tối ưu tư vấn giáo dục lối sống.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500">
          © 2026 Diabetes Multi-Agent AI Support System. Dự án nghiên cứu ứng dụng Trí tuệ Nhân tạo trong Y tế.
        </div>
      </footer>
    </div>
  );
};

