import numpy as np


def load_prices(path: str) -> np.ndarray:
    prices = np.loadtxt(path)

    if prices.ndim != 2:
        raise ValueError(
            "Price data must be a 2D array with shape "
            f"(instruments, days); got {prices.ndim}D data."
        )

    n_instruments, n_days = prices.shape

    if n_instruments < 1:
        raise ValueError("Price data must contain at least one instrument.")

    if n_days < 2:
        raise ValueError("Price data must contain at least two days.")

    if np.any(~np.isfinite(prices)):
        raise ValueError("Price data contains NaN or infinite values.")

    if np.any(prices <= 0):
        raise ValueError("Price data must contain only positive prices.")

    return prices
