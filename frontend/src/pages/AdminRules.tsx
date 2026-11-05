import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Check, X, AlertCircle, Lock } from 'lucide-react';
import api from '../api/client';
import { Rule } from '../types';

export const AdminRules: React.FC = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState('');

  const fetchRules = async () => {
    try {
      const res = await api.get('/rules');
      setRules(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleToggle = async (id: number) => {
    try {
      setMsg('');
      await api.put(`/rules/${id}/toggle`);
      fetchRules();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || 'Không thể thay đổi trạng thái quy tắc.');
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang tải danh mục quy tắc...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Bộ Quy Tắc Lâm Sàng Độc Lập (Rule Engine)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Hệ thống quy chuẩn xác định (deterministic), không dùng LLM phỏng đoán, đảm bảo tuân thủ nghiêm ngặt chuẩn an toàn ADA và WHO.
        </p>
      </div>

      {msg && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" /> {msg}
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-800 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-teal-600" />
            Danh Sách Quy Tắc Đang Kích Hoạt ({rules.length} quy tắc)
          </h3>
          <span className="text-xs text-slate-400">
            Quy tắc cốt lõi được gắn khóa an toàn không thể tắt
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-5 py-3.5">Mã Quy Tắc</th>
                <th className="px-5 py-3.5">Tên & Mô Tả</th>
                <th className="px-5 py-3.5">Phân Loại</th>
                <th className="px-5 py-3.5">Mức Ưu Tiên</th>
                <th className="px-5 py-3.5">Khóa Cốt Lõi</th>
                <th className="px-5 py-3.5 text-right">Trạng Thái</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {rules.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50/60 transition">
                  <td className="px-5 py-3.5 font-mono font-bold text-teal-700">
                    {r.rule_id}
                  </td>
                  <td className="px-5 py-3.5 max-w-md">
                    <p className="font-bold text-slate-900">{r.rule_name}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{r.description}</p>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase ${
                      r.category === 'safety' ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'
                    }`}>
                      {r.category}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-slate-600">
                    Priority #{r.priority}
                  </td>
                  <td className="px-5 py-3.5">
                    {r.is_immutable ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-md">
                        <Lock className="w-3 h-3" /> Cốt lõi
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[11px]">Cấu hình được</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => handleToggle(r.id)}
                      disabled={r.is_immutable}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                        r.is_enabled
                          ? 'bg-emerald-100 text-emerald-800 hover:bg-emerald-200'
                          : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                      } ${r.is_immutable ? 'opacity-60 cursor-not-allowed' : ''}`}
                    >
                      {r.is_enabled ? 'Đang Bật' : 'Đã Tắt'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

