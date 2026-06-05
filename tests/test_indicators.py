import pandas as pd

from twstock_kline_mpc_control.indicators import add_indicators


def test_add_indicators_creates_signal_columns():
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "open": range(100, 130),
            "high": range(101, 131),
            "low": range(99, 129),
            "close": range(100, 130),
            "volume": range(1000, 1030),
        }
    )

    result = add_indicators(frame, fast_window=3, slow_window=5, volatility_window=5)

    assert {"return", "ma_fast", "ma_slow", "trend", "momentum", "volatility", "signal"}.issubset(result.columns)
    assert result["signal"].dropna().between(-0.08, 0.08).all()

