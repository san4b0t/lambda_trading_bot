"use client";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const [price, setPrice] = useState<number>(0);
  const [side, setSide] = useState<string>("none");
  const [balance, setBalance] = useState<number>(0);
  const [status, setStatus] = useState<string>("Connecting...");

  useEffect(() => {
    const wsMarket = new WebSocket("ws://localhost:8000/ws/market");
    const wsPortfolio = new WebSocket("ws://localhost:8000/ws/portfolio");

    wsMarket.onopen = () => setStatus("Connected to Live Engine");
    wsMarket.onclose = () => setStatus("Disconnected from Engine");

    wsMarket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.data.price) {
          setPrice(parsed.data.price);
          setSide(parsed.data.side);
        }
      } catch (err) {}
    };

    wsPortfolio.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.data.balance !== undefined) {
          setBalance(parsed.data.balance);
        }
      } catch (err) {}
    };

    return () => {
      wsMarket.close();
      wsPortfolio.close();
    };
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white p-6">
      <div className="w-full max-w-md p-8 border border-zinc-800 rounded-xl bg-zinc-900 shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-xl font-bold tracking-tight">
            System Diagnostics
          </h1>
          <div className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${status.includes("Connected") ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}
            ></span>
            <p className="text-xs text-zinc-400 font-medium">{status}</p>
          </div>
        </div>

        <div className="mb-4 p-4 rounded-lg bg-indigo-950/30 border border-indigo-900/50">
          <h2 className="text-xs uppercase tracking-wider text-indigo-400 font-bold mb-1">
            Live Testnet Balance
          </h2>
          <p className="text-3xl font-mono font-semibold tracking-tight text-white">
            $
            {balance > 0
              ? balance.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })
              : "0.00"}
          </p>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-850">
            <h2 className="text-xs uppercase tracking-wider text-zinc-500 font-bold mb-1">
              BTC/USDT Local Shadow Book
            </h2>
            <p className="text-4xl font-mono font-semibold tracking-tight text-emerald-400">
              ${price > 0 ? price.toFixed(2) : "0.00"}
            </p>
          </div>

          <div className="flex justify-between items-center text-sm px-1">
            <span className="text-zinc-400">Last Action Side:</span>
            <span
              className={`font-mono uppercase font-bold text-xs px-2 py-0.5 rounded ${side === "buy" ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}
            >
              {side}
            </span>
          </div>
        </div>
      </div>
    </main>
  );
}
