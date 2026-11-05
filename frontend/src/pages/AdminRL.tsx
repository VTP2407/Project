import React, { useEffect, useState } from 'react';
import { Sparkles, Play, RotateCcw, TrendingUp, Award, Layers } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import api from '../api/client';
import { RLExperiment } from '../types';

export const AdminRL: React.FC = () => {
  const [experiment, setExperiment] = useState<RLExperiment | null>(null);
  const [loading, setLoading] = useState(true);

  // Form controls
  const [episodes, setEpisodes] = useState(500);
  const [alpha, setAlpha] = useState(0.1);
  const [gamma, setGamma] = useState(0.95);
  const [epsilon, setEpsilon] = useState(0.1);
  const [training, setTraining] = useState(false);

  const fetchLatestExperiment = async () => {
    try {
      const res = await api.get('/rl/experiments');
      if (res.data.length > 0) {
        setExperiment(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestExperiment();
  }, []);

  const handleTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    setTraining(true);
    try {
      const res = await api.post('/rl/train', {
        episodes: Number(episodes),
        alpha: Number(alpha),
        gamma: Number(gamma),
        epsilon: Number(epsilon)
      });
      setExperiment(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setTraining(false);
    }
  };

  // Prepare chart data
  const chartData = experiment?.learning_metrics_json?.reward_history
    ? experiment.learning_metrics_json.reward_history.map((reward, idx) => ({
        episode: idx * 10,
        reward,
        moving_avg: experiment.learning_metrics_json.moving_average[idx] || reward
      }))
    : [];

  const policySummary = experiment?.q_table_summary?.policy_summary || [];

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Đang tải dữ liệu thí nghiệm Học tăng cường...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Mô Phỏng Học Tăng Cường (Reinforcement Learning - Q-Learning)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Thuật toán Q-Learning tự học chính sách tối ưu (Optimal Policy) trong môi trường mô phỏng giáo dục lối sống sức khỏe.
        </p>
      </div>

      {/* Control Panel & Config */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-slate-800 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-orange-500" />
            Cấu Hình Tham Số Huấn Luyện Q-Learning
          </h3>
          <span className="text-xs text-slate-400">
            Môi trường: 36 Trạng thái (Đường huyết x Vận động x Dinh dưỡng)
          </span>
        </div>

        <form onSubmit={handleTrain} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Số tập (Episodes)
            </label>
            <input
              type="number"
              min="50"
              max="3000"
              step="50"
              value={episodes}
              onChange={(e) => setEpisodes(parseInt(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Tốc độ học (α - Alpha)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max="1.0"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Hệ số chiết khấu (γ - Gamma)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.5"
              max="0.99"
              value={gamma}
              onChange={(e) => setGamma(parseFloat(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
              Khám phá (ε - Epsilon)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max="0.5"
              value={epsilon}
              onChange={(e) => setEpsilon(parseFloat(e.target.value))}
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={training}
              className="w-full py-2.5 bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs rounded-xl shadow-md transition disabled:opacity-50 flex items-center justify-center gap-1.5"
            >
              <Play className="w-4 h-4" />
              {training ? 'Đang mô phỏng...' : 'Chạy Huấn Luyện RL'}
            </button>
          </div>
        </form>
      </div>

      {/* Rewards Progress Chart */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-bold text-slate-800">Đường Cong Học Tập (Learning Progress & Total Reward per Episode)</h3>
            <p className="text-xs text-slate-400">
              Phần thưởng hội tụ tăng dần chứng minh Agent học được chiến lược can thiệp giáo dục tối ưu
            </p>
          </div>
          {experiment && (
            <span className="text-xs font-bold text-teal-700 bg-teal-50 px-3 py-1 rounded-full">
              Phần thưởng hội tụ: {experiment.learning_metrics_json?.final_average_reward} pts
            </span>
          )}
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="episode" tick={{ fontSize: 10, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
              <Tooltip contentStyle={{ fontSize: '11px', borderRadius: '8px' }} />
              <Line type="monotone" dataKey="reward" stroke="#fdba74" dot={false} strokeWidth={1} name="Reward tức thời" />
              <Line type="monotone" dataKey="moving_avg" stroke="#ea580c" strokeWidth={2.5} dot={false} name="Moving Average (Hội tụ)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Q-Table Policy Inspection */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-800 flex items-center gap-2">
            <Award className="w-5 h-5 text-teal-600" />
            Bảng Tra Q-Table & Hành Động Khuyến Nghị Tối Ưu (Policy Evaluation)
          </h3>
          <span className="text-xs text-slate-400">
            Q-Matrix argmax(Q[s, a])
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-5 py-3.5">Trạng Thái Bệnh Nhân (State)</th>
                <th className="px-5 py-3.5">Hành Động Tối Ưu Được Chọn (Optimal Action)</th>
                <th className="px-5 py-3.5">Q-Values: [Vận động, Dinh dưỡng, Tự theo dõi, Khám BS]</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {policySummary.map((p, idx) => (
                <tr key={idx} className="hover:bg-slate-50/60 transition">
                  <td className="px-5 py-3.5 font-bold text-slate-800">
                    {p.glucose_state} (Ít vận động, Ăn kém)
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200">
                      ★ {p.recommended_action}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-slate-600">
                    [{p.q_values.join(', ')}]
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

