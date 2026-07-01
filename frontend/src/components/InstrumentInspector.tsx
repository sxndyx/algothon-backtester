import type { BacktestResults } from "../data/mockResults";
import { formatNumber } from "../lib/formatters";
import { LineChart } from "./Charts";

type InstrumentInspectorProps = {
  results: BacktestResults;
  selectedInstrument: number;
  onSelectedInstrumentChange: (instrument: number) => void;
};

export function InstrumentInspector({
  results,
  selectedInstrument,
  onSelectedInstrumentChange,
}: InstrumentInspectorProps) {
  const positions = results.positions.map((dayPositions, index) => ({
    day: index + 1,
    value: dayPositions[selectedInstrument] ?? 0,
  }));
  const trades = results.trades.map((dayTrades) => dayTrades[selectedInstrument] ?? 0);
  const tradeCount = trades.filter((trade) => trade !== 0).length;
  const netPosition = positions[positions.length - 1]?.value ?? 0;
  const maxAbsPosition = Math.max(...positions.map((point) => Math.abs(point.value)));

  return (
    <section className="inspector-panel">
      <div className="inspector-header">
        <div>
          <p className="section-kicker">Instrument Inspector</p>
          <h2>Instrument {selectedInstrument}</h2>
        </div>
        <label className="instrument-select">
          <span>Instrument</span>
          <select
            value={selectedInstrument}
            onChange={(event) => onSelectedInstrumentChange(Number(event.target.value))}
          >
            {Array.from({ length: results.metadata.n_instruments }, (_, index) => (
              <option value={index} key={index}>
                {index}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="inspector-grid">
        <LineChart
          data={positions}
          title="Position Over Time"
          tone="amber"
          formatValue={(value) => formatNumber(value)}
        />
        <div className="instrument-stats">
          <article>
            <span>Current Position</span>
            <strong>{formatNumber(netPosition)}</strong>
          </article>
          <article>
            <span>Trade Days</span>
            <strong>{formatNumber(tradeCount)}</strong>
          </article>
          <article>
            <span>Max Abs Position</span>
            <strong>{formatNumber(maxAbsPosition)}</strong>
          </article>
          <article>
            <span>Position Limit</span>
            <strong>${formatNumber(results.metadata.position_limit_dollars)}</strong>
          </article>
        </div>
      </div>
    </section>
  );
}
