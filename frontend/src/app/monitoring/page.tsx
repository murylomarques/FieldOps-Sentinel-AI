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
    human_override_rate?: number;
    score_distribution: Array<{ status: string; count: number }>;
  } | null>(null);

  useEffect(() => {
    const token = getToken();
    apiFetch<{ avg_latency_ms: number; processed_volume: number; avg_score: number; simulated_drift: number; human_override_rate?: number; score_distribution: Array<{ status: string; count: number }> }>("/api/v1/monitoring/models", {}, token).then(setMonitoring).catch(console.error);
  }, []);

  if (!monitoring) {
    return (
      <AuthGuard>
        <DashboardShell>
          <Card className="p-8 text-center text-slate-500">Loading model telemetry...</Card>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="grid gap-5 xl:grid-cols-3">
          <Card className="xl:col-span-2 p-5">
            <div className="mb-4 flex items-center gap-2"><Activity size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Model Monitoring</h1></div>
            <p className="text-sm text-slate-500">Trust layer with latency, simulated drift, processing volume, and human override behavior.</p>

            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Average Latency</p><p className="text-xl font-semibold text-slate-900">{monitoring.avg_latency_ms} ms</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Processed Volume</p><p className="text-xl font-semibold text-slate-900">{monitoring.processed_volume}</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Average Score</p><p className="text-xl font-semibold text-slate-900">{monitoring.avg_score}</p></div>
              <div className="rounded-2xl border border-slate-200 p-3"><p className="text-slate-500">Human Override Rate</p><p className="text-xl font-semibold text-slate-900">{(monitoring.human_override_rate || 0).toFixed(1)}%</p></div>
            </div>
          </Card>

          <Card className="p-5">
            <h2 className="font-display text-lg font-bold text-slate-900">Status Distribution</h2>
            <StatusDistributionChart data={monitoring.score_distribution} />
            <p className="text-xs text-slate-500">Simulated drift: {monitoring.simulated_drift}</p>
          </Card>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}
