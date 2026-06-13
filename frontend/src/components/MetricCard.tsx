import { colors, styles, hoverCard } from "@/lib/theme";

interface MetricCardProps {
  label: string;
  value: string | number;
  /** Optional small description shown below the value */
  desc?: string;
  /** Optional color override for the value (defaults to text primary) */
  valueColor?: string;
}

/**
 * Generic metric tile — used for RMSE, MAE, MAPE, Sharpe Ratio, etc.
 * Example: <MetricCard label="RMSE" value={12.5} />
 *          <MetricCard label="Sharpe Ratio" value={1.8} />
 */
export default function MetricCard({
  label,
  value,
  desc,
  valueColor,
}: MetricCardProps) {
  return (
    <div className={`p-4 rounded-xl ${hoverCard}`} style={styles.card}>
      <div className="text-xs mb-1" style={{ color: colors.textMuted }}>
        {label}
      </div>
      <div
        className="text-2xl font-bold"
        style={{ color: valueColor ?? colors.textPrimary }}
      >
        {value}
      </div>
      {desc && (
        <div className="text-xs mt-1" style={{ color: colors.textFaint }}>
          {desc}
        </div>
      )}
    </div>
  );
}