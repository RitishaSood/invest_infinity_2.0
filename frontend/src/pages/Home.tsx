import { Link } from "react-router-dom";

const features = [
  {
    icon: "📈",
    title: "LSTM & GRU Forecasting",
    desc: "Deep learning models trained on historical price data to predict future stock movements with high accuracy.",
  },
  {
    icon: "⚖️",
    title: "Portfolio Optimization",
    desc: "Modern Portfolio Theory to find the optimal asset allocation that maximizes returns for a given risk level.",
  },
  {
    icon: "🛡️",
    title: "Risk Analysis",
    desc: "Comprehensive risk metrics including VaR, CVaR, Sharpe Ratio, and volatility breakdowns.",
  },
  {
    icon: "📊",
    title: "Interactive Charts",
    desc: "Real-time visualizations of forecasts, allocations, and performance comparisons in one dashboard.",
  },
  {
    icon: "🔍",
    title: "Model Comparison",
    desc: "Compare LSTM vs GRU outputs side-by-side using RMSE, MAE, and MAPE metrics.",
  },
  {
    icon: "💾",
    title: "Save & Revisit",
    desc: "Create an account to save forecast runs and portfolio sessions for future reference.",
  },
];

const workflow = [
  {
    step: "01",
    label: "Select Stocks",
    desc: "Pick from AAPL, MSFT, GOOGL and more",
  },
  { step: "02", label: "Choose Model", desc: "LSTM or GRU forecasting engine" },
  { step: "03", label: "Set Horizon", desc: "7, 30, 60, or 90 day outlook" },
  {
    step: "04",
    label: "Run Forecast",
    desc: "Deep learning predictions in seconds",
  },
  {
    step: "05",
    label: "Optimize Portfolio",
    desc: "MPT-based allocation recommendations",
  },
  {
    step: "06",
    label: "Analyze Risk",
    desc: "Full risk metrics and performance report",
  },
];

const techStack = [
  { name: "Python", role: "Backend & ML" },
  { name: "LSTM / GRU", role: "Forecasting" },
  { name: "React", role: "Frontend" },
  { name: "FastAPI", role: "REST API" },
  { name: "Recharts", role: "Visualizations" },
  { name: "Tailwind CSS", role: "Styling" },
];

export default function Home() {
  return (
    <div
      className="min-h-screen"
      style={{
        background:
          "linear-gradient(135deg, #0a0f1e 0%, #0d1529 50%, #0a1020 100%)",
      }}
    >
      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center text-center px-6 pt-32 pb-24 overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div
            style={{
              position: "absolute",
              top: "10%",
              left: "50%",
              transform: "translateX(-50%)",
              width: 600,
              height: 600,
              borderRadius: "50%",
              background:
                "radial-gradient(circle, rgba(0,212,255,0.05) 0%, transparent 70%)",
            }}
          />
        </div>

        <div
          className="mb-6 flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-medium"
          style={{
            borderColor: "rgba(0,212,255,0.25)",
            color: "#00d4ff",
            background: "rgba(0,212,255,0.08)",
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse" />
          AI-Powered Investment Intelligence
        </div>

        <h1
          className="text-5xl md:text-7xl font-bold tracking-tight mb-6 max-w-4xl"
          style={{ lineHeight: 1.1 }}
        >
          <span style={{ color: "#e2e8f0" }}>Forecast Smarter.</span> <br />
          <span
            style={{
              background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Invest Better.
          </span>
        </h1>

        <p className="text-lg max-w-2xl mb-10" style={{ color: "#94a3b8" }}>
          Invest Infinity combines deep learning stock forecasting with Modern
          Portfolio Theory to help you make data-driven investment decisions —
          no finance degree required.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            to="/dashboard"
            className="px-8 py-3 rounded-lg font-semibold text-sm transition-all duration-200"
            style={{
              background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
              color: "#fff",
              boxShadow: "0 0 24px rgba(0,212,255,0.25)",
            }}
          >
            Get Started Free
          </Link>
          <Link
            to="/about"
            className="px-8 py-3 rounded-lg font-semibold text-sm border transition-all duration-200"
            style={{
              borderColor: "rgba(123,94,167,0.4)",
              color: "#c4b5fd",
              background: "rgba(123,94,167,0.08)",
            }}
          >
            Learn More
          </Link>
        </div>

        {/* Mini stats */}
        <div className="mt-16 grid grid-cols-3 gap-8 text-center">
          {[
            ["6+", "Stock Symbols"],
            ["2", "DL Models"],
            ["4", "Time Horizons"],
          ].map(([val, label]) => (
            <div key={label}>
              <div className="text-3xl font-bold" style={{ color: "#00d4ff" }}>
                {val}
              </div>
              <div className="text-xs mt-1" style={{ color: "#64748b" }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section className="px-6 py-20 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-2"
            style={{ color: "#00d4ff" }}
          >
            How It Works
          </p>
          <h2 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
            From Data to Decision in 6 Steps
          </h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {workflow.map((w, i) => (
            <div
              key={w.step}
              className="relative flex flex-col items-center text-center p-4 rounded-xl"
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
              }}
            >
              {i < workflow.length - 1 && (
                <div
                  className="hidden lg:block absolute top-8 right-0 translate-x-1/2 text-xs"
                  style={{ color: "#334155" }}
                >
                  →
                </div>
              )}
              <div
                className="text-xs font-mono font-bold mb-2"
                style={{ color: "#00d4ff" }}
              >
                {w.step}
              </div>
              <div
                className="text-sm font-semibold mb-1"
                style={{ color: "#e2e8f0" }}
              >
                {w.label}
              </div>
              <div className="text-xs" style={{ color: "#64748b" }}>
                {w.desc}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section
        className="px-6 py-20"
        style={{ background: "rgba(0,0,0,0.15)" }}
      >
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p
              className="text-xs font-semibold tracking-widest uppercase mb-2"
              style={{ color: "#7b5ea7" }}
            >
              Features
            </p>
            <h2 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
              Everything You Need
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="p-6 rounded-xl transition-all duration-200 group"
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                }}
              >
                <div className="text-2xl mb-4">{f.icon}</div>
                <h3
                  className="text-sm font-semibold mb-2"
                  style={{ color: "#e2e8f0" }}
                >
                  {f.title}
                </h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "#64748b" }}
                >
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="px-6 py-20 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-2"
            style={{ color: "#00d4ff" }}
          >
            Built With
          </p>
          <h2 className="text-3xl font-bold" style={{ color: "#e2e8f0" }}>
            Technology Stack
          </h2>
        </div>
        <div className="flex flex-wrap justify-center gap-4">
          {techStack.map((t) => (
            <div
              key={t.name}
              className="px-5 py-3 rounded-lg text-center"
              style={{
                background: "rgba(0,212,255,0.05)",
                border: "1px solid rgba(0,212,255,0.15)",
              }}
            >
              <div
                className="text-sm font-semibold"
                style={{ color: "#e2e8f0" }}
              >
                {t.name}
              </div>
              <div className="text-xs mt-0.5" style={{ color: "#64748b" }}>
                {t.role}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24 text-center">
        <div
          className="max-w-2xl mx-auto p-12 rounded-2xl"
          style={{
            background:
              "linear-gradient(135deg, rgba(0,212,255,0.06), rgba(123,94,167,0.1))",
            border: "1px solid rgba(123,94,167,0.2)",
          }}
        >
          <h2 className="text-3xl font-bold mb-4" style={{ color: "#e2e8f0" }}>
            Ready to Invest Smarter?
          </h2>
          <p className="text-sm mb-8" style={{ color: "#94a3b8" }}>
            No account required. Start forecasting stocks and optimizing your
            portfolio right now.
          </p>
          <Link
            to="/dashboard"
            className="inline-block px-10 py-3 rounded-lg font-semibold text-sm"
            style={{
              background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
              color: "#fff",
              boxShadow: "0 0 32px rgba(0,212,255,0.2)",
            }}
          >
            Open Dashboard
          </Link>
        </div>
      </section>
    </div>
  );
}