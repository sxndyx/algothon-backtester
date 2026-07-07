# Algothon Backtester

This repository contains a deterministic backtester and visualiser data engine
for the UNSW x Susquehanna International Group Algothon.

It runs competitor strategies over the provided official price dataset. It does
not simulate, bootstrap, Monte Carlo sample, randomise, or substitute market
data. Backtest runs export structured JSON for a future frontend visualiser, and
the repository includes a lightweight quick-look plotting script for local
review.

## Current Status

| Component | Status | Notes |
| --- | --- | --- |
| Deterministic backtester engine | Implemented | Runs strategies day by day over the provided price matrix. |
| Visualiser data output | Implemented | Outputs structured JSON with summary, series, matrices, trade logs, instrument summaries, warnings, and clipping events. |
| Quick-look plots | Implemented | `scripts/plot_results.py` saves PNG charts from a results JSON file. |
| Final web frontend | Not implemented | No frontend application is present in this repository yet. |

## Repository Structure

```text
.
├── data/
│   └── prices.txt
├── docs/
│   ├── backtest_rules.md
│   ├── results_schema.md
│   └── visualiser_contract.md
├── engine/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── simulator.py
│   └── strategy_loader.py
├── examples/
│   ├── broken_strategy.py
│   ├── momentum_strategy.py
│   ├── sample_results.json
│   └── zero_strategy.py
├── scripts/
│   ├── plot_results.py
│   └── run_backtest.py
├── README.md
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Price Data Format

Price data is loaded as a numeric text matrix:

- Rows are instruments.
- Columns are days.
- Values are accessed as `prices[instrument, day]`.
- The expected shape is `(n_instruments, n_days)`.

The current sample file, `data/prices.txt`, contains:

```text
100 101 102 103 104
50 51 50 52 53
200 198 199 201 202
```

This sample has 3 instruments and 5 days.

## Strategy Format

By default, a strategy file must define:

```python
def getMyPosition(prices):
    ...
```

The `prices` argument has shape `(n_instruments, days_so_far)` and contains
only the provided dataset up to and including the current day. The strategy
returns one target position per instrument.

Strategies should be deterministic for the same input price history. They
should not generate or depend on simulated, bootstrapped, Monte Carlo,
randomised, or fake market data.

## Running A Backtest

Standard run:

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
  --out window_results.json
```

Custom strategy function name:

```bash
PYTHONPATH=. python3 scripts/run_backtest.py \
  --strategy examples/momentum_strategy.py \
  --prices data/prices.txt \
  --function-name getMyPosition \
  --out examples/sample_results.json
```

## CLI Options

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--strategy` | Yes | None | Path to a Python strategy file. |
| `--prices` | Yes | None | Path to the official price dataset. |
| `--out` | No | `results.json` | Path where the results JSON will be written. |
| `--commission` | No | `0.001` | Commission rate charged on traded notional. |
| `--position-limit` | No | `10000.0` | Dollar position limit applied per instrument. |
| `--start-day` | No | `1` | First zero-based day index to run. Must be at least `1`. |
| `--end-day` | No | Last available day | Last zero-based day index to run, inclusive. |
| `--function-name` | No | `getMyPosition` | Strategy function name to load from the strategy file. |

## Backtest Logic

The engine follows a deterministic daily loop:

1. Each day passes `prices[:, : day + 1]` into the strategy.
2. The returned target positions are validated for shape and finite values.
3. Positions are clipped to the configured per-instrument dollar limit.
4. Trades are calculated as new position minus previous position.
5. Commission is charged on traded notional.
6. P&L is calculated from positions held over the price movement from the
   previous day to the current day.
7. Results are deterministic for the same strategy, configuration, and dataset.

## Output JSON

`scripts/run_backtest.py` writes a structured JSON object with these top-level
fields:

| Field | Description |
| --- | --- |
| `metadata` | Dataset dimensions, run window, cost settings, strategy function name, and determinism flags. |
| `summary` | Score, total P&L, gross P&L, drawdown, turnover, commission, and trade counts. |
| `daily_records` | One record per backtested day for replay and daily result tables. |
| `series` | Chart-ready arrays for days, P&L, drawdown, turnover, and commission. |
| `positions` | End-of-day position matrix by day and instrument. |
| `trades` | Signed trade matrix by day and instrument. |
| `trade_logs` | Readable one-row-per-trade records for tables and buy/sell markers. |
| `instrument_summary` | Per-instrument P&L, turnover, commission, position, and trade metrics. |
| `warnings` | Deterministic rule-based diagnostics for commission drag, turnover, clipping, volatility, and P&L concentration. |
| `clipping_events` | Days where requested positions were clipped by position limits. |

See `docs/results_schema.md` and `docs/visualiser_contract.md` for more detail.

## Quick-Look Plots

The quick-look plotting script reads a results JSON file and saves PNG charts:

```bash
PYTHONPATH=. python3 scripts/plot_results.py \
  --results examples/sample_results.json \
  --out-dir examples/plots
```

It writes:

- `cumulative_pnl.png`
- `daily_pnl.png`
- `drawdown.png`
- `turnover_commission.png`

This script is intended as a lightweight local visualiser bridge. It is not the
final web frontend.

## Examples

- `examples/zero_strategy.py`: returns zero positions for every instrument.
- `examples/momentum_strategy.py`: simple deterministic momentum example.
- `examples/broken_strategy.py`: intentionally returns the wrong number of
  positions to demonstrate validation errors.

## What This Project Does Not Do

- No live trading.
- No brokerage integration.
- No real-time market data.
- No strategy generation.
- No simulated, bootstrapped, or Monte Carlo market paths.
- No hosted execution of arbitrary uploaded Python code.
- No final polished web frontend yet.

## Next Steps

Likely future improvements include:

- Frontend dashboard for the JSON output.
- Position heatmap and trade matrix views.
- Instrument-level breakdown pages.
- Refinement of warning and diagnostic thresholds.
- Strategy comparison across multiple result files.
- Formal tests for P&L, commission, clipping, and no future leakage.
