import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Activity, 
  Bot, 
  ClipboardCheck, 
  FileText, 
  Heart, 
  LayoutDashboard, 
  LogOut, 
  Sliders, 
  BrainCircuit, 
  BookOpen, 
  Cpu, 
  Sparkles,
  ShieldAlert,
  User as UserIcon
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  const isAdmin = user?.role === 'admin';

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItemClass = (path: string) => {
    const active = location.pathname === path;
    return `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
      active
        ? 'bg-teal-50 text-teal-700 font-semibold shadow-sm'
        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
    }`;
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-50">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-white border-r border-slate-200 flex flex-col shrink-0">
        <div className="p-5 border-b border-slate-100 flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 flex items-center justify-center text-white shadow-md">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-800 leading-tight">Diabetes AI</h1>
            <p className="text-[11px] font-medium text-teal-600">Multi-Agent System</p>
          </div>
        </div>

        <nav className="p-3.5 space-y-1.5 flex-1 overflow-y-auto">
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Bệnh nhân
          </div>
          <Link to="/dashboard" className={navItemClass('/dashboard')}>
            <LayoutDashboard className="w-4 h-4" />
            Tổng quan sức khỏe
          </Link>
          <Link to="/glucose" className={navItemClass('/glucose')}>
            <Activity className="w-4 h-4 text-emerald-600" />
            Theo dõi đường huyết
          </Link>
          <Link to="/assessment" className={navItemClass('/assessment')}>
            <ClipboardCheck className="w-4 h-4 text-cyan-600" />
            Đánh giá nguy cơ AI
          </Link>
          <Link to="/chat" className={navItemClass('/chat')}>
            <Bot className="w-4 h-4 text-teal-600" />
            Trợ lý Đa Agent
          </Link>
          <Link to="/profile" className={navItemClass('/profile')}>
            <Heart className="w-4 h-4 text-rose-500" />
            Hồ sơ & Mục tiêu
          </Link>
          <Link to="/reports" className={navItemClass('/reports')}>
            <FileText className="w-4 h-4 text-indigo-500" />
            Báo cáo sức khỏe
          </Link>

          {/* Admin Navigation */}
          {isAdmin && (
            <div className="pt-4 space-y-1.5 border-t border-slate-100 mt-4">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-3 h-3 text-amber-500" /> Quản Trị Hệ Thống
              </div>
              <Link to="/admin" className={navItemClass('/admin')}>
                <Sliders className="w-4 h-4 text-amber-600" />
                Thống kê Admin
              </Link>
              <Link to="/admin/agents" className={navItemClass('/admin/agents')}>
                <BrainCircuit className="w-4 h-4 text-purple-600" />
                Giám sát Multi-Agent
              </Link>
              <Link to="/admin/rules" className={navItemClass('/admin/rules')}>
                <ShieldAlert className="w-4 h-4 text-red-500" />
                Bộ quy tắc lâm sàng
              </Link>
              <Link to="/admin/knowledge" className={navItemClass('/admin/knowledge')}>
                <BookOpen className="w-4 h-4 text-blue-600" />
                Cơ sở tri thức (RAG)
              </Link>
              <Link to="/admin/models" className={navItemClass('/admin/models')}>
                <Cpu className="w-4 h-4 text-teal-600" />
                Mô hình ML / DL
              </Link>
              <Link to="/admin/rl" className={navItemClass('/admin/rl')}>
                <Sparkles className="w-4 h-4 text-orange-500" />
                Học tăng cường (RL)
              </Link>
            </div>
          )}
        </nav>

        {/* User Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
          <div className="flex items-center gap-2.5 truncate">
            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold text-xs shrink-0">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-slate-800 truncate">{user?.full_name || 'Người dùng'}</p>
              <p className="text-[10px] text-slate-400 capitalize">{user?.role || 'Patient'}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout} 
            title="Đăng xuất" 
            className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

