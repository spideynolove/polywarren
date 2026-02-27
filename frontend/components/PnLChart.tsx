"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { PnLSnapshot } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function PnLChart() {
  const [data, setData] = useState<PnLSnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_URL}/pnl`);
        if (res.ok) {
          const snapshots: PnLSnapshot[] = await res.json();
          setData([...snapshots].reverse());
        }
      } finally {
        setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, []);

  const latest = data[data.length - 1];
  const pnlColor = latest && latest.value >= 0 ? "#4ade80" : "#f87171";

  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">PnL</h2>
        {latest && (
          <span className={`text-xl font-mono font-bold ${pnlColor === "#4ade80" ? "text-green-400" : "text-red-400"}`}>
            {latest.value >= 0 ? "+" : ""}{latest.value.toFixed(4)}
          </span>
        )}
      </div>
      {loading ? (
        <div className="h-48 flex items-center justify-center text-zinc-500">Loading…</div>
      ) : data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-zinc-500">No PnL data yet</div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(v) => new Date(v).toLocaleTimeString()}
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              width={50}
            />
            <Tooltip
              contentStyle={{ background: "#18181b", border: "1px solid #3f3f46", borderRadius: 4 }}
              labelFormatter={(v) => new Date(v as string).toLocaleString()}
              formatter={(v: number) => [v.toFixed(4), "PnL"]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={pnlColor}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
