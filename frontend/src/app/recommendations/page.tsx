"use client";

import { useEffect, useState } from "react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch, getToken } from "@/lib/api";
import { RecommendationQueue } from "@/lib/types";

export default function RecommendationsPage() {
  const [queue, setQueue] = useState<RecommendationQueue[]>([]);
  const [notes, setNotes] = useState<Record<string, string>>({});

  const loadQueue = () => {
    const token = getToken();
    apiFetch<RecommendationQueue[]>("/api/v1/recommendations/queue", {}, token).then(setQueue).catch(console.error);
  };

  useEffect(() => {
    loadQueue();
  }, []);

  async function decide(decisionId: string, approve: boolean) {
    const token = getToken();
    await apiFetch("/api/v1/recommendations/approve", {
      method: "POST",
      body: JSON.stringify({
        decision_id: decisionId,
        approve,
        justification: notes[decisionId] || "Reviewed by dispatcher",
      }),
    }, token);
    loadQueue();
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <Card>
          <h1 className="font-display text-xl font-bold">Recommendations Queue</h1>
          <p className="mt-1 text-sm text-slate-500">Critical actions require human-in-the-loop approval before execution.</p>

          <div className="mt-5 space-y-4">
            {queue.map((item) => (
              <div key={item.decision_id} className="rounded-2xl border border-slate-200 p-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-semibold">{item.order_id} • {item.action_type}</p>
                    <p className="text-xs text-slate-500">Decision {item.decision_id} • impact {(item.impact_score * 100).toFixed(1)}%</p>
                  </div>
                  <Badge label={item.status} tone="amber" />
                </div>
                <Textarea
                  className="mt-3"
                  rows={2}
                  placeholder="Human justification"
                  value={notes[item.decision_id] || ""}
                  onChange={(e) => setNotes((prev) => ({ ...prev, [item.decision_id]: e.target.value }))}
                />
                <div className="mt-3 flex gap-2">
                  <Button onClick={() => decide(item.decision_id, true)}>Approve</Button>
                  <Button variant="danger" onClick={() => decide(item.decision_id, false)}>Reject</Button>
                </div>
              </div>
            ))}
            {!queue.length && <p className="text-sm text-slate-500">No pending recommendations.</p>}
          </div>
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}
