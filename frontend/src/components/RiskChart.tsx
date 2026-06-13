import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { colors, styles, chartColors } from "@/lib/theme";

export interface RiskMetricPoint {
  metric: string;
  value: number;
}

interface RiskChartProps {
  data: RiskMetricPoint[];
  title?: string;
}

const defaultData: RiskMetricPoint[] = [
  { metric: "Volatility", value: 17.2 },
  { metric: "VaR (95%)", value: 4.8 },
  { metric: "CVaR (95%)", value: 6.5 },
  { metric: "Max Drawdown", value: 12.1 },
];

/**
 * Bar chart of portfolio risk metrics (volatility, VaR, CVaR, drawdown).
 */
export default function RiskChart({
  data = defaultData,
  title = "Risk Breakdown",
}: RiskChartProps) {
  return (
    <div className="p-6 rounded-xl" style={styles.card}>
      <h2
        className="text-sm font-semibold mb-4"
        style={{ color: colors.textPrimary }}
      >
        {title}
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
          <XAxis dataKey="metric" stroke={chartColors.axis} fontSize={11} />
          <YAxis stroke={chartColors.axis} fontSize={11} />
          <Tooltip
            contentStyle={{
              background: chartColors.tooltipBg,
              border: `1px solid ${chartColors.tooltipBorder}`,
              borderRadius: 8,
            }}
            labelStyle={{ color: colors.textPrimary }}
          />
          <Bar
            dataKey="value"
            fill={chartColors.secondary}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export { defaultData as defaultRiskData };