import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { colors, styles, chartColors } from "@/lib/theme";

export interface AllocationSlice {
  name: string;
  value: number;
}

interface AllocationChartProps {
  data: AllocationSlice[];
  title?: string;
}

const defaultData: AllocationSlice[] = [
  { name: "AAPL", value: 28 },
  { name: "MSFT", value: 24 },
  { name: "GOOGL", value: 18 },
  { name: "NVDA", value: 16 },
  { name: "AMZN", value: 14 },
];

/**
 * Donut chart showing optimized portfolio asset allocation.
 */
export default function AllocationChart({
  data = defaultData,
  title = "Asset Allocation",
}: AllocationChartProps) {
  return (
    <div className="p-6 rounded-xl" style={styles.card}>
      <h2
        className="text-sm font-semibold mb-4"
        style={{ color: colors.textPrimary }}
      >
        {title}
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
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
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={chartColors.palette[i % chartColors.palette.length]}
                stroke="none"
              />
            ))}
          </Pie>
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
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export { defaultData as defaultAllocationData };