import type { BacktestResults } from "../data/mockResults";
import {
  formatBasisPoints,
  formatCompactCurrency,
  formatCurrency,
  formatNumber,
} from "../lib/formatters";

type SummaryCardsProps = {
  results: BacktestResults;
};

export function SummaryCards({ results }: SummaryCardsProps) {
  const { metadata, summary } = results;
  const cards = [
    {
      label: "Score",
      value: formatNumber(summary.score),
      accent: "blue",
    },
    {
      label: "Total P&L",
      value: formatCurrency(summary.total_pnl),
      accent: summary.total_pnl >= 0 ? "green" : "red",
    },
    {
      label: "Mean Daily P&L",
      value: formatCurrency(summary.mean_daily_pnl),
      accent: "green",
    },
    {
      label: "Volatility",
      value: formatCurrency(summary.std_daily_pnl),
      accent: "amber",
    },
    {
      label: "Max Drawdown",
      value: formatCurrency(summary.max_drawdown),
      accent: "red",
    },
    {
      label: "Turnover",
      value: formatCompactCurrency(summary.total_turnover),
      accent: "purple",
    },
    {
      label: "Commission",
      value: formatCurrency(summary.total_commission),
      accent: "orange",
    },
    {
      label: "Commission Rate",
      value: formatBasisPoints(metadata.commission_rate),
      accent: "slate",
    },
  ];

  return (
    <section className="summary-grid" aria-label="Backtest summary">
      {cards.map((card) => (
        <article className={`summary-card summary-card-${card.accent}`} key={card.label}>
          <span>{card.label}</span>
          <strong>{card.value}</strong>
        </article>
      ))}
    </section>
  );
}
