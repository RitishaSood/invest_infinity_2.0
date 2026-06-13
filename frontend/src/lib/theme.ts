/**
 * Invest Infinity — Design Tokens
 * Place at: frontend/src/lib/theme.ts
 *
 * Single source of truth for colors, gradients, and shared style objects.
 * Derived from the logo palette: teal/cyan (#00d4ff) -> purple (#7b5ea7).
 *
 * Usage:
 *   import { colors, styles, gradients, chartColors, hoverCard } from "@/lib/theme";
 *   <div style={styles.page}>
 *   <div className={`p-6 rounded-xl ${hoverCard}`} style={styles.card}>
 *   <button style={active ? styles.pillActive : styles.pillInactive}>
 */

import type { CSSProperties } from "react";

// ---------------------------------------------------------------------------
// Raw color tokens
// ---------------------------------------------------------------------------
export const colors = {
  // Background gradient stops (dark navy/blue from logo background)
  bgStart: "#0a0f1e",
  bgMid: "#0d1529",
  bgEnd: "#0a1020",

  // Logo accent colors (used sparingly — labels, brand glyph, charts)
  cyan: "#00d4ff",
  purple: "#7b5ea7",
  purpleLight: "#c4b5fd",

  // Text
  textPrimary: "#e2e8f0",
  textSecondary: "#94a3b8",
  textMuted: "#64748b",
  textFaint: "#475569",

  // Status colors
  success: "#34d399",
  danger: "#f87171",
  warning: "#f59e0b",

  // Surfaces / borders
  surface: "rgba(255,255,255,0.03)",
  surfaceHover: "rgba(255,255,255,0.04)",
  surfaceSubtle: "rgba(255,255,255,0.02)",
  border: "rgba(255,255,255,0.06)",
  borderStrong: "rgba(255,255,255,0.08)",

  // Selected / active state — SINGLE PURPLE CONVENTION for all buttons
  selectedBg: "rgba(123,94,167,0.18)",
  selectedBgStrong: "rgba(123,94,167,0.25)",
  selectedBorder: "rgba(123,94,167,0.4)",
  selectedBorderStrong: "rgba(123,94,167,0.45)",
  selectedText: "#c4b5fd",

  // Accent highlight (cyan, for eyebrow labels / stat numbers — not buttons)
  accentBg: "rgba(0,212,255,0.05)",
  accentBorder: "rgba(0,212,255,0.15)",
  accentText: "#00d4ff",
} as const;

// ---------------------------------------------------------------------------
// Gradients (kept minimal — only for backgrounds & brand glyph text)
// ---------------------------------------------------------------------------
export const gradients = {
  pageBackground: `linear-gradient(135deg, ${colors.bgStart} 0%, ${colors.bgMid} 50%, ${colors.bgEnd} 100%)`,
  navFooterBackground: `linear-gradient(135deg, ${colors.bgStart} 0%, ${colors.bgMid} 60%, ${colors.bgEnd} 100%)`,
  brandText: `linear-gradient(90deg, ${colors.cyan}, ${colors.purple})`,
} as const;

// ---------------------------------------------------------------------------
// Reusable style objects (React.CSSProperties)
// ---------------------------------------------------------------------------
export const styles: Record<string, CSSProperties> = {
  // Page wrapper
  page: {
    minHeight: "100vh",
    background: gradients.pageBackground,
  },

  // Card / panel container
  card: {
    background: colors.surface,
    border: `1px solid ${colors.border}`,
  },

  // Card highlighted as "chosen" (e.g. selected model card on Dashboard)
  cardSelected: {
    background: colors.selectedBg,
    border: `1px solid ${colors.selectedBorderStrong}`,
  },

  // Inner stat tile inside a card
  statTile: {
    background: colors.surfaceSubtle,
  },

  // Pill / toggle button — inactive (stocks, models, horizons, nav links)
  pillInactive: {
    background: colors.surfaceHover,
    color: colors.textSecondary,
    border: `1px solid ${colors.borderStrong}`,
  },

  // Pill / toggle button — active/selected (SINGLE PURPLE)
  pillActive: {
    background: colors.selectedBg,
    color: colors.selectedText,
    border: `1px solid ${colors.selectedBorder}`,
  },

  // Primary action button (Generate Forecast, Optimize Portfolio, Login, Submit)
  buttonPrimary: {
    background: colors.selectedBgStrong,
    color: colors.selectedText,
    border: `1px solid ${colors.selectedBorderStrong}`,
  },

  // Secondary / outline button
  buttonSecondary: {
    background: colors.surfaceHover,
    color: colors.textSecondary,
    border: `1px solid ${colors.borderStrong}`,
  },

  // Input fields
  input: {
    background: colors.surfaceHover,
    border: `1px solid ${colors.borderStrong}`,
    color: colors.textPrimary,
  },

  // Nav/footer bar background
  navFooter: {
    background: gradients.navFooterBackground,
  },

  // Badge / eyebrow text (cyan accent)
  eyebrow: {
    color: colors.accentText,
  },

  // Brand gradient text (hero headline highlight, logo glyph)
  brandText: {
    background: gradients.brandText,
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
};

// ---------------------------------------------------------------------------
// Hover-pop card class
// ---------------------------------------------------------------------------
/**
 * Apply alongside `styles.card` for a subtle "pop up" hover effect:
 * slight lift + a soft dark shadow behind the card (no glow).
 * Usage: className={`p-6 rounded-xl ${hoverCard}`} style={styles.card}
 */
export const hoverCard =
  "transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_12px_24px_-8px_rgba(0,0,0,0.6)]";

// ---------------------------------------------------------------------------
// Recharts-friendly tokens
// ---------------------------------------------------------------------------
export const chartColors = {
  primary: colors.cyan,
  secondary: colors.purple,
  grid: "rgba(255,255,255,0.05)",
  axis: colors.textMuted,
  tooltipBg: colors.bgMid,
  tooltipBorder: "rgba(255,255,255,0.1)",
  palette: ["#00d4ff", "#7b5ea7", "#5eead4", "#a78bfa", "#38bdf8"],
} as const;