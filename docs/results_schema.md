# Results Schema

This is the official JSON result object produced by
`scripts/run_backtest.py` for the Algothon visualiser.

The object is deterministic for the same strategy and official price dataset.
The engine does not generate simulated, bootstrapped, randomised, or fake market
data.

## Top-Level Object

```text
{
  "metadata": object,
  "summary": object,
  "daily_records": array<object>,
  "series": object,
  "positions": array<array<int>>,
  "trades": array<array<int>>,
  "trade_logs": array<object>,
  "clipping_events": array<object>
}
```

## metadata

- `n_instruments` (`int`): number of instruments in the loaded price matrix.
- `n_days` (`int`): number of days in the loaded price matrix.
- `start_day` (`int`): first zero-based day index included in the run.
- `end_day` (`int`): final zero-based day index included in the run.
- `run_days` (`int`): number of backtested days.
- `commission_rate` (`float`): commission rate applied to traded notional.
- `position_limit_dollars` (`float`): per-instrument dollar exposure limit.
- `deterministic` (`bool`): always `true` for official engine output.
- `uses_simulated_price_data` (`bool`): always `false`.

For partial windows, portfolio positions start flat on `start_day`; the
strategy still receives official price history up to each current day.

## summary

- `score` (`float`): engine score, currently mean daily P&L minus `0.1`
  times daily P&L standard deviation.
- `total_pnl` (`float`): cumulative net P&L over the run window.
- `mean_daily_pnl` (`float`): mean of daily net P&L.
- `std_daily_pnl` (`float`): standard deviation of daily net P&L.
- `max_drawdown` (`float`): worst drawdown from the cumulative P&L peak.
- `total_commission` (`float`): sum of daily commissions.
- `total_turnover` (`float`): sum of absolute traded notional.
- `total_trades` (`int`): number of non-zero instrument trades.
- `clipping_event_count` (`int`): number of days with at least one clipped
  requested position.

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

## series

Arrays aligned one-to-one with `daily_records`:

- `daily_pnl` (`array<float>`)
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
- `side` (`string`): `buy` or `sell`.
- `shares` (`int`): absolute share count traded.
- `signed_shares` (`int`): signed share count, matching the `trades` matrix.
- `price` (`float`): official price used for the trade.
- `notional` (`float`): absolute traded notional.
- `position_after` (`int`): end-of-day position after the trade.

## clipping_events

One object per day where at least one requested position exceeded the dollar
position limit:

- `day` (`int`): zero-based day index.
- `num_clipped_instruments` (`int`): number of instruments clipped that day.
