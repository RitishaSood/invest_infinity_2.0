import { colors, styles, hoverCard } from "@/lib/theme";

interface ForecastCardProps {
  model: "LSTM" | "GRU";
  rmse: number;
  mae: number;
  mape: number;
  /** Whether this model is currently selected for portfolio optimization */
  selected?: boolean;
  /** Called when the user picks this model */
  onSelect?: () => void;
}

/**
 * Forecast accuracy summary card for a single model.
 * Example: <ForecastCard model="LSTM" rmse={12.5} mae={9.3} mape={1.32} />
 */
export default function ForecastCard({
  model,
  rmse,
  mae,
  mape,
  selected,
  onSelect,
}: ForecastCardProps) {
  return (
    <div
      className={`p-6 rounded-xl ${hoverCard}`}
      style={selected ? styles.cardSelected : styles.card}
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3
            className="text-lg font-bold"
            style={{ color: colors.textPrimary }}
          >
            {model}
          </h3>
          <p className="text-xs" style={{ color: colors.textMuted }}>
            {model === "LSTM"
              ? "Long Short-Term Memory"
              : "Gated Recurrent Unit"}
          </p>
        </div>
        {selected && (
          <span
            className="text-xs font-semibold px-3 py-1 rounded-full"
            style={styles.pillActive}
          >
            Selected
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        {[
          ["RMSE", rmse],
          ["MAE", mae],
          ["MAPE", `${mape}%`],
        ].map(([label, val]) => (
          <div key={label} className="p-3 rounded-lg" style={styles.statTile}>
            <div className="text-xs mb-1" style={{ color: colors.textMuted }}>
              {label}
            </div>
            <div
              className="text-base font-semibold"
              style={{ color: colors.textPrimary }}
            >
              {val}
            </div>
          </div>
        ))}
      </div>

      {onSelect && (
        <button
          onClick={onSelect}
          className="w-full py-2.5 rounded-lg text-sm font-semibold transition-all"
          style={selected ? styles.buttonPrimary : styles.buttonSecondary}
        >
          {selected
            ? "Selected for Optimization"
            : `Use ${model} for Portfolio Optimization`}
        </button>
      )}
    </div>
  );
}