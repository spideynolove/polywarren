import MarketTable from "@/components/MarketTable";
import PositionTable from "@/components/PositionTable";
import PnLChart from "@/components/PnLChart";

export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <main className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">polywarren</h1>
        <a
          href="/api/healthz"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-zinc-500 hover:text-zinc-300 font-mono transition-colors"
        >
          /healthz
        </a>
      </header>

      <PnLChart />
      <MarketTable />
      <PositionTable />
    </main>
  );
}
