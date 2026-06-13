import { useState } from "react";
import ForecastChart, { defaultForecastData } from "@/components/ForecastChart";
import ForecastCard from "@/components/ForecastCard";
import AllocationChart, {
  defaultAllocationData,
} from "@/components/AllocationChart";
import PortfolioCard from "@/components/PortfolioCard";
import type { ForecastModel } from "@/components/ModelSelector";
import { colors, styles, hoverCard } from "@/lib/theme";

interface ModelResult {
  model: ForecastModel;
  rmse: number;
  mae: number;
  mape: number;
  expectedReturn: number;
  volatility: number;
  sharpe: number;
}

const RESULTS: ModelResult[] = [
  {
    model: "LSTM",
    rmse: 2.41,
    mae: 1.87,
    mape: 1.32,
    expectedReturn: 12.4,
    volatility: 18.7,
    sharpe: 1.42,
  },
  {
    model: "GRU",
    rmse: 2.78,
    mae: 2.12,
    mape: 1.59,
    expectedReturn: 11.1,
    volatility: 17.9,
    sharpe: 1.31,
  },
];

export default function Forecast() {
  const [chosenModel, setChosenModel] = useState<ForecastModel | null>(null);
  const [optimized, setOptimized] = useState(false);

  const chosenResult = RESULTS.find((r) => r.model === chosenModel);

  return (
    <div className="px-6 py-12" style={styles.page}>
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Results
          </p>
          <h1
            className="text-3xl font-bold"
            style={{ color: colors.textPrimary }}
          >
            Forecast
          </h1>
          <p className="text-sm mt-2" style={{ color: colors.textMuted }}>
            Review forecasts from both models, compare accuracy, and choose one
            for portfolio optimization.
          </p>
        </div>

        {/* Step 5: Forecast graph */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 5
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Forecast Chart &amp; Accuracy
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Historical prices vs. LSTM and GRU predictions, with accuracy
            metrics for each model.
          </p>
        </div>

        <div className="mb-8">
          <ForecastChart data={defaultForecastData} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {RESULTS.map((r) => (
            <ForecastCard
              key={r.model}
              model={r.model}
              rmse={r.rmse}
              mae={r.mae}
              mape={r.mape}
            />
          ))}
        </div>

        {/* Step 6: Compare & choose model */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 6
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Compare &amp; Choose Model
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Review what each model's results would mean for your portfolio, then
            pick one to optimize with.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {RESULTS.map((r) => {
            const isChosen = chosenModel === r.model;
            return (
              <div
                key={r.model}
                className={`p-6 rounded-xl ${hoverCard}`}
                style={isChosen ? styles.cardSelected : styles.card}
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3
                      className="text-lg font-bold"
                      style={{ color: colors.textPrimary }}
                    >
                      {r.model}
                    </h3>
                    <p className="text-xs" style={{ color: colors.textMuted }}>
                      {r.model === "LSTM"
                        ? "Long Short-Term Memory"
                        : "Gated Recurrent Unit"}
                    </p>
                  </div>
                  {isChosen && (
                    <span
                      className="text-xs font-semibold px-3 py-1 rounded-full"
                      style={styles.pillActive}
                    >
                      Selected
                    </span>
                  )}
                </div>

                <p
                  className="text-xs font-semibold mb-2"
                  style={{ color: colors.textSecondary }}
                >
                  If used for portfolio optimization:
                </p>
                <div className="grid grid-cols-3 gap-3 mb-5">
                  {[
                    ["Expected Return", `${r.expectedReturn}%`],
                    ["Volatility", `${r.volatility}%`],
                    ["Sharpe Ratio", r.sharpe],
                  ].map(([label, val]) => (
                    <div
                      key={label}
                      className="p-3 rounded-lg"
                      style={styles.statTile}
                    >
                      <div
                        className="text-xs mb-1"
                        style={{ color: colors.textMuted }}
                      >
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

                <button
                  onClick={() => {
                    setChosenModel(r.model);
                    setOptimized(false);
                  }}
                  className="w-full py-2.5 rounded-lg text-sm font-semibold transition-all"
                  style={
                    isChosen ? styles.buttonPrimary : styles.buttonSecondary
                  }
                >
                  {isChosen
                    ? "Selected for Optimization"
                    : `Use ${r.model} for Portfolio Optimization`}
                </button>
              </div>
            );
          })}
        </div>

        {/* Step 7: Optimize Portfolio */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 7
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Optimize Portfolio
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Run Modern Portfolio Theory optimization using your chosen model's
            forecast results.
          </p>
        </div>

        <div
          className={`p-6 rounded-xl flex items-center justify-between mb-8 ${hoverCard}`}
          style={styles.card}
        >
          <div>
            <h2
              className="text-sm font-semibold mb-1"
              style={{ color: colors.textPrimary }}
            >
              Run Optimization
            </h2>
            <p className="text-xs" style={{ color: colors.textMuted }}>
              {chosenModel
                ? `Using ${chosenModel} forecast results`
                : "Select a model above to continue"}
            </p>
          </div>
          <button
            onClick={() => setOptimized(true)}
            disabled={!chosenModel}
            className="px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-40 transition-all"
            style={styles.buttonPrimary}
          >
            Optimize Portfolio
          </button>
        </div>

        {optimized && chosenResult && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AllocationChart data={defaultAllocationData} />
            <div className="space-y-4">
              <h2
                className="text-sm font-semibold"
                style={{ color: colors.textPrimary }}
              >
                Portfolio Summary — optimized using {chosenModel}
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <PortfolioCard
                  label="Expected Return"
                  value={`${chosenResult.expectedReturn}%`}
                  desc="Annualized"
                />
                <PortfolioCard
                  label="Volatility"
                  value={`${chosenResult.volatility}%`}
                  desc="Annualized std. dev."
                />
                <PortfolioCard
                  label="Sharpe Ratio"
                  value={chosenResult.sharpe}
                  desc="Risk-adjusted return"
                />
                <PortfolioCard
                  label="Assets"
                  value={defaultAllocationData.length}
                  desc="In optimized portfolio"
                />
              </div>
              <p className="text-xs" style={{ color: colors.textFaint }}>
                View full allocation breakdown and risk analytics on the
                Portfolio and Analytics pages.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}