import { colors, styles } from "@/lib/theme";

const PERIODS = ["1y", "2y", "5y", "10y"] as const;
export type DataPeriod = (typeof PERIODS)[number];

interface InvestmentControlsProps {
  period: DataPeriod;
  onPeriodChange: (period: DataPeriod) => void;
  amount: number;
  onAmountChange: (amount: number) => void;
  riskFreeRate: number;
  onRiskFreeRateChange: (rate: number) => void;
}

/**
 * Historical data period, investment amount, and risk-free rate controls.
 * Used on the Dashboard's Step 1 alongside StockSelector.
 */
export default function InvestmentControls({
  period,
  onPeriodChange,
  amount,
  onAmountChange,
  riskFreeRate,
  onRiskFreeRateChange,
}: InvestmentControlsProps) {
  return (
    <div className="space-y-6">
      {/* Historical data period */}
      <div>
        <h2
          className="text-sm font-semibold mb-3"
          style={{ color: colors.textPrimary }}
        >
          Historical Data Period
        </h2>
        <div className="flex gap-2 flex-wrap">
          {PERIODS.map((p) => {
            const active = period === p;
            return (
              <button
                key={p}
                type="button"
                onClick={() => onPeriodChange(p)}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                style={active ? styles.pillActive : styles.pillInactive}
              >
                {p}
              </button>
            );
          })}
        </div>
      </div>

      {/* Investment amount */}
      <div>
        <h2
          className="text-sm font-semibold mb-3"
          style={{ color: colors.textPrimary }}
        >
          Investment Amount ($)
        </h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => onAmountChange(Math.max(1000, amount - 1000))}
            className="w-9 h-9 rounded-lg text-sm font-semibold transition-all"
            style={styles.buttonSecondary}
          >
            −
          </button>
          <input
            type="number"
            value={amount}
            onChange={(e) =>
              onAmountChange(Math.max(0, Number(e.target.value)))
            }
            className="flex-1 px-3 py-2 rounded-lg text-sm outline-none text-center"
            style={styles.input}
          />
          <button
            type="button"
            onClick={() => onAmountChange(amount + 1000)}
            className="w-9 h-9 rounded-lg text-sm font-semibold transition-all"
            style={styles.buttonSecondary}
          >
            +
          </button>
        </div>
      </div>

      {/* Risk-free rate */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2
            className="text-sm font-semibold"
            style={{ color: colors.textPrimary }}
          >
            Risk-Free Rate (%)
          </h2>
          <span
            className="text-sm font-semibold"
            style={{ color: colors.purpleLight }}
          >
            {riskFreeRate.toFixed(2)}
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={10}
          step={0.05}
          value={riskFreeRate}
          onChange={(e) => onRiskFreeRateChange(Number(e.target.value))}
          className="w-full"
          style={{ accentColor: colors.purple }}
        />
      </div>
    </div>
  );
}

export { PERIODS };