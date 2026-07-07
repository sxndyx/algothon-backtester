def getMyPosition(prices):
    """
    Deliberately broken strategy for validating error messages.
    """
    if prices.shape[1] >= 3:
        raise RuntimeError("example strategy failure")

    return [0] * prices.shape[0]
