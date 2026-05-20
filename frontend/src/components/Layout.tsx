import { Link, NavLink, Outlet } from "react-router-dom";
import {
  Bot,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import clsx from "clsx";

const navItems = [
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/monitoring", label: "Monitoring", icon: LayoutDashboard },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col shrink-0">
        <div className="p-5 border-b border-slate-800">
          <Link to="/chat" className="flex items-center gap-2 font-semibold text-lg">
            <Bot className="w-7 h-7 text-brand-400" />
            <span>AI Chatbot</span>
          </Link>
          <p className="text-xs text-slate-500 mt-1">Embedding RAG Cloud</p>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand-600/20 text-brand-300"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
                )
              }
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <p className="text-sm font-medium truncate">{user?.full_name}</p>
          <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-3 flex items-center gap-2 text-sm text-slate-400 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
