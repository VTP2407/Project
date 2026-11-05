import React, { useEffect, useState } from 'react';
import { BrainCircuit, Clock, CheckCircle2, ShieldCheck, ChevronRight, Activity } from 'lucide-react';
import api from '../api/client';

export const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [selectedExec, setSelectedExec] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agRes, exRes] = await Promise.all([
          api.get('/agents'),
          api.get('/agents/executions')
        ]);
        setAgents(agRes.data);
        setExecutions(exRes.data);
        if (exRes.data.length > 0) {
          setSelectedExec(exRes.data[0]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang tải cấu trúc Multi-Agent...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Giám Sát Hệ Thống Đa Agent (Agent Monitor)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Theo dõi quy trình phối hợp, phân luồng điều kiện và thời gian thực thi (latency) của từng Agent chuyên biệt.
        </p>
      </div>

      {/* Agents Roster Grid */}
      <div>
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-400 mb-3">
          Danh Sách 8 Agent Chuyên Trách Được Đăng Ký
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {agents.map((ag) => (
            <div key={ag.id} className="p-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-900">{ag.name}</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              </div>
              <p className="text-[11px] font-semibold text-teal-700">{ag.role}</p>
              <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">{ag.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Executions Timeline Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: History list */}
        <div className="lg:col-span-5 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
          <h3 className="font-bold text-sm text-slate-800">Lịch Sử Các Lần Phân Luồng Gần Nhất</h3>
          {executions.length === 0 ? (
            <p className="text-xs text-slate-400 italic">Chưa có lượt thực thi nào được ghi lại.</p>
          ) : (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {executions.map((e) => (
                <div
                  key={e.id}
                  onClick={() => setSelectedExec(e)}
                  className={`p-3.5 rounded-xl border text-xs cursor-pointer transition ${
                    selectedExec?.id === e.id
                      ? 'border-teal-500 bg-teal-50/50 shadow-sm'
                      : 'border-slate-100 bg-slate-50 hover:bg-slate-100/70'
                  }`}
                >
                  <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1 font-mono">
                    <span>ID #{e.id}</span>
                    <span className="flex items-center gap-1 text-teal-700 font-semibold">
                      <Clock className="w-3 h-3" /> {e.total_duration_ms}ms
                    </span>
                  </div>
                  <p className="font-semibold text-slate-800 line-clamp-1">"{e.query}"</p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    {e.timeline?.length || 0} agents tham gia xử lý
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Flow Diagram & Execution Timeline */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-purple-600" />
              Sơ Đồ Phối Hợp & Tiến Trình Thực Thi
            </h3>
            {selectedExec && (
              <span className="text-xs font-semibold px-2.5 py-1 bg-purple-50 text-purple-700 rounded-full">
                Tổng thời gian: {selectedExec.total_duration_ms}ms
              </span>
            )}
          </div>

          {!selectedExec ? (
            <p className="text-xs text-slate-400 italic">Chọn một phiên thực thi ở danh sách bên trái để kiểm tra chi tiết.</p>
          ) : (
            <div className="space-y-4">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                <span className="font-semibold text-slate-500 uppercase text-[10px] block mb-0.5">Yêu cầu từ người dùng:</span>
                <span className="font-medium text-slate-900 text-sm">"{selectedExec.query}"</span>
              </div>

              {/* Step by step timeline */}
              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Thứ tự điều phối Agent (Execution Flow):
                </p>
                {selectedExec.timeline?.map((step: any, index: number) => (
                  <div key={index} className="flex items-start gap-3 relative">
                    {/* Circle marker */}
                    <div className="w-7 h-7 rounded-full bg-teal-600 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm z-10">
                      {index + 1}
                    </div>
                    {/* Content Box */}
                    <div className="flex-1 p-3.5 bg-slate-50 rounded-xl border border-slate-200/70 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900">{step.agent_name}</span>
                        <span className="font-mono text-[10px] text-teal-700 font-semibold px-2 py-0.5 bg-teal-50 rounded-md">
                          {step.duration_ms}ms
                        </span>
                      </div>
                      <p className="text-slate-600 text-[11px] leading-relaxed">
                        {step.action_summary}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Final response preview */}
              <div className="pt-3 border-t border-slate-100">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Câu trả lời cuối cùng sau khi Safety Agent phê duyệt:
                </span>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs text-slate-700 max-h-40 overflow-y-auto whitespace-pre-line leading-relaxed">
                  {selectedExec.final_response}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

