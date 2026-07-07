from numbers import Integral
from typing import Optional

import numpy as np


def validate_positions(positions, n_instruments: int) -> np.ndarray:
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


def resolve_function_name(get_position_function, function_name: Optional[str]) -> str:
    if function_name:
        return function_name

    return getattr(get_position_function, "__name__", "getMyPosition")


def clip_positions_to_limit(
    desired_positions: np.ndarray,
    current_prices: np.ndarray,
    position_limit_dollars: float,
) -> tuple[np.ndarray, int, np.ndarray]:
    max_shares = np.floor(position_limit_dollars / current_prices).astype(int)

    clipped_positions = np.clip(
        desired_positions,
        -max_shares,
        max_shares,
    ).astype(int)

    clipped_mask = clipped_positions != desired_positions
    num_clipped = int(np.sum(clipped_mask))

    return clipped_positions, num_clipped, clipped_mask


def build_trade_log_entries(
    day: int,
    trades: np.ndarray,
    current_prices: np.ndarray,
    previous_positions: np.ndarray,
    new_positions: np.ndarray,
    commission_rate: float,
) -> list[dict]:
    entries = []

    for instrument, signed_quantity in enumerate(trades):
        signed_quantity = int(signed_quantity)

        if signed_quantity == 0:
            continue

        price = float(current_prices[instrument])
        trade_value = float(abs(signed_quantity) * price)

        entries.append(
            {
                "day": int(day),
                "instrument": int(instrument),
                "side": "BUY" if signed_quantity > 0 else "SELL",
                "previous_position": int(previous_positions[instrument]),
                "new_position": int(new_positions[instrument]),
                "trade_quantity": abs(signed_quantity),
                "signed_quantity": signed_quantity,
                "price": price,
                "trade_value": trade_value,
                "commission": float(trade_value * commission_rate),
            }
        )

    return entries


def calculate_drawdown(cumulative_pnl: list[float]) -> list[float]:
    drawdowns = []
    peak = float("-inf")

    for value in cumulative_pnl:
        peak = max(peak, value)
        drawdowns.append(value - peak)

    return drawdowns


def build_instrument_summary(
    instrument_pnl: list[list[float]],
    instrument_turnover: list[list[float]],
    instrument_commission: list[list[float]],
    positions: list[list[int]],
    trades: list[list[int]],
) -> list[dict]:
    pnl_matrix = np.asarray(instrument_pnl, dtype=float)
    turnover_matrix = np.asarray(instrument_turnover, dtype=float)
    commission_matrix = np.asarray(instrument_commission, dtype=float)
    position_matrix = np.asarray(positions, dtype=int)
    trade_matrix = np.asarray(trades, dtype=int)

    n_instruments = position_matrix.shape[1] if position_matrix.size else 0
    instrument_summary = []

    for instrument in range(n_instruments):
        instrument_daily_pnl = pnl_matrix[:, instrument]
        instrument_positions = position_matrix[:, instrument]
        instrument_trades = trade_matrix[:, instrument]

        instrument_summary.append(
            {
                "instrument": int(instrument),
                "total_pnl": float(np.sum(instrument_daily_pnl)),
                "total_trades": int(np.count_nonzero(instrument_trades)),
                "total_turnover": float(np.sum(turnover_matrix[:, instrument])),
                "total_commission": float(np.sum(commission_matrix[:, instrument])),
                "average_position": float(np.mean(instrument_positions)),
                "max_abs_position": int(np.max(np.abs(instrument_positions))),
                "best_day_pnl": float(np.max(instrument_daily_pnl)),
                "worst_day_pnl": float(np.min(instrument_daily_pnl)),
            }
        )

    return instrument_summary


def build_warnings(
    summary: dict,
    instrument_summary: list[dict],
    daily_pnl: list[float],
    clipping_events: list[dict],
    run_days: int,
    n_instruments: int,
    position_limit_dollars: float,
) -> list[dict]:
    warnings = []
    total_commission = summary["total_commission"]
    total_gross_pnl = summary["total_gross_pnl"]
    total_turnover = summary["total_turnover"]

    commission_base = max(abs(total_gross_pnl), total_commission, 1.0)
    commission_drag = total_commission / commission_base
    if commission_drag >= 0.25:
        warnings.append(
            {
                "code": "HIGH_COMMISSION_DRAG",
                "severity": "warning",
                "message": "Commission is high relative to gross P&L.",
                "metric": "total_commission / max(abs(total_gross_pnl), total_commission, 1)",
                "value": float(commission_drag),
                "threshold": 0.25,
            }
        )

    daily_capacity = max(position_limit_dollars * n_instruments, 1.0)
    average_daily_turnover = total_turnover / max(run_days, 1)
    turnover_ratio = average_daily_turnover / daily_capacity
    if turnover_ratio >= 0.5:
        warnings.append(
            {
                "code": "HIGH_TURNOVER",
                "severity": "warning",
                "message": "Average daily turnover is high relative to available exposure.",
                "metric": "average_daily_turnover / (position_limit_dollars * n_instruments)",
                "value": float(turnover_ratio),
                "threshold": 0.5,
            }
        )

    clipping_rate = len(clipping_events) / max(run_days, 1)
    if clipping_rate >= 0.25:
        warnings.append(
            {
                "code": "FREQUENT_CLIPPING",
                "severity": "warning",
                "message": "Requested positions are frequently clipped by limits.",
                "metric": "clipping_event_days / run_days",
                "value": float(clipping_rate),
                "threshold": 0.25,
            }
        )

    mean_daily_pnl = summary["mean_daily_pnl"]
    std_daily_pnl = summary["std_daily_pnl"]
    volatility_ratio = std_daily_pnl / max(abs(mean_daily_pnl), 1.0)
    if len(daily_pnl) > 1 and volatility_ratio >= 2.0:
        warnings.append(
            {
                "code": "HIGH_DAILY_PNL_VOLATILITY",
                "severity": "warning",
                "message": "Daily P&L volatility is high relative to average daily P&L.",
                "metric": "std_daily_pnl / max(abs(mean_daily_pnl), 1)",
                "value": float(volatility_ratio),
                "threshold": 2.0,
            }
        )

    pnl_denominator = sum(abs(item["total_pnl"]) for item in instrument_summary)
    if pnl_denominator > 0:
        max_pnl_share = max(
            abs(item["total_pnl"]) / pnl_denominator for item in instrument_summary
        )
        if max_pnl_share >= 0.6:
            warnings.append(
                {
                    "code": "PNL_CONCENTRATION",
                    "severity": "warning",
                    "message": "P&L is concentrated in a small number of instruments.",
                    "metric": "max_abs_instrument_pnl / sum_abs_instrument_pnl",
                    "value": float(max_pnl_share),
                    "threshold": 0.6,
                }
            )

    return warnings


def run_backtest(
    prices: np.ndarray,
    get_position_function,
    commission_rate: float = 0.001,
    position_limit_dollars: float = 10000.0,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
    function_name: Optional[str] = None,
) -> dict:
    """
    Backtest on provided data only.

    No new price data is generated. The engine only walks through the supplied
    official price matrix.
    """
    n_instruments, n_days = prices.shape
    start_day, end_day = validate_day_window(n_days, start_day, end_day)
    function_name = resolve_function_name(get_position_function, function_name)

    current_positions = np.zeros(n_instruments, dtype=int)

    daily_records = []
    daily_pnl = []
    gross_daily_pnl = []
    cumulative_pnl = []
    position_history = []
    trade_history = []
    daily_turnover = []
    daily_commission = []
    instrument_pnl_history = []
    instrument_turnover_history = []
    instrument_commission_history = []
    trade_logs = []
    clipping_events = []

    running_pnl = 0.0
    running_gross_pnl = 0.0

    for day in range(start_day, end_day + 1):
        prices_so_far = prices[:, : day + 1]

        previous_prices = prices[:, day - 1]
        current_prices = prices[:, day]
        previous_positions = current_positions.copy()

        try:
            desired_positions = get_position_function(prices_so_far)
        except Exception as exc:
            raise RuntimeError(
                f"Strategy function {function_name} crashed on day {day} "
                f"with prices_so_far shape {prices_so_far.shape}: {exc}"
            ) from exc

        try:
            desired_positions = validate_positions(desired_positions, n_instruments)
        except ValueError as exc:
            raise ValueError(
                f"Strategy function {function_name} returned invalid positions "
                f"on day {day} with prices_so_far shape {prices_so_far.shape}: {exc}"
            ) from exc

        clipped_positions, num_clipped, clipped_mask = clip_positions_to_limit(
            desired_positions=desired_positions,
            current_prices=current_prices,
            position_limit_dollars=position_limit_dollars,
        )

        trades = clipped_positions - previous_positions
        trade_values = trades * current_prices
        instrument_turnover = np.abs(trade_values).astype(float)
        instrument_commission = instrument_turnover * commission_rate

        turnover = float(np.sum(instrument_turnover))
        commission = float(np.sum(instrument_commission))
        day_trade_logs = build_trade_log_entries(
            day=day,
            trades=trades,
            current_prices=current_prices,
            previous_positions=previous_positions,
            new_positions=clipped_positions,
            commission_rate=commission_rate,
        )

        price_changes = current_prices - previous_prices
        instrument_gross_pnl = previous_positions * price_changes
        instrument_net_pnl = instrument_gross_pnl - instrument_commission
        gross_pnl = float(np.sum(instrument_gross_pnl))
        net_pnl = float(np.sum(instrument_net_pnl))

        running_gross_pnl += gross_pnl
        running_pnl += net_pnl

        daily_pnl.append(net_pnl)
        gross_daily_pnl.append(gross_pnl)
        cumulative_pnl.append(running_pnl)
        position_history.append(clipped_positions.tolist())
        trade_history.append(trades.tolist())
        daily_turnover.append(turnover)
        daily_commission.append(commission)
        instrument_pnl_history.append(instrument_net_pnl.astype(float).tolist())
        instrument_turnover_history.append(instrument_turnover.astype(float).tolist())
        instrument_commission_history.append(instrument_commission.astype(float).tolist())
        trade_logs.extend(day_trade_logs)

        if num_clipped > 0:
            clipping_events.append(
                {
                    "day": int(day),
                    "num_clipped_instruments": num_clipped,
                    "instruments": [
                        int(instrument)
                        for instrument in np.flatnonzero(clipped_mask)
                    ],
                }
            )

        daily_records.append(
            {
                "day": int(day),
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
    run_days = int(end_day - start_day + 1)

    instrument_summary = build_instrument_summary(
        instrument_pnl=instrument_pnl_history,
        instrument_turnover=instrument_turnover_history,
        instrument_commission=instrument_commission_history,
        positions=position_history,
        trades=trade_history,
    )

    summary = {
        "score": float(score),
        "total_pnl": float(running_pnl),
        "total_gross_pnl": float(running_gross_pnl),
        "mean_daily_pnl": mean_daily_pnl,
        "std_daily_pnl": std_daily_pnl,
        "max_drawdown": max_drawdown,
        "total_commission": float(np.sum(daily_commission)),
        "total_turnover": float(np.sum(daily_turnover)),
        "total_trades": len(trade_logs),
        "clipping_event_count": len(clipping_events),
    }

    warnings = build_warnings(
        summary=summary,
        instrument_summary=instrument_summary,
        daily_pnl=daily_pnl,
        clipping_events=clipping_events,
        run_days=run_days,
        n_instruments=n_instruments,
        position_limit_dollars=position_limit_dollars,
    )

    return {
        "metadata": {
            "n_instruments": int(n_instruments),
            "n_days": int(n_days),
            "start_day": int(start_day),
            "end_day": int(end_day),
            "run_days": run_days,
            "commission_rate": float(commission_rate),
            "position_limit_dollars": float(position_limit_dollars),
            "strategy_function_name": function_name,
            "deterministic": True,
            "uses_simulated_price_data": False,
        },
        "summary": summary,
        "daily_records": daily_records,
        "series": {
            "days": [record["day"] for record in daily_records],
            "daily_pnl": daily_pnl,
            "gross_daily_pnl": gross_daily_pnl,
            "cumulative_pnl": cumulative_pnl,
            "drawdown": drawdown,
            "daily_turnover": daily_turnover,
            "daily_commission": daily_commission,
        },
        "positions": position_history,
        "trades": trade_history,
        "trade_logs": trade_logs,
        "instrument_summary": instrument_summary,
        "warnings": warnings,
        "clipping_events": clipping_events,
    }
