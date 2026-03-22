"use client";

import { useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { StatusDistributionChart } from "@/components/charts/status-distribution-chart";
import { Card } from "@/components/ui/card";
import { apiFetch, getToken } from "@/lib/api";

export default function MonitoringPage() {
  const [monitoring, setMonitoring] = useState<{
    avg_latency_ms: number;
    processed_volume: number;
    avg_score: number;
    simulated_drift: number;
    human_override_rate: number;
    score_distribution: Array<{ status: string; count: number }>;
  } | null>(null);

  useEffect(() => {
    const token = getToken();
    apiFetch("/api/v1/monitoring/models", {}, token).then(setMonitoring).catch(console.error);
  }, []);

  if (!monitoring) {
    return (
      <AuthGuard>
        <DashboardShell>
          <Card className="p-8 text-center text-slate-500">Carregando telemetria do modelo...</Card>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="grid gap-5 xl:grid-cols-3">
          <Card className="xl:col-span-2 p-5">
            <div className="mb-4 flex items-center gap-2"><Activity size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Monitoramento de Modelo</h1></div>
            <p className="text-sm text-slate-500">Camada de confianca com latencia, drift simulado, volume e override humano.</p>

            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Latencia Media</p><p className="text-xl font-semibold text-slate-900">{monitoring.avg_latency_ms} ms</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Volume Processado</p><p className="text-xl font-semibold text-slate-900">{monitoring.processed_volume}</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Score Medio</p><p className="text-xl font-semibold text-slate-900">{monitoring.avg_score}</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Taxa de Override Humano</p><p className="text-xl font-semibold text-slate-900">{monitoring.human_override_rate}%</p></div>
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="font-display text-lg font-bold text-slate-900">Distribuicao de Status</h2>
            <StatusDistributionChart data={monitoring.score_distribution} />
            <p className="text-xs text-slate-500">Drift simulado: {monitoring.simulated_drift}</p>
          </Card>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}