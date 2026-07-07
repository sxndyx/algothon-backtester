# algothon-backtester

Deterministic backtester and visualiser data engine for the UNSW x Susquehanna
International Group Algothon.

The engine only walks through the provided official price dataset. It does not
simulate, bootstrap, Monte Carlo sample, randomise, or substitute market data.

## Setup

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

Windowed run:

```bash
PYTHONPATH=. python3 scripts/run_backtest.py \
  --strategy examples/momentum_strategy.py \
  --prices data/prices.txt \
  --start-day 1 \
  --end-day 3 \
  --function-name getMyPosition \
  --out window_results.json
```

## CLI Options

- `--strategy`: path to a Python strategy file.
- `--prices`: path to the official price dataset.
- `--out`: output path for the results JSON.
- `--commission`: commission rate, where `0.001` is 10 bps.
- `--position-limit`: dollar position limit per instrument.
- `--start-day`: first zero-based day index to run. Must be at least `1`.
- `--end-day`: last zero-based day index to run, inclusive.
- `--function-name`: strategy function to load. Defaults to `getMyPosition`.

## Strategy Format

A strategy file must define the configured strategy function:

```python
def getMyPosition(prices):
    ...
```

`prices` is a NumPy array with shape `(n_instruments, days_so_far)` containing
provided prices up to and including the current day. The strategy must return a
one-dimensional target position array with one integer-compatible value per
instrument.

Strategies should be deterministic for the same input price history. They must
not generate or depend on simulated, bootstrapped, Monte Carlo, randomised, or
fake market data.

## Output

The CLI writes a stable JSON result object for the visualiser:

- `metadata`: dataset size, run window, cost settings, strategy function, and
  determinism flags.
- `summary`: score, P&L, drawdown, turnover, commission, and trade counts.
- `daily_records`: one object per backtested day.
- `series`: chart-ready arrays for P&L, drawdown, turnover, and commission.
- `positions`: matrix of end-of-day positions by day and instrument.
- `trades`: matrix of signed share trades by day and instrument.
- `trade_logs`: readable one-row-per-trade records for tables and markers.
- `instrument_summary`: per-instrument P&L, turnover, commission, and position
  metrics.
- `warnings`: deterministic rule-based diagnostics.
- `clipping_events`: days where position limits clipped requested positions.

See `docs/results_schema.md` and `docs/visualiser_contract.md` for details.

## Quick-Look Plots

Generate PNG charts from a results JSON:

```bash
PYTHONPATH=. python3 scripts/plot_results.py \
  --results examples/sample_results.json \
  --out-dir examples/plots
```

This writes:

- `cumulative_pnl.png`
- `daily_pnl.png`
- `drawdown.png`
- `turnover_commission.png`

The plot script is a lightweight visualiser bridge, not the final frontend.
