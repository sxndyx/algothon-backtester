import importlib.util
from pathlib import Path


def load_strategy(strategy_path: str):
    """
    Dynamically load a Python strategy file that contains getMyPosition().
    """
    path = Path(strategy_path)

    if not path.exists():
        raise FileNotFoundError(f"Strategy file not found: {strategy_path}")

    spec = importlib.util.spec_from_file_location("user_strategy", strategy_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import strategy file: {strategy_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "getMyPosition"):
        raise AttributeError("Strategy file must define getMyPosition(prices).")

    return module.getMyPosition