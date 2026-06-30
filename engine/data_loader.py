import numpy as np


def load_prices(path: str) -> np.ndarray:
    """
    Load official Algothon price data from a text file.

    Expected shape:
        rows = instruments
        columns = days

    Example:
        prices[instrument, day]
    """
    prices = np.loadtxt(path)

    if prices.ndim != 2:
        raise ValueError("Price data must be a 2D array.")

    if prices.shape[0] <= 0 or prices.shape[1] <= 1:
        raise ValueError("Price data must contain instruments and multiple days.")

    if np.any(~np.isfinite(prices)):
        raise ValueError("Price data contains NaN or infinite values.")

    return prices