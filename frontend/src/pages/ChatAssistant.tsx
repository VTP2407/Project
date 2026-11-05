import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  Clock, 
  BrainCircuit, 
  ShieldCheck, 
  BookOpen, 
  AlertTriangle,
  Plus,
  Trash2,
  ChevronRight,
  Info
} from 'lucide-react';
import api from '../api/client';
import { AgentTimelineStep } from '../types';

interface MessageItem {
  id: string | number;
  role: 'user' | 'assistant';
  content: string;
  timeline?: AgentTimelineStep[];
  citations?: Array<{ title: string; source: string; category: string; score: number }>;
  duration_ms?: number;
}

export const ChatAssistant: React.FC = () => {
  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Xin chào! Tôi là Trợ lý AI Đa Agent chuyên sâu về Đái Tháo Đường. Hệ thống phối hợp giữa các Agent: Ngữ cảnh bệnh nhân, Đánh giá học máy, Tri thức RAG chuẩn y khoa, Giáo dục lối sống và Thẩm định an toàn lâm sàng. Bạn đang quan tâm đến vấn đề sức khỏe nào hôm nay?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>(undefined);
  const [activeTimeline, setActiveTimeline] = useState<AgentTimelineStep[] | null>(null);
  const [conversations, setConversations] = useState<any[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const res = await api.get('/chat/conversations');
      setConversations(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg: MessageItem = {
      id: Date.now(),
      role: 'user',
      content: query
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chat', {
        message: query,
        conversation_id: conversationId
      });

      const data = res.data;
      setConversationId(data.conversation_id);
      setActiveTimeline(data.timeline);

      const assistantMsg: MessageItem = {
        id: data.message_id || Date.now() + 1,
        role: 'assistant',
        content: data.reply,
        timeline: data.timeline,
        citations: data.citations,
        duration_ms: data.total_duration_ms
      };

      setMessages((prev) => [...prev, assistantMsg]);
      fetchConversations();
    } catch (err: any) {
      const errMsg: MessageItem = {
        id: Date.now() + 2,
        role: 'assistant',
        content: '⚠️ Đã xảy ra lỗi khi kết nối với Hệ thống Multi-Agent: ' + (err.response?.data?.detail || err.message)
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setConversationId(undefined);
    setActiveTimeline(null);
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Cuộc trò chuyện mới đã bắt đầu. Mời bạn đặt câu hỏi hoặc chia sẻ chỉ số đường huyết để các Agent cùng phân tích.'
      }
    ]);
  };

  const loadConversation = async (convId: number) => {
    try {
      const res = await api.get(`/chat/conversations/${convId}/messages`);
      setConversationId(convId);
      const loaded: MessageItem[] = res.data.map((m: any) => ({
        id: m.id,
        role: m.sender_role,
        content: m.content,
        timeline: m.agent_metadata_json?.timeline,
        duration_ms: m.agent_metadata_json?.total_duration_ms
      }));
      setMessages(loaded);
      if (loaded.length > 0 && loaded[loaded.length - 1].timeline) {
        setActiveTimeline(loaded[loaded.length - 1].timeline || null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const suggestions = [
    "Đường huyết sáng nay của tôi là 135 mg/dL lúc đói, mức này có nguy hiểm không?",
    "Tiêu chuẩn chẩn đoán chỉ số HbA1c theo ADA là bao nhiêu?",
    "Chế độ ăn phù hợp cho người có nguy cơ tiền đái tháo đường?",
    "Tôi bị vã mồ hôi, run tay và đường huyết đo được 62 mg/dL thì phải xử trí thế nào?"
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Trợ Lý AI Đa Agent (Multi-Agent Chat)</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Phối hợp tự động: Orchestrator ➔ Context ➔ Knowledge (RAG) ➔ Lifestyle ➔ Safety Agent
          </p>
        </div>
        <button
          onClick={handleNewChat}
          className="px-3.5 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-xl text-xs font-semibold shadow-sm transition flex items-center gap-1.5 self-start"
        >
          <Plus className="w-3.5 h-3.5 text-teal-600" /> Cuộc trò chuyện mới
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-210px)] min-h-[580px]">
        {/* Chat Stream Column */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200/80 shadow-sm flex flex-col overflow-hidden">
          {/* Messages list */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'bg-slate-50 border border-slate-100 text-slate-800'
                  }`}
                >
                  <div className="whitespace-pre-line">{m.content}</div>

                  {/* Metadata preview for assistant */}
                  {m.role === 'assistant' && m.timeline && (
                    <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
                      <span className="flex items-center gap-1 text-teal-700 font-medium">
                        <BrainCircuit className="w-3.5 h-3.5" /> {m.timeline.length} Agents đã phối hợp
                      </span>
                      {m.duration_ms && (
                        <span className="flex items-center gap-1 text-slate-400">
                          <Clock className="w-3 h-3" /> {m.duration_ms}ms
                        </span>
                      )}
                      <button
                        onClick={() => setActiveTimeline(m.timeline || null)}
                        className="text-teal-600 font-semibold hover:underline flex items-center gap-0.5"
                      >
                        Xem tiến trình <ChevronRight className="w-3 h-3" />
                      </button>
                    </div>
                  )}

                  {/* Citations preview */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-200/60">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                        Tài liệu tham chiếu chuẩn:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {m.citations.map((c, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] bg-white border border-slate-200 text-slate-700 px-2 py-0.5 rounded-md font-medium"
                          >
                            📖 {c.title} ({c.source})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 items-center text-xs text-slate-400 p-2">
                <div className="w-7 h-7 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center animate-pulse">
                  <Bot className="w-4 h-4" />
                </div>
                <span>Hệ thống Đa Agent đang phân tích câu hỏi & thẩm định an toàn...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Starter Suggestions */}
          {messages.length <= 2 && (
            <div className="px-4 py-2 border-t border-slate-100 bg-slate-50/50">
              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-teal-600" /> Gợi ý câu hỏi lâm sàng:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(s)}
                    className="text-[11px] px-2.5 py-1 bg-white hover:bg-teal-50 hover:text-teal-700 border border-slate-200 rounded-lg text-slate-600 transition text-left"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Box */}
          <div className="p-3 border-t border-slate-200 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Nhập câu hỏi hoặc số đo đường huyết của bạn..."
                className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl shadow-sm transition disabled:opacity-40 flex items-center gap-1.5 text-xs font-semibold"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Multi-Agent Execution Monitor Drawer */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 flex flex-col overflow-hidden">
          <div className="pb-3 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-purple-600" />
              Agent Execution Monitor
            </h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full">
              Live Inspector
            </span>
          </div>

          <div className="flex-1 overflow-y-auto py-3 space-y-3">
            {!activeTimeline ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-4 text-slate-400">
                <BrainCircuit className="w-8 h-8 mb-2 opacity-40 text-purple-500" />
                <p className="text-xs font-medium">Chưa có tiến trình nào được kích hoạt.</p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Gửi câu hỏi để quan sát Orchestrator phân luồng và điều phối các Agent AI.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5">
                <p className="text-[11px] font-semibold text-slate-500">
                  Chuỗi phối hợp ({activeTimeline.length} Agent):
                </p>
                {activeTimeline.map((step, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl border border-slate-100 bg-slate-50 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800 flex items-center gap-1.5">
                        <span className="w-4 h-4 rounded-full bg-teal-100 text-teal-800 text-[10px] flex items-center justify-center font-bold">
                          {idx + 1}
                        </span>
                        {step.agent_name}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {step.duration_ms}ms
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 leading-tight">
                      {step.action_summary}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Past conversations list */}
          <div className="pt-3 border-t border-slate-100">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Lịch sử hội thoại:
            </p>
            <div className="space-y-1 max-h-28 overflow-y-auto">
              {conversations.slice(0, 4).map((c) => (
                <button
                  key={c.id}
                  onClick={() => loadConversation(c.id)}
                  className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs truncate transition ${
                    conversationId === c.id
                      ? 'bg-teal-50 text-teal-800 font-semibold'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  💬 {c.title}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

