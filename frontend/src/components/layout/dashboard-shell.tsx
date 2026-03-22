"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, Bot, ChartNoAxesCombined, ClipboardList, Gauge, LogOut, Sparkles } from "lucide-react";
import { clearToken } from "@/lib/api";
import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Command Center", icon: Gauge },
  { href: "/orders", label: "Orders", icon: ClipboardList },
  { href: "/recommendations", label: "Recommendations", icon: Bot },
  { href: "/insights", label: "Executive Insights", icon: ChartNoAxesCombined },
  { href: "/monitoring", label: "Model Monitoring", icon: Activity },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen md:grid md:grid-cols-[270px_1fr]">
      <aside className="border-r border-slate-200 bg-white/80 p-5 backdrop-blur">
        <div className="mb-8 flex items-center gap-3">
          <div className="rounded-xl bg-primary p-2 text-white"><Sparkles size={18} /></div>
          <div>
            <p className="font-display text-sm text-slate-500">FIELDOPS SENTINEL AI</p>
            <h1 className="font-display text-lg font-bold">Operations Command</h1>
          </div>
        </div>
        <nav className="space-y-2">
          {items.map((item) => {
            const active = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                href={item.href}
                key={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold transition",
                  active ? "bg-primary text-white" : "text-slate-600 hover:bg-slate-100"
                )}
              >
                <Icon size={16} /> {item.label}
              </Link>
            );
          })}
        </nav>

        <button
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
          className="mt-10 flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          <LogOut size={15} /> Sign out
        </button>
      </aside>
      <main className="p-5 md:p-8">{children}</main>
    </div>
  );
}
