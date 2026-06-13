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
import { colors, styles, chartColors } from "@/lib/theme";

export interface ForecastPoint {
  day: string;
  historical?: number | null;
  lstm?: number | null;
  gru?: number | null;
}

interface ForecastChartProps {
  data: ForecastPoint[];
  title?: string;
}

const defaultData: ForecastPoint[] = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1;
  const base = 180 + Math.sin(i / 4) * 8 + i * 0.6;
  return {
    day: `Day ${day}`,
    historical: i < 20 ? Math.round(base + (Math.random() - 0.5) * 4) : null,
    lstm: i >= 18 ? Math.round(base + (Math.random() - 0.5) * 6 + 2) : null,
    gru: i >= 18 ? Math.round(base + (Math.random() - 0.5) * 6 - 1) : null,
  };
});

/**
 * Historical vs predicted price chart, with separate LSTM and GRU lines.
 */
export default function ForecastChart({
  data = defaultData,
  title = "Historical vs Predicted Price",
}: ForecastChartProps) {
  return (
    <div className="p-6 rounded-xl" style={styles.card}>
      <h2
        className="text-sm font-semibold mb-4"
        style={{ color: colors.textPrimary }}
      >
        {title}
      </h2>
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
          <XAxis
            dataKey="day"
            stroke={chartColors.axis}
            fontSize={11}
            interval={3}
          />
          <YAxis
            stroke={chartColors.axis}
            fontSize={11}
            domain={["auto", "auto"]}
          />
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
          <Line
            type="monotone"
            dataKey="historical"
            name="Historical"
            stroke={chartColors.primary}
            strokeWidth={2}
            dot={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="lstm"
            name="LSTM Predicted"
            stroke={chartColors.secondary}
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="gru"
            name="GRU Predicted"
            stroke={chartColors.palette[2]}
            strokeWidth={2}
            strokeDasharray="2 3"
            dot={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export { defaultData as defaultForecastData };