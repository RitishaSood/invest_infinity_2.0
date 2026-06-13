import { colors, styles, hoverCard } from "@/lib/theme";

interface PortfolioCardProps {
  label: string;
  value: string | number;
  desc?: string;
}

/**
 * Portfolio-level performance tile — Expected Return, Volatility, Sharpe Ratio, etc.
 * Example: <PortfolioCard label="Sharpe Ratio" value={1.8} desc="Risk-adjusted return" />
 */
export default function PortfolioCard({
  label,
  value,
  desc,
}: PortfolioCardProps) {
  return (
    <div className={`p-4 rounded-xl ${hoverCard}`} style={styles.card}>
      <div className="text-xs mb-1" style={{ color: colors.textMuted }}>
        {label}
      </div>
      <div className="text-xl font-bold" style={{ color: colors.purpleLight }}>
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