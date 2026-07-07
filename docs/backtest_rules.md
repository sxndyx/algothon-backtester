# Backtest Rules

The Algothon backtester is deterministic and official-dataset-only.

## Data

- The engine only uses the provided price dataset.
- It does not generate fake, simulated, bootstrapped, Monte Carlo, or randomised
  data.
- Price data is loaded as a matrix with shape `(n_instruments, n_days)`.

## Daily Loop

- The first tradable day is day `1`; day `0` has no previous price for P&L.
- Each day passes `prices[:, : day + 1]` into the strategy.
- `start_day` and `end_day` only select a window from the provided dataset.

## Positions, Trades, And Costs

- The strategy returns target positions for each instrument.
- Position limits are applied per instrument.
- Trades are target position minus previous position.
- Commission is charged on traded notional.
- P&L comes from previous positions over price movement, then commission is
  deducted.

## Determinism

Same strategy plus same data and same configuration produces the same result.
