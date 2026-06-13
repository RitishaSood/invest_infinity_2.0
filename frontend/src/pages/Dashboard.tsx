import { useState } from "react";
import { useNavigate } from "react-router-dom";
import StockSelector from "@/components/StockSelector";
import InvestmentControls, {
  type DataPeriod,
} from "@/components/InvestmentControls";
import { colors, styles, hoverCard } from "@/lib/theme";

type StepStatus = "pending" | "loading" | "done";

export default function Dashboard() {
  const navigate = useNavigate();

  const [selectedStocks, setSelectedStocks] = useState<string[]>([
    "AAPL",
    "MSFT",
    "GOOGL",
  ]);
  const [period, setPeriod] = useState<DataPeriod>("5y");
  const [amount, setAmount] = useState(100000);
  const [riskFreeRate, setRiskFreeRate] = useState(5);

  const [fetchStatus, setFetchStatus] = useState<StepStatus>("pending");
  const [trainStatus, setTrainStatus] = useState<StepStatus>("pending");

  const handleFetchData = () => {
    setFetchStatus("loading");
    setTimeout(() => setFetchStatus("done"), 800);
  };

  const handleTrainModels = () => {
    setTrainStatus("loading");
    setTimeout(() => setTrainStatus("done"), 1200);
  };

  const statusLabel = (
    status: StepStatus,
    doneLabel: string,
    idleLabel: string,
  ) => {
    if (status === "loading") return "Running…";
    if (status === "done") return doneLabel;
    return idleLabel;
  };

  return (
    <div className="px-6 py-12" style={styles.page}>
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Workspace
          </p>
          <h1
            className="text-3xl font-bold"
            style={{ color: colors.textPrimary }}
          >
            Dashboard
          </h1>
          <p className="text-sm mt-2" style={{ color: colors.textMuted }}>
            Configure your portfolio, fetch historical data, and train
            forecasting models.
          </p>
        </div>

        {/* Step 1: Select Stocks, Period, Amount, Risk-Free Rate */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 1
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Configure Portfolio
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Choose your stocks and set up the parameters for data fetching and
            optimization.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div
            className={`lg:col-span-2 p-6 rounded-xl ${hoverCard}`}
            style={styles.card}
          >
            <StockSelector
              selected={selectedStocks}
              onChange={setSelectedStocks}
            />
          </div>
          <div className={`p-6 rounded-xl ${hoverCard}`} style={styles.card}>
            <InvestmentControls
              period={period}
              onPeriodChange={setPeriod}
              amount={amount}
              onAmountChange={setAmount}
              riskFreeRate={riskFreeRate}
              onRiskFreeRateChange={setRiskFreeRate}
            />
          </div>
        </div>

        {/* Step 2: Fetch Data */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 2
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Fetch Data
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Download historical OHLCV price data for your selected stocks.
          </p>
        </div>

        <div
          className={`p-6 rounded-xl flex items-center justify-between mb-8 ${hoverCard}`}
          style={styles.card}
        >
          <div>
            <h3
              className="text-sm font-semibold mb-1"
              style={{ color: colors.textPrimary }}
            >
              {statusLabel(fetchStatus, "Data Loaded", "Fetch Historical Data")}
            </h3>
            <p className="text-xs" style={{ color: colors.textMuted }}>
              {fetchStatus === "done"
                ? `${selectedStocks.length} stocks · ${period} history · ready for training`
                : `${selectedStocks.length} stocks · ${period} history`}
            </p>
          </div>
          <button
            onClick={handleFetchData}
            disabled={selectedStocks.length === 0 || fetchStatus === "loading"}
            className="px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-40 transition-all"
            style={
              fetchStatus === "done" ? styles.pillActive : styles.buttonPrimary
            }
          >
            {statusLabel(fetchStatus, "✓ Fetched", "Fetch Data")}
          </button>
        </div>

        {/* Step 3: Train Models */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 3
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Train Models
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            Train one LSTM and one GRU model per stock using time-based
            train/test splits.
          </p>
        </div>

        <div
          className={`p-6 rounded-xl flex items-center justify-between mb-8 ${hoverCard}`}
          style={styles.card}
        >
          <div>
            <h3
              className="text-sm font-semibold mb-1"
              style={{ color: colors.textPrimary }}
            >
              {statusLabel(trainStatus, "Models Trained", "Train LSTM & GRU")}
            </h3>
            <p className="text-xs" style={{ color: colors.textMuted }}>
              {trainStatus === "done"
                ? "Both models ready · proceed to Forecast"
                : "Trains LSTM and GRU simultaneously for each selected stock"}
            </p>
          </div>
          <button
            onClick={handleTrainModels}
            disabled={fetchStatus !== "done" || trainStatus === "loading"}
            className="px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-40 transition-all"
            style={
              trainStatus === "done" ? styles.pillActive : styles.buttonPrimary
            }
          >
            {statusLabel(trainStatus, "✓ Trained", "Train Models")}
          </button>
        </div>

        {/* Step 4: Move to Forecast */}
        <div className="mb-4">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Step 4
          </p>
          <h2
            className="text-xl font-bold mb-1"
            style={{ color: colors.textPrimary }}
          >
            Go to Forecast
          </h2>
          <p className="text-sm" style={{ color: colors.textMuted }}>
            View forecast charts, compare model accuracy, and choose a model for
            optimization.
          </p>
        </div>

        <div
          className={`p-6 rounded-xl flex items-center justify-between ${hoverCard}`}
          style={styles.card}
        >
          <div>
            <h3
              className="text-sm font-semibold mb-1"
              style={{ color: colors.textPrimary }}
            >
              Continue to Forecast
            </h3>
            <p className="text-xs" style={{ color: colors.textMuted }}>
              {trainStatus === "done"
                ? "Ready — view your forecasts"
                : "Complete the steps above first"}
            </p>
          </div>
          <button
            onClick={() => navigate("/forecast")}
            disabled={trainStatus !== "done"}
            className="px-6 py-3 rounded-lg text-sm font-semibold disabled:opacity-40 transition-all"
            style={styles.buttonPrimary}
          >
            Go to Forecast
          </button>
        </div>
      </div>
    </div>
  );
}