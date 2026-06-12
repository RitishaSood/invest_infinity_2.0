import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const riskData = [
  { metric: "Volatility", value: 17.2 },
  { metric: "VaR (95%)", value: 4.8 },
  { metric: "CVaR (95%)", value: 6.5 },
  { metric: "Max Drawdown", value: 12.1 },
];

const returnData = Array.from({ length: 12 }, (_, i) => ({
  month: `M${i + 1}`,
  return: Math.round((Math.random() * 8 - 2) * 10) / 10,
}));

const riskMetrics = [
  { label: "Sharpe Ratio", value: "1.58" },
  { label: "Volatility", value: "17.2%" },
  { label: "VaR (95%)", value: "4.8%" },
  { label: "CVaR (95%)", value: "6.5%" },
];

export default function Analytics() {
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
            Risk & Performance
          </p>
          <h1 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
            Analytics
          </h1>
          <p className="text-sm mt-2" style={{ color: "#64748b" }}>
            Risk metrics and historical return distribution for your portfolio.
          </p>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {riskMetrics.map((m) => (
            <div key={m.label} className="p-5 rounded-xl" style={cardStyle}>
              <div className="text-xs mb-2" style={{ color: "#64748b" }}>
                {m.label}
              </div>
              <div className="text-2xl font-bold" style={{ color: "#e2e8f0" }}>
                {m.value}
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Chart */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Risk Breakdown
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={riskData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.05)"
                />
                <XAxis dataKey="metric" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#0d1529",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 8,
                  }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Bar dataKey="value" fill="#7b5ea7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Return Chart */}
          <div className="p-6 rounded-xl" style={cardStyle}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: "#e2e8f0" }}
            >
              Monthly Returns
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={returnData}>
                <defs>
                  <linearGradient
                    id="returnGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.05)"
                />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#0d1529",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: 8,
                  }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Area
                  type="monotone"
                  dataKey="return"
                  name="Return %"
                  stroke="#00d4ff"
                  fill="url(#returnGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}