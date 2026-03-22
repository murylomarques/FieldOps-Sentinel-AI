"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, Bot, ChartNoAxesCombined, ClipboardList, Gauge, History, LogOut, ShieldCheck, Sparkles } from "lucide-react";
import { clearToken } from "@/lib/api";
import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Command Center", icon: Gauge, hint: "Live operations" },
  { href: "/orders", label: "Orders", icon: ClipboardList, hint: "Case flow" },
  { href: "/recommendations", label: "Recommendations", icon: Bot, hint: "AI approval queue" },
  { href: "/insights", label: "Executive Insights", icon: ChartNoAxesCombined, hint: "Business impact" },
  { href: "/monitoring", label: "Model Monitoring", icon: Activity, hint: "Reliability and drift" },
  { href: "/replay/ORD-DEMO-00001", label: "Replay", icon: History, hint: "Incident timeline" },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen xl:grid xl:grid-cols-[300px_1fr]">
      <aside className="grid-pattern border-r border-slate-200/70 bg-slate-50/80 p-6 backdrop-blur">
        <div className="glass-panel p-4">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-gradient-to-br from-primary to-secondary p-2 text-white shadow-lg">
              <Sparkles size={18} />
            </div>
            <div>
              <p className="font-display text-xs uppercase tracking-[0.16em] text-slate-500">FieldOps Sentinel AI</p>
              <h1 className="font-display text-lg font-bold text-slate-900">Operations Intelligence</h1>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2 text-xs text-slate-600">
            <ShieldCheck size={14} className="text-secondary" /> Critical actions with human governance
          </div>
        </div>

        <nav className="mt-5 space-y-2">
          {items.map((item) => {
            const active = pathname.startsWith(item.href.split("/").slice(0, 2).join("/"));
            const Icon = item.icon;
            return (
              <Link
                href={item.href}
                key={item.href}
                className={cn(
                  "block rounded-2xl border p-3 transition",
                  active
                    ? "border-primary/35 bg-gradient-to-r from-primary/10 to-secondary/10"
                    : "border-transparent bg-white/70 hover:border-slate-200 hover:bg-white"
                )}
              >
                <div className="flex items-center gap-3">
                  <div className={cn("rounded-xl p-2", active ? "bg-primary text-white" : "bg-slate-100 text-slate-600")}>
                    <Icon size={15} />
                  </div>
                  <div>
                    <p className={cn("text-sm font-semibold", active ? "text-slate-900" : "text-slate-700")}>{item.label}</p>
                    <p className="text-xs text-slate-500">{item.hint}</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </nav>

        <button
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
        >
          <LogOut size={15} /> Sign out
        </button>
      </aside>

      <main className="p-4 md:p-6 xl:p-8">{children}</main>
    </div>
  );
}
