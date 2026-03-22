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
    apiFetch("/api/v1/dashboard/executive-insights", {}, token).then(setInsights).catch(console.error);
  }, []);

  return (
    <AuthGuard>
      <DashboardShell>
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2"><ChartNoAxesCombined size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Insights Executivos</h1></div>
          <p className="text-sm text-slate-500">Inteligencia agregada para lideranca de operacoes e despacho.</p>

          {insights && (
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Principais Gargalos</h2><ul className="mt-2 space-y-1 text-sm text-slate-600">{insights.key_bottlenecks.map((b) => (<li key={b}>{b}</li>))}</ul></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Regioes com Maior Risco</h2><p className="mt-2 text-sm text-slate-600">{insights.high_risk_regions.join(", ") || "Sem hotspots no momento"}</p></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Alertas de Carga de Tecnicos</h2><ul className="mt-2 space-y-1 text-sm text-slate-600">{insights.technician_load_alerts.map((b) => (<li key={b}>{b}</li>))}</ul></div>
              <div className="rounded-2xl border border-slate-200 p-4"><h2 className="font-semibold text-slate-900">Backlog Critico</h2><p className="mt-2 text-3xl font-bold text-slate-900">{insights.critical_backlog}</p><p className="text-sm text-slate-500">Ordens em risco nas proximas horas: {insights.risk_orders_next_hours}</p></div>
            </div>
          )}
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}