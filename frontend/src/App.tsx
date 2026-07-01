import { useMemo, useState } from "react";
import "./App.css";
import { BarChart, DualLineChart, LineChart } from "./components/Charts";
import { InstrumentInspector } from "./components/InstrumentInspector";
import { SummaryCards } from "./components/SummaryCards";
import { mockResults } from "./data/mockResults";
import { formatCompactCurrency, formatCurrency } from "./lib/formatters";

function App() {
  const [selectedInstrument, setSelectedInstrument] = useState(0);
  const results = mockResults;

  const dailyPnl = useMemo(
    () =>
      results.series.daily_pnl.map((value, index) => ({
        day: index + 1,
        value,
      })),
    [results.series.daily_pnl],
  );

  const cumulativePnl = useMemo(
    () =>
      results.series.cumulative_pnl.map((value, index) => ({
        day: index + 1,
        value,
      })),
    [results.series.cumulative_pnl],
  );

  const drawdown = useMemo(
    () =>
      results.series.drawdown.map((value, index) => ({
        day: index + 1,
        value,
      })),
    [results.series.drawdown],
  );

  const turnoverCommission = useMemo(
    () =>
      results.series.daily_turnover.map((turnover, index) => ({
        day: index + 1,
        primary: turnover,
        secondary: results.series.daily_commission[index] ?? 0,
      })),
    [results.series.daily_commission, results.series.daily_turnover],
  );

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="section-kicker">UNSW FinTechSoc x SIG</p>
          <h1>Algothon Backtester</h1>
        </div>
        <div className="run-meta">
          <span>{results.metadata.n_instruments} instruments</span>
          <span>{results.metadata.n_days} days</span>
          <span>{results.summary.total_trades} trade events</span>
        </div>
      </header>

      <SummaryCards results={results} />

      <section className="chart-grid" aria-label="Backtest charts">
        <LineChart
          data={cumulativePnl}
          title="Cumulative P&L"
          tone="blue"
          formatValue={formatCurrency}
        />
        <BarChart data={dailyPnl} title="Daily P&L" formatValue={formatCurrency} />
        <LineChart
          data={drawdown}
          title="Drawdown"
          tone="red"
          formatValue={formatCurrency}
        />
        <DualLineChart
          data={turnoverCommission}
          title="Turnover and Commission"
          primaryLabel="Turnover"
          secondaryLabel="Commission"
          formatValue={formatCompactCurrency}
        />
      </section>

      <InstrumentInspector
        results={results}
        selectedInstrument={selectedInstrument}
        onSelectedInstrumentChange={setSelectedInstrument}
      />
    </main>
  );
}

export default App;
