"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
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
  return <Badge label="Standard" tone="blue" />;
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
    return orders.filter((o) => o.order_id.toLowerCase().includes(q.toLowerCase()) || o.city.toLowerCase().includes(q.toLowerCase()));
  }, [orders, q]);

  return (
    <AuthGuard>
      <DashboardShell>
        <Card>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <h1 className="font-display text-xl font-bold">Orders Control Tower</h1>
            <Input className="max-w-sm" placeholder="Search order_id or city" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-slate-500">
                <tr>
                  <th className="pb-2 text-left">Order</th>
                  <th className="pb-2 text-left">Region</th>
                  <th className="pb-2 text-left">Priority</th>
                  <th className="pb-2 text-left">Technician</th>
                  <th className="pb-2 text-left">SLA Hours</th>
                  <th className="pb-2 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((o) => (
                  <tr key={o.order_id} className="border-t border-slate-100">
                    <td className="py-3">{o.order_id}<div className="text-xs text-slate-500">{o.city}</div></td>
                    <td>{o.region}</td>
                    <td>{riskBadge(o)}</td>
                    <td>{o.technician_id}</td>
                    <td>{o.sla_hours_remaining.toFixed(1)}</td>
                    <td>
                      <Link href={`/orders/${o.order_id}`} className="font-semibold text-primary">Open case</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </DashboardShell>
    </AuthGuard>
  );
}
