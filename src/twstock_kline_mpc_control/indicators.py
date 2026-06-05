from __future__ import annotations

import numpy as np
import pandas as pd


def add_indicators(
    frame: pd.DataFrame,
    fast_window: int = 5,
    slow_window: int = 20,
    volatility_window: int = 20,
) -> pd.DataFrame:
    """Add lightweight trend and risk features used by the MPC controller."""
    if "close" not in frame.columns:
        raise ValueError("Input frame must contain a close column.")
    if fast_window <= 0 or slow_window <= 0 or volatility_window <= 1:
        raise ValueError("Indicator windows must be positive; volatility_window must be > 1.")

    result = frame.copy()
    close = result["close"].astype(float)
    returns = close.pct_change().replace([np.inf, -np.inf], np.nan)

    result["return"] = returns
    result["ma_fast"] = close.rolling(fast_window).mean()
    result["ma_slow"] = close.rolling(slow_window).mean()
    result["trend"] = (result["ma_fast"] / result["ma_slow"] - 1.0).replace([np.inf, -np.inf], np.nan)
    result["momentum"] = close.pct_change(fast_window).replace([np.inf, -np.inf], np.nan)
    result["volatility"] = returns.rolling(volatility_window).std().replace(0.0, np.nan)
    result["signal"] = (0.65 * result["trend"] + 0.35 * result["momentum"]).clip(-0.08, 0.08)
    return result

