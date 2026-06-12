import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const allocation = [
  { name: "AAPL", value: 28 },
  { name: "MSFT", value: 24 },
  { name: "GOOGL", value: 18 },
  { name: "NVDA", value: 16 },
  { name: "AMZN", value: 14 },
];

const COLORS = ["#00d4ff", "#7b5ea7", "#5eead4", "#a78bfa", "#38bdf8"];

const stats = [
  { label: "Expected Return", value: "13.6%", desc: "Annualized" },
  { label: "Volatility", value: "17.2%", desc: "Annualized std. dev." },
  { label: "Sharpe Ratio", value: "1.58", desc: "Risk-adjusted return" },
];

export default function Portfolio() {
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
            Allocation
          </p>
          <h1 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
            Portfolio
          </h1>
          <p className="text-sm mt-2" style={{ color: "#64748b" }}>
            Optimized allocation using Modern Portfolio Theory.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Allocation Chart */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Asset Allocation
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={allocation}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  label={({ name, value }) => `${name} ${value}%`}
                  labelLine={false}
                >
                  {allocation.map((_, i) => (
                    <Cell
                      key={i}
                      fill={COLORS[i % COLORS.length]}
                      stroke="none"
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#0d1529",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 8,
                  }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Portfolio Stats */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Performance Metrics
            </h2>
            <div className="space-y-4">
              {stats.map((s) => (
                <div
                  key={s.label}
                  className="flex items-center justify-between p-4 rounded-lg"
                  style={{ background: "rgba(255,255,255,0.02)" }}
                >
                  <div>
                    <div
                      className="text-sm font-medium"
                      style={{ color: "#e2e8f0" }}
                    >
                      {s.label}
                    </div>
                    <div className="text-xs" style={{ color: "#64748b" }}>
                      {s.desc}
                    </div>
                  </div>
                  <div
                    className="text-xl font-bold"
                    style={{ color: "#00d4ff" }}
                  >
                    {s.value}
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs mt-6" style={{ color: "#475569" }}>
              Allocation generated from mock optimization run. Replace with live
              MPT engine output.
            </p>
          </div>
        </div>

        {/* Holdings table */}
        <div className="p-6 rounded-xl" style={cardStyle}>
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: "#e2e8f0" }}
          >
            Holdings Breakdown
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr
                  style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
                >
                  {["Asset", "Weight", "Expected Return", "Volatility"].map(
                    (h) => (
                      <th
                        key={h}
                        className="text-left py-2 px-3 font-medium"
                        style={{ color: "#64748b" }}
                      >
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {allocation.map((a, i) => (
                  <tr
                    key={a.name}
                    style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}
                  >
                    <td
                      className="py-3 px-3 font-medium"
                      style={{ color: "#e2e8f0" }}
                    >
                      <span
                        className="inline-block w-2 h-2 rounded-full mr-2"
                        style={{ background: COLORS[i % COLORS.length] }}
                      />
                      {a.name}
                    </td>
                    <td className="py-3 px-3" style={{ color: "#94a3b8" }}>
                      {a.value}%
                    </td>
                    <td className="py-3 px-3" style={{ color: "#34d399" }}>
                      {(10 + Math.random() * 10).toFixed(1)}%
                    </td>
                    <td className="py-3 px-3" style={{ color: "#f59e0b" }}>
                      {(15 + Math.random() * 10).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}