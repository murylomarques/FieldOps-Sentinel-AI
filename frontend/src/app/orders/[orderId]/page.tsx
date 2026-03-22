"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
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
          <p>Loading order...</p>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="grid gap-5 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <h1 className="font-display text-2xl font-bold">{order.order_id}</h1>
            <p className="mt-2 text-sm text-slate-500">Timeline and operational context for this field service case.</p>
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-slate-500">Customer</span><p>{order.customer_id}</p></div>
              <div><span className="text-slate-500">Region</span><p>{order.region}</p></div>
              <div><span className="text-slate-500">Service Type</span><p>{order.service_type}</p></div>
              <div><span className="text-slate-500">Technician Skill</span><p>{order.technician_skill}</p></div>
              <div><span className="text-slate-500">SLA Remaining</span><p>{order.sla_hours_remaining.toFixed(1)} hours</p></div>
              <div><span className="text-slate-500">Traffic / Rain</span><p>{order.traffic_level} / {order.rain_level}</p></div>
            </div>
          </Card>

          <Card>
            <h2 className="font-display text-lg font-semibold">Agent Recommendation</h2>
            {recommendation ? (
              <div className="mt-4 space-y-2 text-sm">
                <p>Decision ID: <span className="font-semibold">{recommendation.decision_id}</span></p>
                <p>Action: {recommendation.action_type}</p>
                <p>Confidence: {(recommendation.confidence * 100).toFixed(1)}%</p>
                <Badge label={recommendation.status} tone="amber" />
              </div>
            ) : (
              <p className="mt-4 text-sm text-slate-500">No pending recommendation for this order.</p>
            )}
          </Card>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}
