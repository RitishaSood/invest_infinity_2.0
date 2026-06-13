import AllocationChart, {
  defaultAllocationData,
} from "@/components/AllocationChart";
import PortfolioCard from "@/components/PortfolioCard";
import { colors, styles, chartColors, hoverCard } from "@/lib/theme";

export default function Portfolio() {
  return (
    <div className="px-6 py-12" style={styles.page}>
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <p
            className="text-xs font-semibold tracking-widest uppercase mb-1"
            style={styles.eyebrow}
          >
            Allocation
          </p>
          <h1
            className="text-3xl font-bold"
            style={{ color: colors.textPrimary }}
          >
            Portfolio
          </h1>
          <p className="text-sm mt-2" style={{ color: colors.textMuted }}>
            Optimized allocation using Modern Portfolio Theory, based on your
            chosen forecast model.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <AllocationChart data={defaultAllocationData} />

          {/* Portfolio Stats */}
          <div className={`p-6 rounded-xl ${hoverCard}`} style={styles.card}>
            <h2
              className="text-sm font-semibold mb-4"
              style={{ color: colors.textPrimary }}
            >
              Performance Metrics
            </h2>
            <div className="grid grid-cols-1 gap-4">
              <PortfolioCard
                label="Expected Return"
                value="13.6%"
                desc="Annualized"
              />
              <PortfolioCard
                label="Volatility"
                value="17.2%"
                desc="Annualized std. dev."
              />
              <PortfolioCard
                label="Sharpe Ratio"
                value="1.58"
                desc="Risk-adjusted return"
              />
            </div>
            <p className="text-xs mt-6" style={{ color: colors.textFaint }}>
              Allocation generated from mock optimization run. Replace with live
              MPT engine output.
            </p>
          </div>
        </div>

        {/* Holdings table */}
        <div className={`p-6 rounded-xl ${hoverCard}`} style={styles.card}>
          <h2
            className="text-sm font-semibold mb-4"
            style={{ color: colors.textPrimary }}
          >
            Holdings Breakdown
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: `1px solid ${colors.border}` }}>
                  {["Asset", "Weight", "Expected Return", "Volatility"].map(
                    (h) => (
                      <th
                        key={h}
                        className="text-left py-2 px-3 font-medium"
                        style={{ color: colors.textMuted }}
                      >
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {defaultAllocationData.map((a, i) => (
                  <tr
                    key={a.name}
                    style={{ borderBottom: `1px solid ${colors.surface}` }}
                  >
                    <td
                      className="py-3 px-3 font-medium"
                      style={{ color: colors.textPrimary }}
                    >
                      <span
                        className="inline-block w-2 h-2 rounded-full mr-2"
                        style={{
                          background:
                            chartColors.palette[i % chartColors.palette.length],
                        }}
                      />
                      {a.name}
                    </td>
                    <td
                      className="py-3 px-3"
                      style={{ color: colors.textSecondary }}
                    >
                      {a.value}%
                    </td>
                    <td className="py-3 px-3" style={{ color: colors.success }}>
                      {(10 + Math.random() * 10).toFixed(1)}%
                    </td>
                    <td className="py-3 px-3" style={{ color: colors.warning }}>
                      {(15 + Math.random() * 10).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}