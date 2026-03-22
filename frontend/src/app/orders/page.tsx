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
  if (order.priority === "critical") return <Badge label="Critical" tone="red" />;
  if (order.priority === "high") return <Badge label="High" tone="amber" />;
  if (order.priority === "medium") return <Badge label="Medium" tone="blue" />;
  return <Badge label="Low" tone="green" />;
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    const token = getToken();
    apiFetch<Order[]>("/api/v1/orders?page=1&page_size=200", {}, token).then(setOrders).catch(console.error);
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
              <h1 className="font-display text-2xl font-bold text-slate-900">Orders</h1>
              <p className="text-sm text-slate-500">Operational queue enriched with risk context and intervention-ready actions.</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative w-72">
                <Search size={14} className="absolute left-3 top-3 text-slate-400" />
                <Input className="pl-8" placeholder="Search order, city, region" value={q} onChange={(e) => setQ(e.target.value)} />
              </div>
              <button className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700">
                <Filter size={14} /> Filters
              </button>
            </div>
          </div>

          <Card className="overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-4 py-3 text-left">Order</th>
                    <th className="px-4 py-3 text-left">Location</th>
                    <th className="px-4 py-3 text-left">Service</th>
                    <th className="px-4 py-3 text-left">Priority</th>
                    <th className="px-4 py-3 text-left">Technician</th>
                    <th className="px-4 py-3 text-left">SLA Remaining</th>
                    <th className="px-4 py-3 text-left">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((o) => (
                    <tr key={o.order_id} className="border-t border-slate-100 hover:bg-slate-50/70">
                      <td className="px-4 py-3"><p className="font-semibold text-slate-800">{o.order_id}</p><p className="text-xs text-slate-500">{o.customer_id}</p></td>
                      <td className="px-4 py-3"><p className="text-slate-800">{o.city}</p><p className="text-xs text-slate-500">{o.region}</p></td>
                      <td className="px-4 py-3 text-slate-700">{o.service_type}</td>
                      <td className="px-4 py-3">{riskBadge(o)}</td>
                      <td className="px-4 py-3 text-slate-700">{o.technician_id}</td>
                      <td className="px-4 py-3 text-slate-700">{o.sla_hours_remaining.toFixed(1)}h</td>
                      <td className="px-4 py-3"><Link href={`/orders/${o.order_id}`} className="font-semibold text-primary hover:underline">Open Case</Link></td>
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
