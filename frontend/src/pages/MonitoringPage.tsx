import { useEffect, useState } from "react";
import { Activity, Database, FileText, MessageSquare, Users } from "lucide-react";
import api from "../services/api";
import type { MonitoringStats } from "../types";

const statCards = [
  { key: "users" as const, label: "Users", icon: Users, color: "text-blue-400" },
  { key: "conversations" as const, label: "Conversations", icon: MessageSquare, color: "text-brand-400" },
  { key: "messages" as const, label: "Messages", icon: Activity, color: "text-emerald-400" },
  { key: "documents" as const, label: "Documents", icon: FileText, color: "text-amber-400" },
];

export default function MonitoringPage() {
  const [stats, setStats] = useState<MonitoringStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<MonitoringStats>("/monitoring/stats")
      .then(({ data }) => setStats(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!stats) {
    return <div className="p-6 text-red-400">Failed to load monitoring data</div>;
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Monitoring Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">
          {stats.app.name} &mdash; {stats.app.environment}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map(({ key, label, icon: Icon, color }) => (
          <div key={key} className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-sm">{label}</span>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <p className="text-3xl font-bold">{stats[key]}</p>
          </div>
        ))}
      </div>

      <div className="card p-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-brand-400" />
          Service Health
        </h2>
        <div className="space-y-3">
          {Object.entries(stats.services).map(([name, status]) => (
            <div
              key={name}
              className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0"
            >
              <span className="text-slate-300 capitalize">{name.replace(/_/g, " ")}</span>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  status === "healthy"
                    ? "text-emerald-400 bg-emerald-400/10"
                    : "text-red-400 bg-red-400/10"
                }`}
              >
                {status}
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-4">
          Prometheus metrics available at /api/monitoring/metrics
        </p>
      </div>
    </div>
  );
}
