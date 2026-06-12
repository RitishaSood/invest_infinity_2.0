import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/forecast", label: "Forecast" },
  { to: "/portfolio", label: "Portfolio" },
  { to: "/analytics", label: "Analytics" },
  { to: "/about", label: "About" },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav
      className="sticky top-0 z-50 flex items-center justify-between px-4 py-2"
      style={{
        background:
          "linear-gradient(135deg, #0a0f1e 0%, #0d1529 60%, #0a1020 100%)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
      }}
    >
      {/* Logo — top left, larger, no extra padding/box */}
      <Link to="/" className="flex items-center -my-1">
        <img
          src="/logo.png"
          alt="Invest Infinity"
          className="h-24 w-auto object-contain"
        />
      </Link>

      {/* Centered pill nav */}
      <div
        className="hidden md:flex items-center gap-1 px-2 py-1.5 rounded-full absolute left-1/2 -translate-x-1/2"
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.25)",
        }}
      >
        {links.map((l) => {
          const active = pathname === l.to;
          return (
            <Link
              key={l.to}
              to={l.to}
              className="px-4 py-1.5 rounded-full text-sm font-medium transition-all"
              style={
                active
                  ? {
                      background: "rgba(0,212,255,0.12)",
                      color: "#00d4ff",
                      boxShadow: "0 0 0 1px rgba(0,212,255,0.25) inset",
                    }
                  : { color: "#94a3b8" }
              }
            >
              {l.label}
            </Link>
          );
        })}
      </div>

      {/* Login button — top right */}
      <Link
        to="/login"
        className="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
        style={{
          background: "linear-gradient(90deg, #00d4ff, #7b5ea7)",
          color: "#fff",
          boxShadow: "0 0 16px rgba(0,212,255,0.18)",
        }}
      >
        Login
      </Link>
    </nav>
  );
}