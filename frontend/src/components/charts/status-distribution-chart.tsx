"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#0a4da2", "#0f766e", "#f59e0b", "#dc2626", "#475569"];

export function StatusDistributionChart({ data }: { data: Array<{ status: string; count: number }> }) {
  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="status" outerRadius={95} innerRadius={45} label>
            {data.map((entry, idx) => (
              <Cell key={entry.status} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}