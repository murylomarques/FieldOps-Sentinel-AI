"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Brain, ShieldCheck, Timer } from "lucide-react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { apiFetch, getToken } from "@/lib/api";
import { Order, RecommendationQueue } from "@/lib/types";

export default function OrderDetailPage() {
  const params = useParams<{ orderId: string }>();
  const orderId = params.orderId;
  const [order, setOrder] = useState<Order | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationQueue | null>(null);

  useEffect(() => {
    const token = getToken();
    apiFetch<Order>(`/api/v1/orders/${orderId}`, {}, token).then(setOrder).catch(console.error);
    apiFetch<RecommendationQueue[]>("/api/v1/recommendations/queue", {}, token)
      .then((items) => setRecommendation(items.find((r) => r.order_id === orderId) || null))
      .catch(console.error);
  }, [orderId]);

  if (!order) {
    return (
      <AuthGuard>
        <DashboardShell>
          <Card className="p-8 text-center text-slate-500">Carregando inteligencia do caso...</Card>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="space-y-5">
          <section className="rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-900 to-blue-900 p-6 text-white">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-200">Narrativa de Caso com IA</p>
            <h1 className="mt-2 font-display text-3xl font-bold">{order.order_id}</h1>
            <p className="mt-2 text-sm text-slate-200">{order.service_type} em {order.city} ({order.region}) - tecnico {order.technician_id}</p>
          </section>

          <div className="grid gap-5 xl:grid-cols-3">
            <Card className="xl:col-span-2 p-5">
              <h2 className="font-display text-lg font-bold text-slate-900">Timeline Operacional</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Criada em</p><p className="font-semibold text-slate-800">{new Date(order.created_at).toLocaleString()}</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Janela Agendada</p><p className="font-semibold text-slate-800">{new Date(order.scheduled_start).toLocaleString()} - {new Date(order.scheduled_end).toLocaleTimeString()}</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">SLA Restante</p><p className="font-semibold text-slate-800">{order.sla_hours_remaining.toFixed(1)}h</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Carga e Distancia</p><p className="font-semibold text-slate-800">Carga {order.technician_load} / {order.distance_km}km</p></div>
              </div>

              <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-sm text-slate-700">
                <p className="mb-1 font-semibold">Fatores de Contexto da IA</p>
                Trafego {order.traffic_level}, chuva {order.rain_level}, reagendamentos previos {order.previous_reschedules}, historico de no-show do cliente {order.customer_history_no_show}.
              </div>
            </Card>

            <Card className="p-5">
              <div className="mb-3 flex items-center gap-2"><Brain size={16} className="text-primary" /><h2 className="font-display text-lg font-bold text-slate-900">Recomendacao da IA</h2></div>

              {recommendation ? (
                <div className="space-y-3 text-sm">
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">ID da Decisao</p><p className="font-semibold text-slate-800">{recommendation.decision_id}</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Acao</p><p className="font-semibold text-slate-800">{recommendation.action_type}</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Confianca</p><p className="font-semibold text-slate-800">{(recommendation.confidence * 100).toFixed(1)}%</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Impacto</p><p className="font-semibold text-slate-800">{(recommendation.impact_score * 100).toFixed(1)}%</p></div>
                  <Badge label={recommendation.status} tone="amber" />
                </div>
              ) : (
                <p className="text-sm text-slate-500">Nao ha recomendacao pendente para este caso.</p>
              )}

              <div className="mt-4 space-y-2 text-xs text-slate-600">
                <p className="inline-flex items-center gap-1"><ShieldCheck size={13} /> Policy Guard ativo</p>
                <p className="inline-flex items-center gap-1"><Timer size={13} /> Acao de alto impacto exige aprovacao humana</p>
              </div>
            </Card>
          </div>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}