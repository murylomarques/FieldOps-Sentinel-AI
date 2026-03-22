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
  const [risk, setRisk] = useState<any>(null);
  const [timeline, setTimeline] = useState<Array<{ event_type: string; created_at: string }>>([]);

  useEffect(() => {
    const token = getToken();
    apiFetch<Order>(`/api/v1/orders/${orderId}`, {}, token).then(setOrder).catch(console.error);
    apiFetch<RecommendationQueue[]>("/api/v1/recommendations", {}, token)
      .then((items) => setRecommendation(items.find((r) => r.order_id === orderId) || null))
      .catch(console.error);
    apiFetch(`/api/v1/orders/${orderId}/risk`, {}, token).then(setRisk).catch(console.error);
    apiFetch<{ events: Array<{ event_type: string; created_at: string }> }>(`/api/v1/orders/${orderId}/timeline`, {}, token)
      .then((data) => setTimeline(data.events || []))
      .catch(console.error);
  }, [orderId]);

  if (!order) {
    return (
      <AuthGuard>
        <DashboardShell>
          <Card className="p-8 text-center text-slate-500">Loading order intelligence...</Card>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="space-y-5">
          <section className="rounded-3xl border border-slate-200 bg-gradient-to-r from-slate-900 to-blue-900 p-6 text-white">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-200">AI Case Narrative</p>
            <h1 className="mt-2 font-display text-3xl font-bold">{order.order_id}</h1>
            <p className="mt-2 text-sm text-slate-200">{order.service_type} in {order.city} ({order.region}) assigned to {order.technician_id}</p>
          </section>

          <div className="grid gap-5 xl:grid-cols-3">
            <Card className="xl:col-span-2 p-5">
              <h2 className="font-display text-lg font-bold text-slate-900">Operational Timeline</h2>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Created At</p><p className="font-semibold text-slate-800">{new Date(order.created_at).toLocaleString()}</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Scheduled Window</p><p className="font-semibold text-slate-800">{new Date(order.scheduled_start).toLocaleString()} - {new Date(order.scheduled_end).toLocaleTimeString()}</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">SLA Remaining</p><p className="font-semibold text-slate-800">{order.sla_hours_remaining.toFixed(1)}h</p></div>
                <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Load and Distance</p><p className="font-semibold text-slate-800">Load {order.technician_load} / {order.distance_km}km</p></div>
              </div>

              {risk && (
                <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 text-sm text-slate-700">
                  <p className="mb-1 font-semibold">Risk Snapshot</p>
                  Overall {(risk.overall_risk_score * 100).toFixed(1)}% | Delay {(risk.risk_delay_score * 100).toFixed(1)}% | No-show {(risk.risk_no_show_score * 100).toFixed(1)}% | Reschedule {(risk.risk_reschedule_score * 100).toFixed(1)}% | SLA breach {(risk.risk_sla_breach_score * 100).toFixed(1)}%
                </div>
              )}

              <div className="mt-4 rounded-2xl border border-slate-200 p-4">
                <p className="mb-2 text-sm font-semibold text-slate-900">Event Replay</p>
                <div className="space-y-2 text-xs text-slate-600">
                  {timeline.slice(-8).map((event, index) => (
                    <div key={`${event.event_type}-${index}`} className="flex items-center justify-between rounded-xl border border-slate-100 px-3 py-2">
                      <span>{event.event_type}</span>
                      <span>{new Date(event.created_at).toLocaleString()}</span>
                    </div>
                  ))}
                  {!timeline.length && <p>No events recorded yet.</p>}
                </div>
              </div>
            </Card>

            <Card className="p-5">
              <div className="mb-3 flex items-center gap-2"><Brain size={16} className="text-primary" /><h2 className="font-display text-lg font-bold text-slate-900">Recommendation</h2></div>

              {recommendation ? (
                <div className="space-y-3 text-sm">
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Decision ID</p><p className="font-semibold text-slate-800">{recommendation.decision_id}</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Action</p><p className="font-semibold text-slate-800">{recommendation.action_type}</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Confidence</p><p className="font-semibold text-slate-800">{(recommendation.confidence * 100).toFixed(1)}%</p></div>
                  <div className="rounded-2xl border border-slate-200 p-3"><p className="text-xs text-slate-500">Impact</p><p className="font-semibold text-slate-800">{(recommendation.impact_score * 100).toFixed(1)}%</p></div>
                  <Badge label={recommendation.status} tone="amber" />
                </div>
              ) : (
                <p className="text-sm text-slate-500">No recommendation available for this order.</p>
              )}

              <div className="mt-4 space-y-2 text-xs text-slate-600">
                <p className="inline-flex items-center gap-1"><ShieldCheck size={13} /> Policy guard is active</p>
                <p className="inline-flex items-center gap-1"><Timer size={13} /> High-impact actions require human approval</p>
              </div>
            </Card>
          </div>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}
