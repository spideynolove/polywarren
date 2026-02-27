"use client";

import { useEffect, useState } from "react";
import type { Position } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function PositionTable() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_URL}/positions`);
        if (res.ok) setPositions(await res.json());
      } finally {
        setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 10_000);
    return () => clearInterval(id);
  }, []);

  return (
    <section>
      <h2 className="text-lg font-semibold mb-3">Open Positions</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400 text-left">
              <th className="py-2 pr-4">Market</th>
              <th className="py-2 pr-4">Venue</th>
              <th className="py-2 pr-4">Side</th>
              <th className="py-2 pr-4">Size</th>
              <th className="py-2">Entry</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="py-4 text-zinc-500 text-center">Loading…</td>
              </tr>
            ) : positions.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-4 text-zinc-500 text-center">No open positions</td>
              </tr>
            ) : (
              positions.map((p) => (
                <tr key={p.id} className="border-b border-zinc-900 hover:bg-zinc-900/50 transition-colors">
                  <td className="py-2 pr-4 font-mono text-xs truncate max-w-[160px]">
                    {p.market_id.slice(0, 12)}…
                  </td>
                  <td className="py-2 pr-4 text-zinc-400 capitalize">{p.venue}</td>
                  <td className={`py-2 pr-4 font-semibold ${p.side === "yes" ? "text-green-400" : "text-red-400"}`}>
                    {p.side.toUpperCase()}
                  </td>
                  <td className="py-2 pr-4">{p.size}</td>
                  <td className="py-2">{p.entry_price.toFixed(3)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
