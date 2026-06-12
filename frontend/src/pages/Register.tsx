import { Link } from "react-router-dom";

export default function Register() {
  const inputStyle = {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    color: "#e2e8f0",
  };

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
            Create Account
          </h1>
          <p className="text-sm mt-1" style={{ color: "#64748b" }}>
            Save your forecasts and portfolio runs
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
              Name
            </label>
            <input
              type="text"
              placeholder="Jane Doe"
              className="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style={inputStyle}
            />
          </div>
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
              className="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style={inputStyle}
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
              className="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style={inputStyle}
            />
          </div>
          <div>
            <label
              className="block text-xs font-medium mb-1.5"
              style={{ color: "#94a3b8" }}
            >
              Confirm Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full px-3 py-2 rounded-lg text-sm outline-none"
              style={inputStyle}
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
            Create Account
          </button>

          <p className="text-center text-xs" style={{ color: "#64748b" }}>
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-medium"
              style={{ color: "#00d4ff" }}
            >
              Login
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}