import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { colors, styles, chartColors } from "@/lib/theme";

export interface ReturnPoint {
  month: string;
  return: number;
}

interface ReturnChartProps {
  data: ReturnPoint[];
  title?: string;
}

const defaultData: ReturnPoint[] = Array.from({ length: 12 }, (_, i) => ({
  month: `M${i + 1}`,
  return: Math.round((Math.random() * 8 - 2) * 10) / 10,
}));

/**
 * Area chart of monthly portfolio returns.
 */
export default function ReturnChart({
  data = defaultData,
  title = "Monthly Returns",
}: ReturnChartProps) {
  return (
    <div className="p-6 rounded-xl" style={styles.card}>
      <h2
        className="text-sm font-semibold mb-4"
        style={{ color: colors.textPrimary }}
      >
        {title}
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="returnGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="0%"
                stopColor={chartColors.primary}
                stopOpacity={0.4}
              />
              <stop
                offset="100%"
                stopColor={chartColors.primary}
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
          <XAxis dataKey="month" stroke={chartColors.axis} fontSize={11} />
          <YAxis stroke={chartColors.axis} fontSize={11} />
          <Tooltip
            contentStyle={{
              background: chartColors.tooltipBg,
              border: `1px solid ${chartColors.tooltipBorder}`,
              borderRadius: 8,
            }}
            labelStyle={{ color: colors.textPrimary }}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: colors.textSecondary }}
          />
          <Area
            type="monotone"
            dataKey="return"
            name="Return %"
            stroke={chartColors.primary}
            fill="url(#returnGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export { defaultData as defaultReturnData };