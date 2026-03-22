"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { History } from "lucide-react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card } from "@/components/ui/card";
import { apiFetch, getToken } from "@/lib/api";

export default function ReplayPage() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const token = getToken();
    apiFetch(`/api/v1/replay/orders/${orderId}`, {}, token).then(setData).catch(console.error);
  }, [orderId]);

  if (!data) {
    return (
      <AuthGuard>
        <DashboardShell>
          <Card className="p-8 text-center text-slate-500">Loading incident replay...</Card>
        </DashboardShell>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2"><History size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Decision Replay - {data.order?.order_id}</h1></div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 p-4">
              <h2 className="font-semibold text-slate-900">Assessment Snapshot</h2>
              <p className="mt-2 text-sm text-slate-600">Overall risk: {((data.risk_assessment?.overall_risk_score || 0) * 100).toFixed(1)}%</p>
            </div>
            <div className="rounded-2xl border border-slate-200 p-4">
              <h2 className="font-semibold text-slate-900">Human Decision</h2>
              <p className="mt-2 text-sm text-slate-600">{data.human_decision?.decision || "pending"}</p>
              <p className="mt-1 text-xs text-slate-500">{data.human_decision?.justification || "No justification available"}</p>
            </div>
          </div>

          <div className="mt-4 space-y-2">
            {(data.timeline || []).map((event: any, index: number) => (
              <div key={`${event.event_type}-${index}`} className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700">
                <div className="flex items-center justify-between">
                  <span>{event.event_type}</span>
                  <span className="text-xs text-slate-500">{new Date(event.timestamp || event.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}
