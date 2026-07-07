from numbers import Integral
from typing import Optional

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


def validate_day_window(
    n_days: int,
    start_day: Optional[int],
    end_day: Optional[int],
) -> tuple[int, int]:
    """
    Validate and normalize the inclusive day window used for the backtest.
    """
    if n_days < 2:
        raise ValueError("Backtest requires at least two days of price data.")

    if start_day is None:
        start_day = 1

    if end_day is None:
        end_day = n_days - 1

    if isinstance(start_day, bool) or not isinstance(start_day, Integral):
        raise TypeError("start_day must be an integer day index.")

    if isinstance(end_day, bool) or not isinstance(end_day, Integral):
        raise TypeError("end_day must be an integer day index.")

    start_day = int(start_day)
    end_day = int(end_day)

    if start_day < 1:
        raise ValueError(
            "start_day must be at least 1 because day 0 has no previous price."
        )

    if end_day >= n_days:
        raise ValueError(
            f"end_day must be less than the number of days ({n_days}); "
            f"got {end_day}."
        )

    if end_day < start_day:
        raise ValueError(
            f"end_day ({end_day}) must be greater than or equal to "
            f"start_day ({start_day})."
        )

    return start_day, end_day


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


def build_trade_log_entries(
    day: int,
    trades: np.ndarray,
    current_prices: np.ndarray,
    clipped_positions: np.ndarray,
) -> list[dict]:
    """
    Return one readable log entry for each non-zero trade.
    """
    entries = []

    for instrument, signed_shares in enumerate(trades):
        signed_shares = int(signed_shares)

        if signed_shares == 0:
            continue

        price = float(current_prices[instrument])
        notional = float(abs(signed_shares) * price)

        entries.append(
            {
                "day": int(day),
                "instrument": int(instrument),
                "side": "buy" if signed_shares > 0 else "sell",
                "shares": abs(signed_shares),
                "signed_shares": signed_shares,
                "price": price,
                "notional": notional,
                "position_after": int(clipped_positions[instrument]),
            }
        )

    return entries


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
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
) -> dict:
    """
    Backtest on provided data only
    No new price data is generated, Same strategy with same historical data
    """
    n_instruments, n_days = prices.shape
    start_day, end_day = validate_day_window(n_days, start_day, end_day)

    current_positions = np.zeros(n_instruments, dtype=int)

    daily_records = []
    daily_pnl = []
    cumulative_pnl = []
    position_history = []
    trade_history = []
    daily_turnover = []
    daily_commission = []
    trade_logs = []
    clipping_events = []

    running_pnl = 0.0

    for day in range(start_day, end_day + 1):
        prices_so_far = prices[:, : day + 1]

        previous_prices = prices[:, day - 1]
        current_prices = prices[:, day]

        try:
            desired_positions = get_position_function(prices_so_far)
        except Exception as exc:
            raise RuntimeError(
                f"Strategy getMyPosition() crashed on day {day}: {exc}"
            ) from exc

        try:
            desired_positions = validate_positions(desired_positions, n_instruments)
        except ValueError as exc:
            raise ValueError(
                f"Strategy getMyPosition() returned invalid positions on day "
                f"{day}: {exc}"
            ) from exc

        clipped_positions, num_clipped = clip_positions_to_limit(
            desired_positions=desired_positions,
            current_prices=current_prices,
            position_limit_dollars=position_limit_dollars,
        )

        trades = clipped_positions - current_positions

        trade_values = trades * current_prices
        turnover = float(np.sum(np.abs(trade_values)))
        commission = float(turnover * commission_rate)
        day_trade_logs = build_trade_log_entries(
            day=day,
            trades=trades,
            current_prices=current_prices,
            clipped_positions=clipped_positions,
        )

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
        trade_logs.extend(day_trade_logs)

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
                "num_traded_instruments": len(day_trade_logs),
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
            "start_day": int(start_day),
            "end_day": int(end_day),
            "run_days": int(end_day - start_day + 1),
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
            "total_trades": len(trade_logs),
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
        "trade_logs": trade_logs,
        "clipping_events": clipping_events,
    }
