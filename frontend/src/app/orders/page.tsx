"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Filter, Search } from "lucide-react";
import { AuthGuard } from "@/components/layout/auth-guard";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiFetch, getToken } from "@/lib/api";
import { Order } from "@/lib/types";

function riskBadge(order: Order) {
  if (order.priority === "critical") return <Badge label="Critico" tone="red" />;
  if (order.priority === "high") return <Badge label="Alto" tone="amber" />;
  if (order.priority === "medium") return <Badge label="Medio" tone="blue" />;
  return <Badge label="Baixo" tone="green" />;
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    const token = getToken();
    apiFetch<Order[]>("/api/v1/orders", {}, token).then(setOrders).catch(console.error);
  }, []);

  const filtered = useMemo(() => {
    if (!q) return orders;
    const s = q.toLowerCase();
    return orders.filter((o) => o.order_id.toLowerCase().includes(s) || o.city.toLowerCase().includes(s) || o.region.toLowerCase().includes(s));
  }, [orders, q]);

  return (
    <AuthGuard>
      <DashboardShell>
        <div className="space-y-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="font-display text-2xl font-bold text-slate-900">Grade Inteligente de Ordens</h1>
              <p className="text-sm text-slate-500">Visao operacional com contexto de risco da IA e abertura rapida de caso.</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-72">
                <Search size={14} className="absolute left-3 top-3 text-slate-400" />
                <Input className="pl-8" placeholder="Buscar por ordem, cidade, regiao" value={q} onChange={(e) => setQ(e.target.value)} />
              </div>
              <button className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700">
                <Filter size={14} /> Filtros
              </button>
            </div>
          </div>

          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-4 py-3 text-left">Ordem</th>
                    <th className="px-4 py-3 text-left">Local</th>
                    <th className="px-4 py-3 text-left">Servico</th>
                    <th className="px-4 py-3 text-left">Risco</th>
                    <th className="px-4 py-3 text-left">Tecnico</th>
                    <th className="px-4 py-3 text-left">SLA Restante</th>
                    <th className="px-4 py-3 text-left">Acao</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.slice(0, 200).map((o) => (
                    <tr key={o.order_id} className="border-t border-slate-100 hover:bg-slate-50/70">
                      <td className="px-4 py-3"><p className="font-semibold text-slate-800">{o.order_id}</p><p className="text-xs text-slate-500">{o.customer_id}</p></td>
                      <td className="px-4 py-3"><p className="text-slate-800">{o.city}</p><p className="text-xs text-slate-500">{o.region}</p></td>
                      <td className="px-4 py-3 text-slate-700">{o.service_type}</td>
                      <td className="px-4 py-3">{riskBadge(o)}</td>
                      <td className="px-4 py-3 text-slate-700">{o.technician_id}</td>
                      <td className="px-4 py-3 text-slate-700">{o.sla_hours_remaining.toFixed(1)}h</td>
                      <td className="px-4 py-3"><Link href={`/orders/${o.order_id}`} className="font-semibold text-primary hover:underline">Abrir Caso IA</Link></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </DashboardShell>
    </AuthGuard>
  );
}