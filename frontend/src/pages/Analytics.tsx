import RiskChart, { defaultRiskData } from "@/components/RiskChart";
import ReturnChart, { defaultReturnData } from "@/components/ReturnChart";
import MetricCard from "@/components/MetricCard";
import { colors, styles } from "@/lib/theme";

const riskMetrics = [
  { label: "Sharpe Ratio", value: "1.58" },
  { label: "Volatility", value: "17.2%" },
  { label: "VaR (95%)", value: "4.8%" },
  { label: "CVaR (95%)", value: "6.5%" },
];

export default function Analytics() {
  return (
    <div className="px-6 py-12" style={styles.page}>
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Risk & Performance
          </p>
          <h1
            className="text-3xl font-bold"
            style={{ color: colors.textPrimary }}
          >
            Analytics
          </h1>
          <p className="text-sm mt-2" style={{ color: colors.textMuted }}>
            Risk metrics and historical return distribution for your portfolio.
          </p>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {riskMetrics.map((m) => (
            <MetricCard key={m.label} label={m.label} value={m.value} />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskChart data={defaultRiskData} />
          <ReturnChart data={defaultReturnData} />
        </div>
      </div>
    </div>
  );
}