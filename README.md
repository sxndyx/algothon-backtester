# algothon-backtester

Deterministic backtester and visualiser data engine for the UNSW x Susquehanna
International Group Algothon.

The engine only walks through the provided official price dataset. It does not
simulate, bootstrap, randomise, or substitute market data.

## Setup

Create a Python environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run A Backtest

```bash
PYTHONPATH=. python3 scripts/run_backtest.py \
  --strategy examples/momentum_strategy.py \
  --prices data/prices.txt \
  --out examples/sample_results.json
```

Optional controls:

- `--commission`: commission rate, where `0.001` is 10 bps.
- `--position-limit`: dollar position limit per instrument.
- `--start-day`: first zero-based day index to run. It must be at least `1`
  because day `0` has no previous price for P&L.
- `--end-day`: last zero-based day index to run, inclusive.

When a later `--start-day` is used, the strategy still receives official price
history up to the current day, but portfolio positions start flat at the first
backtested day.

## Strategy Format

A strategy file must define:

```python
def getMyPosition(prices):
    ...
```

`prices` is a NumPy array with shape `(n_instruments, days_so_far)` containing
official prices up to and including the current day. The strategy must return a
one-dimensional target position array with one integer-compatible value per
instrument.

Strategies should be deterministic for the same input price history. They must
not generate or depend on simulated, bootstrapped, randomised, or fake market
data.

## Output

The CLI writes a JSON result object for the visualiser. It includes:

- `metadata`: dataset size, run window, cost settings, and determinism flags.
- `summary`: score, P&L, drawdown, turnover, commission, and trade counts.
- `daily_records`: one object per backtested day.
- `series`: arrays for charting P&L, drawdown, turnover, and commission.
- `positions`: matrix of end-of-day positions by day and instrument.
- `trades`: matrix of signed share trades by day and instrument.
- `trade_logs`: readable one-row-per-trade records for tables.
- `clipping_events`: days where position limits clipped requested positions.

See `docs/results_schema.md` for the official visualiser schema.
