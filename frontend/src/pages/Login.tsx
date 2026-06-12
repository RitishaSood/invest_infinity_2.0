import { Link } from "react-router-dom";

export default function Login() {
  return (
    <div
      className="min-h-screen flex items-center justify-center px-6"
      style={{
        background:
          "linear-gradient(135deg, #0a0f1e 0%, #0d1529 50%, #0a1020 100%)",
      }}
    >
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center mb-4">
            <span
              className="text-3xl font-bold"
              style={{
                background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              ∞
            </span>
          </div>
          <h1 className="text-2xl font-bold" style={{ color: "#e2e8f0" }}>
            Welcome Back
          </h1>
          <p className="text-sm mt-1" style={{ color: "#64748b" }}>
            Sign in to access your saved forecasts
          </p>
        </div>

        <form
          className="p-6 rounded-xl space-y-4"
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div>
            <label
              className="block text-xs font-medium mb-1.5"
              style={{ color: "#94a3b8" }}
            >
              Email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors"
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#e2e8f0",
              }}
            />
          </div>
          <div>
            <label
              className="block text-xs font-medium mb-1.5"
              style={{ color: "#94a3b8" }}
            >
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors"
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#e2e8f0",
              }}
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-lg text-sm font-semibold transition-all"
            style={{
              background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
              color: "#fff",
              boxShadow: "0 0 20px rgba(0,212,255,0.2)",
            }}
          >
            Login
          </button>

          <p className="text-center text-xs" style={{ color: "#64748b" }}>
            Don't have an account?{" "}
            <Link
              to="/register"
              className="font-medium"
              style={{ color: "#00d4ff" }}
            >
              Register
            </Link>
          </p>
        </form>

        <p className="text-center text-xs mt-6" style={{ color: "#475569" }}>
          You can continue using forecasting and portfolio tools{" "}
          <Link to="/dashboard" style={{ color: "#7b5ea7" }}>
            without logging in
          </Link>
          .
        </p>
      </div>
    </div>
  );
}