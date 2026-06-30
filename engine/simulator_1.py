import numpy as np


def validate_positions(positions, n_instruments: int) -> np.ndarray:
    """
    Validate the output of getMyPosition().
    """
    positions = np.asarray(positions)

    if positions.shape != (n_instruments,):
        raise ValueError(
            f"Strategy returned shape {positions.shape}, "
            f"but expected ({n_instruments},)."
        )

    if np.any(~np.isfinite(positions)):
        raise ValueError("Strategy returned NaN or infinite positions.")

    return positions.astype(int)


def run_backtest(
    prices: np.ndarray,
    get_position_function,
    commission_rate: float = 0.001,
    position_limit_dollars: float = 10000.0,
) -> dict:
    """
    Run a deterministic backtest on the provided official price dataset.

    This does not generate simulated market data.
    It only walks through the given data day by day.
    """
    n_instruments, n_days = prices.shape

    current_positions = np.zeros(n_instruments, dtype=int)

    daily_pnl = []
    cumulative_pnl = []
    position_history = []
    trade_history = []
    daily_turnover = []
    daily_commission = []

    running_pnl = 0.0

    for day in range(1, n_days):
        prices_so_far = prices[:, : day + 1]

        previous_prices = prices[:, day - 1]
        current_prices = prices[:, day]

        desired_positions = get_position_function(prices_so_far)
        desired_positions = validate_positions(desired_positions, n_instruments)

        # Apply dollar position limit per instrument
        max_shares = np.floor(position_limit_dollars / current_prices).astype(int)
        clipped_positions = np.clip(desired_positions, -max_shares, max_shares)

        trades = clipped_positions - current_positions

        turnover = float(np.sum(np.abs(trades * current_prices)))
        commission = float(turnover * commission_rate)

        # P&L from holding yesterday's positions through today's price movement
        holding_pnl = float(np.sum(current_positions * (current_prices - previous_prices)))

        net_pnl = holding_pnl - commission
        running_pnl += net_pnl

        daily_pnl.append(net_pnl)
        cumulative_pnl.append(running_pnl)
        position_history.append(clipped_positions.tolist())
        trade_history.append(trades.tolist())
        daily_turnover.append(turnover)
        daily_commission.append(commission)

        current_positions = clipped_positions

    mean_daily_pnl = float(np.mean(daily_pnl)) if daily_pnl else 0.0
    std_daily_pnl = float(np.std(daily_pnl)) if daily_pnl else 0.0

    score = mean_daily_pnl - 0.1 * std_daily_pnl

    return {
        "n_instruments": int(n_instruments),
        "n_days": int(n_days),
        "score": float(score),
        "total_pnl": float(running_pnl),
        "mean_daily_pnl": mean_daily_pnl,
        "std_daily_pnl": std_daily_pnl,
        "total_commission": float(np.sum(daily_commission)),
        "total_turnover": float(np.sum(daily_turnover)),
        "daily_pnl": daily_pnl,
        "cumulative_pnl": cumulative_pnl,
        "daily_turnover": daily_turnover,
        "daily_commission": daily_commission,
        "positions": position_history,
        "trades": trade_history,
    }