import numpy as np


def getMyPosition(prices):
    """
    Intentionally returns the wrong number of positions for validation demos.
    """
    n_instruments = prices.shape[0]
    return np.zeros(n_instruments + 1, dtype=int)
