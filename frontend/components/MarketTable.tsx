"use client";

import { useEffect, useRef, useState } from "react";
import type { Tick } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function MarketTable() {
  const [ticks, setTicks] = useState<Tick[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource(`${API_URL}/stream/ticks`);
    esRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.onmessage = (e) => {
      try {
        const data: Tick[] = JSON.parse(e.data);
        setTicks(data.slice(0, 50));
      } catch {}
    };

    return () => {
      es.close();
      setConnected(false);
    };
  }, []);

  return (
    <section>
      <div className="flex items-center gap-2 mb-3">
        <h2 className="text-lg font-semibold">Live Markets</h2>
        <span
          className={`inline-block w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-red-500"}`}
          title={connected ? "connected" : "disconnected"}
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-zinc-800 text-zinc-400 text-left">
              <th className="py-2 pr-4">Symbol</th>
              <th className="py-2 pr-4">Venue</th>
              <th className="py-2 pr-4">YES</th>
              <th className="py-2 pr-4">NO</th>
              <th className="py-2">Volume</th>
            </tr>
          </thead>
          <tbody>
            {ticks.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-4 text-zinc-500 text-center">
                  Waiting for market data…
                </td>
              </tr>
            ) : (
              ticks.map((t) => (
                <tr
                  key={`${t.venue}:${t.symbol}`}
                  className="border-b border-zinc-900 hover:bg-zinc-900/50 transition-colors"
                >
                  <td className="py-2 pr-4 font-mono text-xs truncate max-w-[180px]">{t.symbol}</td>
                  <td className="py-2 pr-4 text-zinc-400 capitalize">{t.venue}</td>
                  <td className="py-2 pr-4 text-green-400">{(t.yes_price * 100).toFixed(1)}¢</td>
                  <td className="py-2 pr-4 text-red-400">{(t.no_price * 100).toFixed(1)}¢</td>
                  <td className="py-2 text-zinc-400">{t.volume != null ? t.volume.toFixed(0) : "—"}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
