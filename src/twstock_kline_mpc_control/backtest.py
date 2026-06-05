from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .indicators import add_indicators
from .mpc import MPCConfig, optimize_weight_plan


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: pd.DataFrame
    summary: dict[str, float]


def run_backtest(
    frame: pd.DataFrame,
    mpc_config: MPCConfig | None = None,
    initial_cash: float = 1_000_000.0,
) -> BacktestResult:
    """Run a long-only daily backtest using the first MPC action each day."""
    cfg = mpc_config or MPCConfig()
    cfg.validate()
    if initial_cash <= 0:
        raise ValueError("initial_cash must be positive.")

    features = frame if {"signal", "volatility", "return"}.issubset(frame.columns) else add_indicators(frame)
    features = features.sort_values("date").reset_index(drop=True).copy()
    features["next_return"] = features["close"].pct_change().shift(-1)

    equity = initial_cash
    current_weight = 0.0
    records: list[dict[str, float | str]] = []

    for index, row in features.iloc[:-1].iterrows():
        if not np.isfinite(row.get("signal", np.nan)) or not np.isfinite(row.get("volatility", np.nan)):
            records.append(_record(row, current_weight, 0.0, equity))
            continue

        horizon_slice = features.iloc[index : index + cfg.horizon]
        expected_returns = horizon_slice["signal"].to_numpy(dtype=float)
        volatilities = horizon_slice["volatility"].to_numpy(dtype=float)
        target_weight = float(optimize_weight_plan(expected_returns, volatilities, current_weight, cfg)[0])

        turnover = abs(target_weight - current_weight)
        market_return = float(row["next_return"]) if np.isfinite(row["next_return"]) else 0.0
        portfolio_return = target_weight * market_return - cfg.transaction_cost * turnover
        equity *= 1.0 + portfolio_return
        current_weight = target_weight
        records.append(_record(row, target_weight, portfolio_return, equity))

    curve = pd.DataFrame.from_records(records)
    if curve.empty:
        raise ValueError("Not enough rows to run a backtest.")

    curve["peak_equity"] = curve["equity"].cummax()
    curve["drawdown"] = curve["equity"] / curve["peak_equity"] - 1.0
    summary = _summary(curve, initial_cash)
    return BacktestResult(equity_curve=curve, summary=summary)


def _record(row: pd.Series, target_weight: float, portfolio_return: float, equity: float) -> dict[str, float | str]:
    return {
        "date": row["date"],
        "close": float(row["close"]),
        "target_weight": target_weight,
        "portfolio_return": portfolio_return,
        "equity": equity,
    }


def _summary(curve: pd.DataFrame, initial_cash: float) -> dict[str, float]:
    returns = curve["portfolio_return"].astype(float)
    total_return = float(curve["equity"].iloc[-1] / initial_cash - 1.0)
    annualized_return = float((1.0 + total_return) ** (252 / max(len(curve), 1)) - 1.0)
    volatility = float(returns.std(ddof=0) * np.sqrt(252))
    sharpe = float(annualized_return / volatility) if volatility > 0 else 0.0
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": float(curve["drawdown"].min()),
        "final_equity": float(curve["equity"].iloc[-1]),
    }

