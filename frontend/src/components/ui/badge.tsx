import { cn } from "@/lib/utils";

export function Badge({ label, tone = "slate" }: { label: string; tone?: "red" | "amber" | "green" | "blue" | "slate" }) {
  const palette = {
    red: "bg-red-100 text-red-700 border-red-200",
    amber: "bg-amber-100 text-amber-700 border-amber-200",
    green: "bg-emerald-100 text-emerald-700 border-emerald-200",
    blue: "bg-blue-100 text-blue-700 border-blue-200",
    slate: "bg-slate-100 text-slate-700 border-slate-200",
  }[tone];

  return <span className={cn("rounded-full border px-2.5 py-1 text-xs font-semibold", palette)}>{label}</span>;
}
