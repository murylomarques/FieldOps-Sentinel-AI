"use client";

import { useEffect, useState } from "react";
import { ChartNoAxesCombined } from "lucide-react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card } from "@/components/ui/card";
import { apiFetch, getToken } from "@/lib/api";

export default function InsightsPage() {
  const [insights, setInsights] = useState<{
    key_bottlenecks: string[];
    high_risk_regions: string[];
    technician_load_alerts: string[];
    critical_backlog: number;
    risk_orders_next_hours: number;
  } | null>(null);

  useEffect(() => {
    const token = getToken();
    apiFetch<{ key_bottlenecks: string[]; high_risk_regions: string[]; technician_load_alerts: string[]; critical_backlog: number; risk_orders_next_hours: number }>("/api/v1/dashboard/executive-insights", {}, token).then(setInsights).catch(console.error);
  }, []);

  return (
    <AuthGuard>
      <DashboardShell>
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2"><ChartNoAxesCombined size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Executive Insights</h1></div>
          <p className="text-sm text-slate-500">Aggregated intelligence for operations leadership and dispatch strategy.</p>

          {insights && (
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Top Bottlenecks</h2><ul className="mt-2 space-y-1 text-sm text-slate-600">{insights.key_bottlenecks.map((b) => (<li key={b}>{b}</li>))}</ul></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Highest Risk Regions</h2><p className="mt-2 text-sm text-slate-600">{insights.high_risk_regions.join(", ") || "No hotspots right now"}</p></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Technician Load Alerts</h2><ul className="mt-2 space-y-1 text-sm text-slate-600">{insights.technician_load_alerts.map((b) => (<li key={b}>{b}</li>))}</ul></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Critical Backlog</h2><p className="mt-2 text-3xl font-bold text-slate-900">{insights.critical_backlog}</p><p className="text-sm text-slate-500">Orders at risk in the next hours: {insights.risk_orders_next_hours}</p></div>
            </div>
          )}
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}
