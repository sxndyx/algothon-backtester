# Results Schema

This is the official JSON result object produced by
`scripts/run_backtest.py` for the Algothon visualiser.

The object is deterministic for the same strategy and official price dataset.
The engine does not generate simulated, bootstrapped, Monte Carlo, randomised,
or fake market data.

## Top-Level Object

```text
{
  "metadata": object,
  "config": object,
  "summary": object,
  "daily_records": array<object>,
  "series": object,
  "positions": array<array<int>>,
  "trades": array<array<int>>,
  "trade_logs": array<object>,
  "instrument_summary": array<object>,
  "warnings": array<object>,
  "clipping_events": array<object>
}
```

## metadata

- `schema_version` (`string`): result schema version.
- `engine` (`string`): engine identifier.
- `n_instruments` (`int`): number of instruments in the loaded price matrix.
- `n_days` (`int`): number of days in the loaded price matrix.
- `start_day` (`int`): first zero-based day index included in the run.
- `end_day` (`int`): final zero-based day index included in the run.
- `run_days` (`int`): number of backtested days.
- `deterministic` (`bool`): always `true` for official engine output.
- `uses_simulated_price_data` (`bool`): always `false`.

For partial windows, portfolio positions start flat on `start_day`; the
strategy still receives official price history up to each current day.

## config

- `commission_rate` (`float`): commission rate applied to traded notional.
- `position_limit_dollars` (`float`): per-instrument dollar exposure limit.
- `strategy_function_name` (`string`): strategy function loaded from the file.

## summary

- `score` (`float`): mean daily P&L minus `0.1` times daily P&L standard
  deviation.
- `total_pnl` (`float`): cumulative net P&L over the run window.
- `total_gross_pnl` (`float`): cumulative P&L before commission.
- `mean_daily_pnl` (`float`): mean of daily net P&L.
- `std_daily_pnl` (`float`): standard deviation of daily net P&L.
- `max_drawdown` (`float`): worst drawdown from the cumulative P&L peak.
- `total_commission` (`float`): sum of daily commissions.
- `total_turnover` (`float`): sum of absolute traded notional.
- `total_trades` (`int`): number of non-zero instrument trades.
- `clipping_event_count` (`int`): number of days with at least one clipped
  requested position.
- `winning_days` (`int`): count of days with positive net P&L.
- `losing_days` (`int`): count of days with negative net P&L.

## daily_records

One object per backtested day, ordered by day:

- `day` (`int`): zero-based day index in the official price matrix.
- `gross_pnl` (`float`): P&L before commission.
- `net_pnl` (`float`): P&L after commission.
- `cumulative_pnl` (`float`): cumulative net P&L through the day.
- `turnover` (`float`): absolute traded notional for the day.
- `commission` (`float`): commission charged for the day.
- `num_traded_instruments` (`int`): count of non-zero instrument trades.
- `num_clipped_instruments` (`int`): count of requested positions clipped by
  the position limit.
- `gross_exposure` (`float`): sum of absolute end-of-day instrument exposure.
- `net_exposure` (`float`): signed end-of-day exposure across instruments.

## series

Arrays aligned one-to-one with `daily_records`:

- `days` (`array<int>`)
- `daily_pnl` (`array<float>`)
- `gross_daily_pnl` (`array<float>`)
- `cumulative_pnl` (`array<float>`)
- `drawdown` (`array<float>`)
- `daily_turnover` (`array<float>`)
- `daily_commission` (`array<float>`)

## positions

Matrix of end-of-day positions. Rows align with `daily_records`; columns align
with instrument index.

## trades

Matrix of signed share trades. Rows align with `daily_records`; columns align
with instrument index. Positive values are buys, negative values are sells, and
zero means no trade for that instrument on that day.

## trade_logs

Readable one-row-per-trade records. Zero trades are omitted.

- `day` (`int`): zero-based day index in the official price matrix.
- `instrument` (`int`): zero-based instrument index.
- `side` (`string`): `BUY` or `SELL`.
- `previous_position` (`int`): position before the trade.
- `new_position` (`int`): position after the trade.
- `trade_quantity` (`int`): absolute share count traded.
- `price` (`float`): official price used for the trade.
- `trade_value` (`float`): absolute traded notional.
- `commission` (`float`): commission charged for the trade.

## instrument_summary

One object per instrument:

- `instrument` (`int`): zero-based instrument index.
- `total_pnl` (`float`): net P&L attributed to the instrument.
- `total_trades` (`int`): number of non-zero trades for the instrument.
- `total_turnover` (`float`): absolute traded notional for the instrument.
- `total_commission` (`float`): total commission charged for the instrument.
- `average_position` (`float`): average end-of-day position during the run.
- `max_abs_position` (`int`): maximum absolute end-of-day position.
- `best_day_pnl` (`float`): best daily net P&L for the instrument.
- `worst_day_pnl` (`float`): worst daily net P&L for the instrument.

## warnings

Deterministic rule-based diagnostics. Each object contains:

- `code` (`string`): stable warning code.
- `severity` (`string`): currently `warning`.
- `message` (`string`): human-readable explanation.
- `metric` (`string`): metric used by the rule.
- `value` (`float`): observed metric value.
- `threshold` (`float`): threshold that triggered the warning.

Current warning codes:

- `HIGH_COMMISSION_DRAG`
- `HIGH_TURNOVER`
- `FREQUENT_POSITION_CLIPPING`
- `HIGH_PNL_VOLATILITY`
- `HEAVY_INSTRUMENT_CONCENTRATION`

## clipping_events

One object per day where at least one requested position exceeded the dollar
position limit:

- `day` (`int`): zero-based day index.
- `num_clipped_instruments` (`int`): number of instruments clipped that day.
- `instruments` (`array<int>`): zero-based instrument indexes clipped that day.
