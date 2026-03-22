"use client";

import { useEffect, useState } from "react";
import { Bot, CheckCircle2, XCircle } from "lucide-react";
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
    await apiFetch(
      "/api/v1/recommendations/approve",
      {
        method: "POST",
        body: JSON.stringify({
          decision_id: decisionId,
          approve,
          justification: notes[decisionId] || "Revisado pelo dispatcher",
        }),
      },
      token
    );
    loadQueue();
  }

  return (
    <AuthGuard>
      <DashboardShell>
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2"><Bot size={18} className="text-primary" /><h1 className="font-display text-2xl font-bold text-slate-900">Fila de Recomendacoes da IA</h1></div>
          <p className="text-sm text-slate-500">Recomendacoes de alto impacto exigem aprovacao humana explicita com justificativa.</p>

          <div className="mt-5 space-y-4">
            {queue.map((item) => (
              <div key={item.decision_id} className="rounded-2xl border border-slate-200 bg-slate-50/70 p-4">
                <div className="mb-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="font-semibold text-slate-900">{item.order_id} - {item.action_type}</p>
                    <p className="text-xs text-slate-500">Decisao {item.decision_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge label={`${(item.confidence * 100).toFixed(1)}% confianca`} tone="blue" />
                    <Badge label={`${(item.impact_score * 100).toFixed(1)}% impacto`} tone="amber" />
                    <Badge label={item.status} tone="amber" />
                  </div>
                </div>

                <Textarea
                  rows={2}
                  placeholder="Justificativa humana para trilha de auditoria"
                  value={notes[item.decision_id] || ""}
                  onChange={(e) => setNotes((prev) => ({ ...prev, [item.decision_id]: e.target.value }))}
                />

                <div className="mt-3 flex flex-wrap gap-2">
                  <Button onClick={() => decide(item.decision_id, true)} className="inline-flex items-center gap-2"><CheckCircle2 size={14} /> Aprovar</Button>
                  <Button variant="danger" onClick={() => decide(item.decision_id, false)} className="inline-flex items-center gap-2"><XCircle size={14} /> Rejeitar</Button>
                </div>
              </div>
            ))}
            {!queue.length && <p className="text-sm text-slate-500">Nao ha recomendacoes pendentes.</p>}
          </div>
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}