"use client";
import { useEffect, useState } from "react";

interface MarketMessage {
  topic: string;
  data: {
    symbol: string;
    price: number;
    side: string;
  };
}

export default function Dashboard() {
  const [price, setPrice] = useState<number>(0);
  const [side, setSide] = useState<string>("none");
  const [status, setStatus] = useState<string>("Connecting...");

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/market");

    ws.onopen = () => {
      setStatus("Connected to Live Engine");
    };

    ws.onmessage = (event) => {
      try {
        const parsed: MarketMessage = JSON.parse(event.data);
        if (parsed.data && parsed.data.price) {
          setPrice(parsed.data.price);
          setSide(parsed.data.side);
        }
      } catch (err) {
        console.error(
          "Failed to parse incoming WebSocket message stream:",
          err,
        );
      }
    };

    ws.onclose = () => {
      setStatus("Disconnected from Engine");
    };

    return () => ws.close();
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white p-6">
      <div className="w-full max-w-md p-8 border border-zinc-800 rounded-xl bg-zinc-900 shadow-2xl">
        <h1 className="text-2xl font-bold tracking-tight mb-2">
          System Diagnostics
        </h1>
        <div className="flex items-center gap-2 mb-6">
          <span
            className={`h-2.5 w-2.5 rounded-full ${status.includes("Connected") ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}
          ></span>
          <p className="text-xs text-zinc-400 font-medium">{status}</p>
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
