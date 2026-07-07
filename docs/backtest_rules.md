# Backtest Rules

The Algothon backtester is deterministic and official-dataset-only. It never
creates simulated, bootstrapped, Monte Carlo, randomised, or fake market data.

## Input Data

- Price data is loaded from the provided text file.
- The price matrix must have shape `(n_instruments, n_days)`.
- Prices must be finite and strictly positive.
- The dataset must contain at least one instrument and at least two days.

## Daily Loop

- The first tradable day is day `1`; day `0` has no previous price for P&L.
- For each backtested day, the strategy receives `prices[:, :day + 1]`.
- `start_day` and `end_day` only select an inclusive day window from the
  provided dataset. They do not create or alter price data.
- When using a later `start_day`, positions start flat on that day while the
  strategy still receives all official history up to the current day.

## Strategy Output

- The strategy function defaults to `getMyPosition`.
- A different function can be selected with `--function-name`.
- The function must return one target position per instrument.
- Returned positions must be finite and have shape `(n_instruments,)`.

## Trading And Costs

- Position limits are applied per instrument using the current official price.
- Trades are calculated as clipped target position minus current position.
- Turnover is the sum of absolute traded notional.
- Commission is charged on traded notional.
- P&L comes from positions held through the current day's price movement, then
  commission is deducted.

## Determinism

For the same strategy file, function name, configuration, and official price
dataset, the engine returns the same result object.
