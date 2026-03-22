"use client";

import { useEffect, useState } from "react";
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
          <p>Loading monitoring...</p>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="grid gap-5 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <h1 className="font-display text-xl font-bold">Model Monitoring</h1>
            <p className="mt-1 text-sm text-slate-500">Latency, drift simulation, processed volume and override analysis.</p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl border border-slate-200 p-3"><p className="text-slate-500">Avg Latency</p><p className="text-lg font-semibold">{monitoring.avg_latency_ms} ms</p></div>
              <div className="rounded-xl border border-slate-200 p-3"><p className="text-slate-500">Volume</p><p className="text-lg font-semibold">{monitoring.processed_volume}</p></div>
              <div className="rounded-xl border border-slate-200 p-3"><p className="text-slate-500">Avg Score</p><p className="text-lg font-semibold">{monitoring.avg_score}</p></div>
              <div className="rounded-xl border border-slate-200 p-3"><p className="text-slate-500">Human Override</p><p className="text-lg font-semibold">{monitoring.human_override_rate}%</p></div>
            </div>
          </Card>
          <Card>
            <h2 className="font-display text-lg font-semibold">Score Distribution</h2>
            <StatusDistributionChart data={monitoring.score_distribution} />
          </Card>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}
