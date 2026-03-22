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
  { name: "Agente de Intake", status: "active", hint: "Normalizando ordens" },
  { name: "Agente de Risco", status: "active", hint: "Atraso / no-show / reagendamento" },
  { name: "Agente de Dispatch", status: "active", hint: "Prioridade e redistribuição" },
  { name: "Agente de Policy Guard", status: "enforcing", hint: "Regras de skill e SLA" },
  { name: "Agente de Explicabilidade", status: "active", hint: "Resumo técnico e executivo" },
  { name: "Agente de Relatório Executivo", status: "active", hint: "Gargalos e impacto" },
];

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

  const headline = useMemo(() => {
    if (kpi.percent_orders_at_risk >= 50) return "Risco operacional elevado detectado";
    if (kpi.percent_orders_at_risk >= 30) return "Risco moderado, operação pode estabilizar com ação rápida";
    return "Operação estável com controle preditivo";
  }, [kpi.percent_orders_at_risk]);

  return (
    <AuthGuard>
      <DashboardShell>
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-950 via-slate-900 to-blue-950 p-6 text-white shadow-2xl">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="mb-2 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em]">
                  <Sparkles size={14} /> Inteligência Agentic de Operações
                </p>
                <h1 className="font-display text-3xl font-bold">Centro de Comando</h1>
                <p className="mt-2 text-sm text-slate-200">{headline}. Aprovação humana e políticas de negócio permanecem obrigatórias.</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-2xl border border-white/10 bg-white/10 p-3">
                  <p className="text-xs text-slate-300">Ordens em Risco</p>
                  <p className="text-xl font-bold">{kpi.percent_orders_at_risk.toFixed(1)}%</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/10 p-3">
                  <p className="text-xs text-slate-300">Impacto Operacional</p>
                  <p className="text-xl font-bold">{kpi.estimated_operational_impact.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Risco Médio de SLA</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.avg_sla_risk_score.toFixed(1)}</p><p className="mt-2 text-xs text-slate-500">Índice de risco por ordem ativa.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Taxa de Aprovação</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.approval_rate.toFixed(1)}%</p><p className="mt-2 text-xs text-slate-500">Decisões críticas aceitas por humanos.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Taxa de Override</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.override_rate.toFixed(1)}%</p><p className="mt-2 text-xs text-slate-500">Intervenções humanas sobre a IA.</p></Card>
            <Card className="p-5"><p className="text-xs uppercase tracking-wider text-slate-500">Latência de Inferência</p><p className="mt-2 text-3xl font-bold text-slate-900">{kpi.avg_response_latency_ms.toFixed(1)} ms</p><p className="mt-2 text-xs text-slate-500">Tempo de resposta do pipeline multiagente.</p></Card>
          </div>

          <div className="grid gap-5 xl:grid-cols-3">
            <Card className="xl:col-span-2 p-5">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="font-display text-lg font-bold text-slate-900">Mapa de Risco por Região</h2>
                  <p className="text-xs text-slate-500">Concentração de risco operacional em tempo quase real.</p>
                </div>
                <Badge label="Ao vivo" tone="blue" />
              </div>
              <RiskByRegionChart data={regionData} />
            </Card>

            <Card className="p-5">
              <h2 className="font-display text-lg font-bold text-slate-900">Fila de Aprovação Humana</h2>
              <p className="text-xs text-slate-500">Recomendações críticas aguardando decisão.</p>
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
                {!queue.length && <p className="text-sm text-slate-500">Sem recomendações pendentes.</p>}
              </div>
            </Card>
          </div>

          <Card className="p-5">
            <div className="mb-4 flex items-center gap-2"><BrainCircuit size={18} className="text-primary" /><h2 className="font-display text-lg font-bold text-slate-900">Runtime dos Agentes de IA</h2></div>
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
              <span className="metric-chip inline-flex items-center gap-1"><Clock3 size={12} /> Latência média {kpi.avg_response_latency_ms.toFixed(1)}ms</span>
              <span className="metric-chip inline-flex items-center gap-1"><AlertTriangle size={12} /> Atrasos evitados (proj.) {kpi.projected_avoided_delays}</span>
            </div>
          </Card>
        </motion.div>
      </DashboardShell>
    </AuthGuard>
  );
}