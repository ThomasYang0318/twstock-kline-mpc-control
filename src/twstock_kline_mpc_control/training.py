from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

import pandas as pd

from .backtest import BacktestResult, run_backtest
from .mpc import MPCConfig


@dataclass(frozen=True)
class TrainHoldoutSplit:
    train: pd.DataFrame
    holdout: pd.DataFrame
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    holdout_start: pd.Timestamp
    holdout_end: pd.Timestamp


@dataclass(frozen=True)
class CalibrationResult:
    best_config: MPCConfig
    train_result: BacktestResult
    holdout_result: BacktestResult
    grid_results: pd.DataFrame
    split: TrainHoldoutSplit


def split_train_holdout(
    frame: pd.DataFrame,
    holdout_years: int = 4,
    min_train_years: int = 3,
) -> TrainHoldoutSplit:
    """Split a time series into non-overlapping train and final holdout periods."""
    if holdout_years <= 0:
        raise ValueError("holdout_years must be positive.")
    if min_train_years <= 0:
        raise ValueError("min_train_years must be positive.")

    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError("Cannot split an empty frame.")

    holdout_start = data["date"].max() - pd.DateOffset(years=holdout_years)
    train = data[data["date"] < holdout_start].reset_index(drop=True)
    holdout = data[data["date"] >= holdout_start].reset_index(drop=True)

    if train.empty or holdout.empty:
        raise ValueError("Split produced an empty train or holdout period.")
    if train["date"].max() >= holdout["date"].min():
        raise ValueError("Train and holdout periods overlap.")

    train_years = (train["date"].max() - train["date"].min()).days / 365.25
    if train_years < min_train_years:
        raise ValueError(
            f"Training period is only {train_years:.2f} years; "
            f"need at least {min_train_years} years."
        )

    return TrainHoldoutSplit(
        train=train,
        holdout=holdout,
        train_start=train["date"].min(),
        train_end=train["date"].max(),
        holdout_start=holdout["date"].min(),
        holdout_end=holdout["date"].max(),
    )


def calibrate_mpc(
    frame: pd.DataFrame,
    holdout_years: int = 4,
    initial_cash: float = 1_000_000.0,
    horizons: Iterable[int] = (3, 5, 10),
    risk_aversions: Iterable[float] = (5.0, 10.0, 20.0),
    turnover_penalties: Iterable[float] = (0.1, 0.5, 1.0),
    transaction_cost: float = 0.001,
) -> CalibrationResult:
    """Tune MPC hyperparameters on train data and evaluate once on holdout data."""
    split = split_train_holdout(frame, holdout_years=holdout_years)
    rows = []
    best_score = float("-inf")
    best_config = None
    best_train_result = None

    for horizon, risk_aversion, turnover_penalty in product(
        horizons,
        risk_aversions,
        turnover_penalties,
    ):
        config = MPCConfig(
            horizon=int(horizon),
            risk_aversion=float(risk_aversion),
            turnover_penalty=float(turnover_penalty),
            transaction_cost=transaction_cost,
        )
        train_result = run_backtest(split.train, mpc_config=config, initial_cash=initial_cash)
        score = _selection_score(train_result.summary)
        row = {
            "horizon": config.horizon,
            "risk_aversion": config.risk_aversion,
            "turnover_penalty": config.turnover_penalty,
            "transaction_cost": config.transaction_cost,
            "score": score,
            **{f"train_{key}": value for key, value in train_result.summary.items()},
        }
        rows.append(row)

        if score > best_score:
            best_score = score
            best_config = config
            best_train_result = train_result

    if best_config is None or best_train_result is None:
        raise ValueError("No MPC configurations were evaluated.")

    holdout_result = run_backtest(split.holdout, mpc_config=best_config, initial_cash=initial_cash)
    grid_results = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    return CalibrationResult(
        best_config=best_config,
        train_result=best_train_result,
        holdout_result=holdout_result,
        grid_results=grid_results,
        split=split,
    )


def _selection_score(summary: dict[str, float]) -> float:
    # Reward risk-adjusted return while penalizing large drawdowns.
    return float(summary["sharpe"] + summary["annualized_return"] + summary["max_drawdown"])

