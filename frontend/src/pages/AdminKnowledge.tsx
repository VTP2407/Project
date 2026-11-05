import React, { useEffect, useState } from 'react';
import { BookOpen, Search, Plus, Trash2, CheckCircle, FileText, Sparkles } from 'lucide-react';
import api from '../api/client';
import { KnowledgeDocument } from '../types';

export const AdminKnowledge: React.FC = () => {
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(true);

  // Search Tester state
  const [testQuery, setTestQuery] = useState('Tiêu chuẩn chẩn đoán đái tháo đường lúc đói');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  // Ingestion form state
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Nutrition');
  const [source, setSource] = useState('WHO');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchDocs = async () => {
    try {
      const res = await api.get('/knowledge/documents');
      setDocs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleTestSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.post('/knowledge/search', {
        query: testQuery,
        top_k: 3
      });
      setSearchResults(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleCreateDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMsg('');
    try {
      await api.post('/knowledge/documents', {
        title,
        category,
        source,
        content
      });
      setTitle('');
      setContent('');
      setMsg('Đã nạp tài liệu và phân đoạn vector (chunking) thành công!');
      fetchDocs();
    } catch (err: any) {
      setMsg(err.response?.data?.detail || 'Không thể nạp tài liệu.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Xóa tài liệu này khỏi cơ sở tri thức RAG?')) return;
    try {
      await api.delete(`/knowledge/documents/${id}`);
      fetchDocs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Cơ Sở Tri Thức & Công Cụ RAG (Knowledge Base)</h1>
        <p className="text-sm text-slate-500 mt-1">
          Quản lý tài liệu y khoa chuẩn xác thực từ WHO, ADA, CDC và kiểm thử trực quan công cụ truy xuất ngữ nghĩa (Semantic Vector Search).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Documents Table */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-blue-600" />
              Tài Liệu Đã Nạp ({docs.length} tài liệu y khoa)
            </h3>
          </div>

          {loading ? (
            <p className="text-xs text-slate-400">Đang tải tài liệu...</p>
          ) : docs.length === 0 ? (
            <p className="text-xs text-slate-400 italic">Chưa có tài liệu nào trong cơ sở tri thức.</p>
          ) : (
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {docs.map((d) => (
                <div key={d.id} className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-sm">{d.title}</span>
                    <button
                      onClick={() => handleDelete(d.id)}
                      className="text-slate-400 hover:text-red-600 p-1 rounded transition"
                      title="Xóa"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 text-[11px]">
                    <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-semibold">
                      {d.source}
                    </span>
                    <span className="text-slate-400">•</span>
                    <span className="text-slate-500 font-medium">{d.category}</span>
                    <span className="text-slate-400">•</span>
                    <span className="text-slate-400">{d.chunk_count} phân đoạn (chunks)</span>
                  </div>
                  <p className="text-slate-600 text-[11px] line-clamp-3 leading-relaxed">
                    {d.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: RAG Semantic Search Tester */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-teal-600" />
              Kiểm Thử Truy Xuất Ngữ Nghĩa RAG (Live Tester)
            </h3>
            <form onSubmit={handleTestSearch} className="space-y-3">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  value={testQuery}
                  onChange={(e) => setTestQuery(e.target.value)}
                  placeholder="Nhập câu hỏi để thử tìm đoạn văn liên quan..."
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <button
                type="submit"
                disabled={searching}
                className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-semibold shadow-sm transition disabled:opacity-50"
              >
                {searching ? 'Đang truy xuất vector...' : 'Chạy Thử Nghiệm Tìm Kiếm'}
              </button>
            </form>

            {searchResults.length > 0 && (
              <div className="space-y-2.5 pt-2 border-t border-slate-100">
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Kết quả trả về ({searchResults.length} đoạn tri thức):
                </p>
                {searchResults.map((r, i) => (
                  <div key={i} className="p-3 bg-teal-50/60 rounded-xl border border-teal-100 text-xs space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-teal-900">{r.title}</span>
                      <span className="font-mono text-[10px] font-bold text-teal-700">
                        Score: {r.similarity_score}
                      </span>
                    </div>
                    <p className="text-[11px] text-teal-950 leading-relaxed italic">
                      "{r.content}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Upload New Document Box */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-2">
              <Plus className="w-4 h-4 text-teal-600" /> Nạp Tài Liệu Y Khoa Mới
            </h3>

            {msg && (
              <div className="p-2.5 bg-emerald-50 text-emerald-800 text-xs rounded-lg border border-emerald-200">
                {msg}
              </div>
            )}

            <form onSubmit={handleCreateDoc} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Tiêu đề tài liệu</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ví dụ: Khuyến cáo kiểm soát đường huyết sau ăn..."
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Nguồn uy tín</label>
                  <input
                    type="text"
                    required
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                    placeholder="ADA, WHO, CDC..."
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Chủ đề</label>
                  <input
                    type="text"
                    required
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="Nutrition, Prevention..."
                    className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Nội dung văn bản</label>
                <textarea
                  rows={3}
                  required
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Dán toàn văn nội dung y khoa vào đây để phân đoạn embedding..."
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg font-semibold shadow-sm transition disabled:opacity-50"
              >
                {submitting ? 'Đang phân đoạn vector...' : 'Nạp và Tạo Embeddings'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

