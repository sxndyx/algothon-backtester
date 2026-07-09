import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { BarChart, DualLineChart, LineChart } from "./components/Charts";
import { DailyRecordsTable } from "./components/DailyRecordsTable";
import { InstrumentInspector } from "./components/InstrumentInspector";
import { MatrixHeatmap } from "./components/MatrixHeatmap";
import { SummaryCards } from "./components/SummaryCards";
import { TradeLogTable } from "./components/TradeLogTable";
import { WarningsPanel } from "./components/WarningsPanel";
import { loadResults, type ResultsLoadResult } from "./data/loadResults";
import { formatCompactCurrency, formatCurrency } from "./lib/formatters";

function App() {
  const [selectedInstrument, setSelectedInstrument] = useState(0);
  const [loadState, setLoadState] = useState<ResultsLoadResult | null>(null);

  useEffect(() => {
    let isMounted = true;

    loadResults().then((result) => {
      if (isMounted) {
        setLoadState(result);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  const results = loadState?.results;

  const dailyPnl = useMemo(
    () =>
      results?.series.daily_pnl.map((value, index) => ({
        day: results.series.days[index] ?? index,
        value,
      })) ?? [],
    [results],
  );

  const cumulativePnl = useMemo(
    () =>
      results?.series.cumulative_pnl.map((value, index) => ({
        day: results.series.days[index] ?? index,
        value,
      })) ?? [],
    [results],
  );

  const drawdown = useMemo(
    () =>
      results?.series.drawdown.map((value, index) => ({
        day: results.series.days[index] ?? index,
        value,
      })) ?? [],
    [results],
  );

  const turnoverCommission = useMemo(
    () =>
      results?.series.daily_turnover.map((turnover, index) => ({
        day: results.series.days[index] ?? index,
        primary: turnover,
        secondary: results.series.daily_commission[index] ?? 0,
      })) ?? [],
    [results],
  );

  if (!results || !loadState) {
    return (
      <main className="app-shell">
        <section className="loading-panel">Loading backtest results...</section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="section-kicker">UNSW FinTechSoc x SIG</p>
          <h1>Algothon Backtester</h1>
        </div>
        <div className="run-meta">
          <span>{results.metadata.n_instruments} instruments</span>
          <span>
            Days {results.metadata.start_day}-{results.metadata.end_day}
          </span>
          <span>{results.summary.total_trades} trade events</span>
        </div>
      </header>

      <section className={`source-banner source-${loadState.source}`}>
        <strong>{loadState.source === "generated" ? "Live results" : "Mock fallback"}</strong>
        <span>{loadState.message}</span>
      </section>

      <SummaryCards results={results} />

      <section className="chart-grid" aria-label="Backtest charts">
        <LineChart
          data={cumulativePnl}
          title="Cumulative P&L"
          tone="blue"
          domain={{ includeZero: true }}
          showZeroLine
          formatValue={formatCurrency}
        />
        <BarChart
          data={dailyPnl}
          title="Daily P&L"
          domain={{ includeZero: true }}
          showZeroLine
          formatValue={formatCurrency}
        />
        <LineChart
          data={drawdown}
          title="Drawdown"
          tone="red"
          domain={{ fixedMax: 0 }}
          showZeroLine
          formatValue={formatCurrency}
        />
        <DualLineChart
          data={turnoverCommission}
          title="Turnover and Commission"
          primaryLabel="Turnover"
          secondaryLabel="Commission"
          domain={{ fixedMin: 0 }}
          showZeroLine
          formatValue={formatCompactCurrency}
        />
      </section>

      <WarningsPanel warnings={results.warnings} />

      <InstrumentInspector
        results={results}
        selectedInstrument={selectedInstrument}
        onSelectedInstrumentChange={setSelectedInstrument}
      />

      <section className="matrix-grid-panels">
        <MatrixHeatmap
          kicker="Exposure"
          title="Position Exposure"
          matrix={results.positions}
          days={results.series.days}
          negativeLabel="Short"
          positiveLabel="Long"
        />
        <MatrixHeatmap
          kicker="Execution"
          title="Trade Activity"
          matrix={results.trades}
          days={results.series.days}
          negativeLabel="Sell"
          positiveLabel="Buy"
        />
      </section>

      <DailyRecordsTable records={results.daily_records} />
      <TradeLogTable tradeLogs={results.trade_logs} />
    </main>
  );
}

export default App;
