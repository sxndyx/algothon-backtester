import numpy as np


def getMyPosition(prices):
    """
    If today's price is higher than yesterday's, go long 10 shares.
    If today's price is lower than yesterday's, go short 10 shares.
    Otherwise hold zero.
    """
    n_instruments, n_days = prices.shape

    if n_days < 2:
        return np.zeros(n_instruments, dtype=int)

    yesterday = prices[:, -2]
    today = prices[:, -1]

    positions = np.zeros(n_instruments, dtype=int)
    positions[today > yesterday] = 10
    positions[today < yesterday] = -10

    return positions