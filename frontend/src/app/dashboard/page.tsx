"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { RiskByRegionChart } from "@/components/charts/risk-by-region-chart";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiFetch, getToken } from "@/lib/api";
import { KpiData, RecommendationQueue } from "@/lib/types";

const defaultKpi: KpiData = {
  percent_orders_at_risk: 0,
  avg_sla_risk_score: 0,
  approval_rate: 0,
  override_rate: 0,
  avg_response_latency_ms: 0,
  projected_avoided_delays: 0,
  projected_backlog_reduction: 0,
  estimated_operational_impact: 0,
};

export default function DashboardPage() {
  const [kpi, setKpi] = useState<KpiData>(defaultKpi);
  const [regionData, setRegionData] = useState<Array<{ region: string; risk_score: number }>>([]);
  const [queue, setQueue] = useState<RecommendationQueue[]>([]);

  useEffect(() => {
    const token = getToken();
    apiFetch<KpiData>("/api/v1/dashboard/kpis", {}, token).then(setKpi).catch(console.error);
    apiFetch<Array<{ region: string; risk_score: number }>>("/api/v1/dashboard/risk-by-region", {}, token)
      .then(setRegionData)
      .catch(console.error);
    apiFetch<RecommendationQueue[]>("/api/v1/recommendations/queue", {}, token).then(setQueue).catch(console.error);
  }, []);

  const cards = [
    ["Orders At Risk", `${kpi.percent_orders_at_risk.toFixed(1)}%`],
    ["Avg SLA Risk", `${kpi.avg_sla_risk_score.toFixed(1)} / 100`],
    ["Approval Rate", `${kpi.approval_rate.toFixed(1)}%`],
    ["Projected Impact", `${kpi.estimated_operational_impact.toFixed(1)}%`],
  ];

  return (
    <AuthGuard>
      <DashboardShell>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          <div>
            <h1 className="font-display text-2xl font-bold">Command Center</h1>
            <p className="text-sm text-slate-500">Real-time decision intelligence for field service operations.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {cards.map(([title, value]) => (
              <Card key={title}>
                <p className="text-xs uppercase tracking-wide text-slate-500">{title}</p>
                <p className="mt-2 text-2xl font-bold text-ink">{value}</p>
              </Card>
            ))}
          </div>

          <div className="grid gap-5 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold">Regional Risk Heat</h2>
                <Badge label="Live" tone="blue" />
              </div>
              <RiskByRegionChart data={regionData} />
            </Card>

            <Card>
              <h2 className="font-display text-lg font-semibold">Pending Human Approval</h2>
              <div className="mt-4 space-y-3">
                {queue.slice(0, 6).map((item) => (
                  <div key={item.decision_id} className="rounded-xl border border-slate-200 p-3">
                    <p className="text-sm font-semibold">{item.order_id}</p>
                    <p className="text-xs text-slate-500">{item.action_type} • confidence {(item.confidence * 100).toFixed(0)}%</p>
                  </div>
                ))}
                {!queue.length && <p className="text-sm text-slate-500">No pending recommendations.</p>}
              </div>
            </Card>
          </div>
        </motion.div>
      </DashboardShell>
    </AuthGuard>
  );
}
