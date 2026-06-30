import argparse
import json
from pathlib import Path

from engine.data_loader import load_prices
from engine.strategy_loader import load_strategy
from engine.simulator import run_backtest


def main():
    parser = argparse.ArgumentParser(description="Run Algothon deterministic backtest.")

    parser.add_argument(
        "--strategy",
        required=True,
        help="Path to strategy file containing getMyPosition(prices).",
    )

    parser.add_argument(
        "--prices",
        required=True,
        help="Path to official price dataset.",
    )

    parser.add_argument(
        "--out",
        default="results.json",
        help="Output path for results JSON.",
    )

    parser.add_argument(
        "--commission",
        type=float,
        default=0.001,
        help="Commission rate. Example: 0.001 = 10 bps.",
    )

    parser.add_argument(
        "--position-limit",
        type=float,
        default=10000.0,
        help="Dollar position limit per instrument.",
    )

    args = parser.parse_args()

    prices = load_prices(args.prices)
    strategy = load_strategy(args.strategy)

    results = run_backtest(
        prices=prices,
        get_position_function=strategy,
        commission_rate=args.commission,
        position_limit_dollars=args.position_limit,
    )

    output_path = Path(args.out)
    output_path.write_text(json.dumps(results, indent=2))

    print("Backtest complete.")
    print(f"Score: {results['summary']['score']:.4f}")
    print(f"Total P&L: {results['summary']['total_pnl']:.2f}")
    print(f"Max drawdown: {results['summary']['max_drawdown']:.2f}")
    print(f"Total commission: {results['summary']['total_commission']:.2f}")
    print(f"Total turnover: {results['summary']['total_turnover']:.2f}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()