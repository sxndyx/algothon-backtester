# Visualiser Contract

Frontend views should consume the JSON produced by `scripts/run_backtest.py`.
The visualiser should not recalculate trades, P&L, commissions, or diagnostics
from raw prices unless it is explicitly validating the engine.

## Cards

Use `summary` for headline cards:

- Score: `summary.score`
- Total P&L: `summary.total_pnl`
- Max drawdown: `summary.max_drawdown`
- Total turnover: `summary.total_turnover`
- Total commission: `summary.total_commission`
- Total trades: `summary.total_trades`

Use `metadata` and `config` for context cards:

- Dataset dimensions: `metadata.n_instruments`, `metadata.n_days`
- Run window: `metadata.start_day`, `metadata.end_day`
- Commission rate: `config.commission_rate`
- Position limit: `config.position_limit_dollars`
- Strategy function: `config.strategy_function_name`

## Charts

Use `series.days` for the x-axis. Series arrays are aligned by index.

- Cumulative P&L chart: `series.cumulative_pnl`
- Daily P&L bars: `series.daily_pnl`
- Drawdown chart: `series.drawdown`
- Turnover chart: `series.daily_turnover`
- Commission chart: `series.daily_commission`

## Tables

- Daily table: `daily_records`
- Trade blotter: `trade_logs`
- Instrument table: `instrument_summary`
- Warning panel: `warnings`
- Clipping table: `clipping_events`

## Heatmaps

Use matrices directly:

- Position heatmap: `positions`
- Trade heatmap: `trades`

Rows align with `daily_records` and `series.days`. Columns align with
zero-based instrument indexes.

## Trade Markers

Use `trade_logs` for chart markers and table rows. Each row has the day,
instrument, side, previous position, new position, quantity, price, notional,
and commission for one non-zero trade.

## Warnings

Render `warnings` as deterministic diagnostics. Warning codes are stable enough
for icons, filters, and documentation links, while `message` is suitable for
display text.
