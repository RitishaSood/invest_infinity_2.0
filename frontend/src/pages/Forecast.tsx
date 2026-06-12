import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const mockData = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1;
  const base = 180 + Math.sin(i / 4) * 8 + i * 0.6;
  return {
    day: `Day ${day}`,
    historical: i < 20 ? Math.round(base + (Math.random() - 0.5) * 4) : null,
    predicted:
      i >= 18 ? Math.round(base + (Math.random() - 0.5) * 6 + 2) : null,
  };
});

const metrics = [
  { label: "RMSE", value: "2.41", desc: "Root Mean Squared Error" },
  { label: "MAE", value: "1.87", desc: "Mean Absolute Error" },
  { label: "MAPE", value: "1.32%", desc: "Mean Absolute % Error" },
];

export default function Forecast() {
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
        <div className="mb-10 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <p
              className="text-xs font-semibold tracking-widest uppercase mb-1"
              style={{ color: "#00d4ff" }}
            >
              Results
            </p>
            <h1 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
              Forecast
            </h1>
            <p className="text-sm mt-2" style={{ color: "#64748b" }}>
              AAPL · 30-day horizon · Model:{" "}
              <span style={{ color: "#c4b5fd" }}>LSTM</span>
            </p>
          </div>
        </div>

        {/* Chart */}
        <div className="p-6 rounded-xl mb-8" style={cardStyle}>
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "#e2e8f0" }}
          >
            Historical vs Predicted Price
          </h2>
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={mockData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.05)"
              />
              <XAxis
                dataKey="day"
                stroke="#64748b"
                fontSize={11}
                interval={3}
              />
              <YAxis stroke="#64748b" fontSize={11} domain={["auto", "auto"]} />
              <Tooltip
                contentStyle={{
                  background: "#0d1529",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                }}
                labelStyle={{ color: "#e2e8f0" }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Line
                type="monotone"
                dataKey="historical"
                name="Historical"
                stroke="#00d4ff"
                strokeWidth={2}
                dot={false}
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="predicted"
                name="Predicted"
                stroke="#7b5ea7"
                strokeWidth={2}
                strokeDasharray="5 4"
                dot={false}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {metrics.map((m) => (
            <div key={m.label} className="p-6 rounded-xl" style={cardStyle}>
              <div
                className="text-xs font-semibold tracking-widest uppercase mb-2"
                style={{ color: "#00d4ff" }}
              >
                {m.label}
              </div>
              <div
                className="text-3xl font-bold mb-1"
                style={{ color: "#e2e8f0" }}
              >
                {m.value}
              </div>
              <div className="text-xs" style={{ color: "#64748b" }}>
                {m.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}