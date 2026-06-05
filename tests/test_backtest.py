import pandas as pd

from twstock_kline_mpc_control.backtest import run_backtest
from twstock_kline_mpc_control.mpc import MPCConfig


def test_backtest_returns_equity_curve_and_summary():
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=60),
            "open": range(100, 160),
            "high": range(101, 161),
            "low": range(99, 159),
            "close": range(100, 160),
            "volume": range(1000, 1060),
        }
    )

    result = run_backtest(frame, mpc_config=MPCConfig(horizon=4), initial_cash=100_000)

    assert not result.equity_curve.empty
    assert result.summary["final_equity"] > 0
    assert "max_drawdown" in result.summary

