import numpy as np


def validate_positions(positions, n_instruments: int) -> np.ndarray:
    """
    Validate the output of getMyPosition()
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


def clip_positions_to_limit(
    desired_positions: np.ndarray,
    current_prices: np.ndarray,
    position_limit_dollars: float,
) -> tuple[np.ndarray, int]:
    """
    Clip positions so no instrument exceeds the dollar position limit
    """
    max_shares = np.floor(position_limit_dollars / current_prices).astype(int)

    clipped_positions = np.clip(
        desired_positions,
        -max_shares,
        max_shares,
    )

    num_clipped = int(np.sum(clipped_positions != desired_positions))

    return clipped_positions.astype(int), num_clipped


def calculate_drawdown(cumulative_pnl: list[float]) -> list[float]:
    """
    Drawdown is the fall from the previous cumulative P&L peak
    """
    drawdowns = []
    peak = float("-inf")

    for value in cumulative_pnl:
        peak = max(peak, value)
        drawdowns.append(value - peak)

    return drawdowns


def run_backtest(
    prices: np.ndarray,
    get_position_function,
    commission_rate: float = 0.001,
    position_limit_dollars: float = 10000.0,
) -> dict:
    """
    Backtest on provided data only
    No new price data is generated, Same strategy with same historical data
    """
    n_instruments, n_days = prices.shape

    current_positions = np.zeros(n_instruments, dtype=int)

    daily_records = []
    daily_pnl = []
    cumulative_pnl = []
    position_history = []
    trade_history = []
    daily_turnover = []
    daily_commission = []
    clipping_events = []

    running_pnl = 0.0

    for day in range(1, n_days):
        prices_so_far = prices[:, : day + 1]

        previous_prices = prices[:, day - 1]
        current_prices = prices[:, day]

        desired_positions = get_position_function(prices_so_far)
        desired_positions = validate_positions(desired_positions, n_instruments)

        clipped_positions, num_clipped = clip_positions_to_limit(
            desired_positions=desired_positions,
            current_prices=current_prices,
            position_limit_dollars=position_limit_dollars,
        )

        trades = clipped_positions - current_positions

        trade_values = trades * current_prices
        turnover = float(np.sum(np.abs(trade_values)))
        commission = float(turnover * commission_rate)

        price_changes = current_prices - previous_prices

        # P&L comes from yesterday's held positions through price move
        gross_pnl = float(np.sum(current_positions * price_changes))
        net_pnl = gross_pnl - commission

        running_pnl += net_pnl

        daily_pnl.append(net_pnl)
        cumulative_pnl.append(running_pnl)
        position_history.append(clipped_positions.tolist())
        trade_history.append(trades.tolist())
        daily_turnover.append(turnover)
        daily_commission.append(commission)

        if num_clipped > 0:
            clipping_events.append(
                {
                    "day": day,
                    "num_clipped_instruments": num_clipped,
                }
            )

        daily_records.append(
            {
                "day": day,
                "gross_pnl": gross_pnl,
                "net_pnl": net_pnl,
                "cumulative_pnl": running_pnl,
                "turnover": turnover,
                "commission": commission,
                "num_traded_instruments": int(np.sum(trades != 0)),
                "num_clipped_instruments": num_clipped,
            }
        )

        current_positions = clipped_positions

    drawdown = calculate_drawdown(cumulative_pnl)

    mean_daily_pnl = float(np.mean(daily_pnl)) if daily_pnl else 0.0
    std_daily_pnl = float(np.std(daily_pnl)) if daily_pnl else 0.0
    score = mean_daily_pnl - 0.1 * std_daily_pnl
    max_drawdown = float(min(drawdown)) if drawdown else 0.0

    return {
        "metadata": {
            "n_instruments": int(n_instruments),
            "n_days": int(n_days),
            "commission_rate": commission_rate,
            "position_limit_dollars": position_limit_dollars,
            "deterministic": True,
            "uses_simulated_price_data": False,
        },
        "summary": {
            "score": float(score),
            "total_pnl": float(running_pnl),
            "mean_daily_pnl": mean_daily_pnl,
            "std_daily_pnl": std_daily_pnl,
            "max_drawdown": max_drawdown,
            "total_commission": float(np.sum(daily_commission)),
            "total_turnover": float(np.sum(daily_turnover)),
            "total_trades": int(
                np.sum([np.sum(np.array(trades) != 0) for trades in trade_history])
            ),
            "clipping_event_count": len(clipping_events),
        },
        "daily_records": daily_records,
        "series": {
            "daily_pnl": daily_pnl,
            "cumulative_pnl": cumulative_pnl,
            "drawdown": drawdown,
            "daily_turnover": daily_turnover,
            "daily_commission": daily_commission,
        },
        "positions": position_history,
        "trades": trade_history,
        "clipping_events": clipping_events,
    }