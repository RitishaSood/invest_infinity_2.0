import { useState } from "react";

const STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"];
const MODELS = ["LSTM", "GRU"];
const HORIZONS = [7, 30, 60, 90];

export default function Dashboard() {
  const [selectedStocks, setSelectedStocks] = useState<string[]>([
    "AAPL",
    "MSFT",
  ]);
  const [model, setModel] = useState("LSTM");
  const [horizon, setHorizon] = useState(30);
  const [generated, setGenerated] = useState(false);

  const toggleStock = (s: string) => {
    setSelectedStocks((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s],
    );
  };

  const cardStyle = {
    background: "rgba(255,255,255,0.03)",
    border: "1px solid rgba(255,255,255,0.06)",
  };

  return (
    <div
      className="min-h-screen px-6 py-12"
      style={{
        background:
          "linear-gradient(135deg, #0a0f1e 0%, #0d1529 50%, #0a1020 100%)",
      }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={{ color: "#00d4ff" }}
          >
            Workspace
          </p>
          <h1 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
            Dashboard
          </h1>
          <p className="text-sm mt-2" style={{ color: "#64748b" }}>
            Configure your forecast and generate predictions using deep learning
            models.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Stock Selector */}
          <div className="lg:col-span-2 p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Select Stocks
            </h2>
            <div className="flex flex-wrap gap-2">
              {STOCKS.map((s) => {
                const active = selectedStocks.includes(s);
                return (
                  <button
                    key={s}
                    onClick={() => toggleStock(s)}
                    className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    style={
                      active
                        ? {
                            background:
                              "linear-gradient(90deg, #00d4ff, #7b5ea7)",
                            color: "#fff",
                          }
                        : {
                            background: "rgba(255,255,255,0.04)",
                            color: "#94a3b8",
                            border: "1px solid rgba(255,255,255,0.08)",
                          }
                    }
                  >
                    {s}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Model Selector */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Forecasting Model
            </h2>
            <div className="flex gap-2">
              {MODELS.map((m) => (
                <button
                  key={m}
                  onClick={() => setModel(m)}
                  className="flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  style={
                    model === m
                      ? {
                          background: "rgba(0,212,255,0.12)",
                          color: "#00d4ff",
                          border: "1px solid rgba(0,212,255,0.3)",
                        }
                      : {
                          background: "rgba(255,255,255,0.04)",
                          color: "#94a3b8",
                          border: "1px solid rgba(255,255,255,0.08)",
                        }
                  }
                >
                  {m}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Horizon Selector */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Forecast Horizon
            </h2>
            <div className="flex gap-2 flex-wrap">
              {HORIZONS.map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  style={
                    horizon === h
                      ? {
                          background: "rgba(123,94,167,0.18)",
                          color: "#c4b5fd",
                          border: "1px solid rgba(123,94,167,0.4)",
                        }
                      : {
                          background: "rgba(255,255,255,0.04)",
                          color: "#94a3b8",
                          border: "1px solid rgba(255,255,255,0.08)",
                        }
                  }
                >
                  {h} days
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <div
            className="lg:col-span-2 p-6 rounded-xl flex items-center justify-between"
            style={cardStyle}
          >
            <div>
              <h2
                className="text-sm font-semibold mb-1"
                style={{ color: "#e2e8f0" }}
              >
                Run Forecast
              </h2>
              <p className="text-xs" style={{ color: "#64748b" }}>
                {selectedStocks.length} stocks · {model} model · {horizon}-day
                horizon
              </p>
            </div>
            <button
              onClick={() => setGenerated(true)}
              disabled={selectedStocks.length === 0}
              className="px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-40 transition-all"
              style={{
                background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
                color: "#fff",
                boxShadow: "0 0 20px rgba(0,212,255,0.2)",
              }}
            >
              Generate Forecast
            </button>
          </div>
        </div>

        {generated && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Forecast Summary */}
            <div className="p-6 rounded-xl" style={cardStyle}>
              <h2
                className="text-sm font-semibold mb-4"
                style={{ color: "#e2e8f0" }}
              >
                Forecast Summary
              </h2>
              <div className="space-y-3">
                {selectedStocks.map((s) => (
                  <div
                    key={s}
                    className="flex items-center justify-between text-sm"
                  >
                    <span style={{ color: "#94a3b8" }}>{s}</span>
                    <span
                      className="font-mono font-semibold"
                      style={{ color: "#00d4ff" }}
                    >
                      {(Math.random() * 50 + 100).toFixed(2)} USD
                    </span>
                    <span
                      className="text-xs"
                      style={{
                        color: Math.random() > 0.5 ? "#34d399" : "#f87171",
                      }}
                    >
                      {Math.random() > 0.5 ? "+" : "-"}
                      {(Math.random() * 5).toFixed(2)}%
                    </span>
                  </div>
                ))}
              </div>
              <p className="text-xs mt-4" style={{ color: "#475569" }}>
                Model: {model} · Horizon: {horizon} days · Mock projection
                values
              </p>
            </div>

            {/* Portfolio Summary */}
            <div className="p-6 rounded-xl" style={cardStyle}>
              <h2
                className="text-sm font-semibold mb-4"
                style={{ color: "#e2e8f0" }}
              >
                Portfolio Summary
              </h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  ["Expected Return", "12.4%"],
                  ["Volatility", "18.7%"],
                  ["Sharpe Ratio", "1.42"],
                  ["Assets", `${selectedStocks.length}`],
                ].map(([label, val]) => (
                  <div
                    key={label}
                    className="p-3 rounded-lg"
                    style={{ background: "rgba(255,255,255,0.02)" }}
                  >
                    <div className="text-xs mb-1" style={{ color: "#64748b" }}>
                      {label}
                    </div>
                    <div
                      className="text-lg font-semibold"
                      style={{ color: "#e2e8f0" }}
                    >
                      {val}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}