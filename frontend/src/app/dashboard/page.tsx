"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, BrainCircuit, CheckCircle2, Clock3, ShieldAlert, Sparkles } from "lucide-react";
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

const agents = [
  { name: "Intake Agent", status: "active", hint: "Normalizing incoming service orders" },
  { name: "Risk Scoring Agent", status: "active", hint: "Delay, no-show, reschedule, SLA breach" },
  { name: "Dispatch Recommendation Agent", status: "active", hint: "Building recovery interventions" },
  { name: "Policy Guard Agent", status: "enforcing", hint: "Validating hard business constraints" },
  { name: "Explainability Agent", status: "active", hint: "Generating deterministic rationale" },
  { name: "Executive Insights Agent", status: "active", hint: "Aggregating operational bottlenecks" },
];

export default function DashboardPage() {
  const [kpi, setKpi] = useState<KpiData>(defaultKpi);
  const [regionData, setRegionData] = useState<Array<{ region: string; risk_score: number }>>([]);
  const [queue, setQueue] = useState<RecommendationQueue[]>([]);

  useEffect(() => {
    const token = getToken();
    apiFetch<KpiData>("/api/v1/dashboard/summary", {}, token).then(setKpi).catch(console.error);
    apiFetch<Array<{ region: string; risk_score: number }>>("/api/v1/dashboard/risk-by-region", {}, token)
      .then(setRegionData)
      .catch(console.error);
    apiFetch<RecommendationQueue[]>("/api/v1/recommendations/queue", {}, token).then(setQueue).catch(console.error);
  }, []);

  const headline = useMemo(() => {
    if (kpi.percent_orders_at_risk >= 50) return "High operational risk detected";
    if (kpi.percent_orders_at_risk >= 30) return "Moderate risk, intervention required";
    return "Operation stable under predictive control";
  }, [kpi.percent_orders_at_risk]);

  return (
    <AuthGuard>
      <DashboardShell>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-6 text-white shadow-2xl">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="mb-2 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]">
                  <Sparkles size={14} /> Agentic Operations Intelligence
                </p>
                <h1 className="font-display text-3xl font-bold">Command Center</h1>
                <p className="mt-2 text-sm text-slate-200">{headline}. Human approval remains mandatory for critical interventions.</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-2xl border border-white/10 bg-white/10 p-3">
                  <p className="text-xs text-slate-300">Orders at Risk</p>
                  <p className="text-xl font-bold">{kpi.percent_orders_at_risk.toFixed(1)}%</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/10 p-3">
                  <p className="text-xs text-slate-300">Operational Impact</p>
                  <p className="text-xl font-bold">{kpi.estimated_operational_impact.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Average SLA Risk</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.avg_sla_risk_score.toFixed(1)}</p><p className="mt-2 text-xs text-slate-500">Aggregated breach pressure index.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Approval Rate</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.approval_rate.toFixed(1)}%</p><p className="mt-2 text-xs text-slate-500">Human accepted interventions.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Override Rate</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.override_rate.toFixed(1)}%</p><p className="mt-2 text-xs text-slate-500">Human overrides over AI recommendations.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Inference Latency</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.avg_response_latency_ms.toFixed(1)} ms</p><p className="mt-2 text-xs text-slate-500">Multi-agent response time.</p></Card>
          </div>

          <div className="grid gap-5 xl:grid-cols-3">
            <Card className="xl:col-span-2 p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="font-display text-lg font-bold text-slate-900">Risk by Region</h2>
                  <p className="text-xs text-slate-500">Regional concentration of operational risk.</p>
                </div>
                <Badge label="Live" tone="blue" />
              </div>
              <RiskByRegionChart data={regionData} />
            </Card>

            <Card className="p-5">
              <h2 className="font-display text-lg font-bold text-slate-900">Approval Queue</h2>
              <p className="text-xs text-slate-500">Critical recommendations waiting for decision.</p>
              <div className="mt-4 space-y-3">
                {queue.slice(0, 6).map((item) => (
                  <div key={item.decision_id} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-3">
                    <div className="mb-1 flex items-center justify-between">
                      <p className="text-sm font-semibold text-slate-800">{item.order_id}</p>
                      <p className="text-xs font-semibold text-slate-500">{(item.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <p className="text-xs text-slate-500">{item.action_type}</p>
                  </div>
                ))}
                {!queue.length && <p className="text-sm text-slate-500">No pending recommendations.</p>}
              </div>
            </Card>
          </div>

          <Card className="p-5">
            <div className="mb-4 flex items-center gap-2"><BrainCircuit size={18} className="text-primary" /><h2 className="font-display text-lg font-bold text-slate-900">Agent Runtime</h2></div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {agents.map((agent) => (
                <div key={agent.name} className="rounded-2xl border border-slate-200 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <p className="text-sm font-semibold text-slate-800">{agent.name}</p>
                    {agent.status === "enforcing" ? <ShieldAlert size={15} className="text-amber-600" /> : <CheckCircle2 size={15} className="text-emerald-600" />}
                  </div>
                  <p className="text-xs text-slate-500">{agent.hint}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <span className="metric-chip inline-flex items-center gap-1"><Clock3 size={12} /> Avg latency {kpi.avg_response_latency_ms.toFixed(1)}ms</span>
              <span className="metric-chip inline-flex items-center gap-1"><AlertTriangle size={12} /> Projected avoided delays {kpi.projected_avoided_delays}</span>
            </div>
          </Card>
        </motion.div>
      </DashboardShell>
    </AuthGuard>
  );
}
