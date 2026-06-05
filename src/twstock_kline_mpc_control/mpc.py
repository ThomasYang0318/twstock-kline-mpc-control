from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MPCConfig:
    horizon: int = 5
    min_weight: float = 0.0
    max_weight: float = 1.0
    risk_aversion: float = 10.0
    turnover_penalty: float = 0.5
    transaction_cost: float = 0.001

    def validate(self) -> None:
        if self.horizon <= 0:
            raise ValueError("horizon must be positive.")
        if self.min_weight > self.max_weight:
            raise ValueError("min_weight must be <= max_weight.")
        if self.risk_aversion < 0 or self.turnover_penalty < 0 or self.transaction_cost < 0:
            raise ValueError("penalties and costs must be non-negative.")


def optimize_weight_plan(
    expected_returns: np.ndarray,
    volatilities: np.ndarray,
    current_weight: float,
    config: MPCConfig | None = None,
) -> np.ndarray:
    """Optimize a bounded scalar weight plan over the MPC horizon."""
    cfg = config or MPCConfig()
    cfg.validate()

    mu = _pad_to_horizon(np.asarray(expected_returns, dtype=float), cfg.horizon)
    sigma = _pad_to_horizon(np.asarray(volatilities, dtype=float), cfg.horizon)
    sigma = np.nan_to_num(sigma, nan=0.02, posinf=0.02, neginf=0.02)
    mu = np.nan_to_num(mu, nan=0.0, posinf=0.0, neginf=0.0)

    bounds = [(cfg.min_weight, cfg.max_weight)] * cfg.horizon
    initial = np.full(cfg.horizon, np.clip(current_weight, cfg.min_weight, cfg.max_weight))

    try:
        from scipy.optimize import minimize

        solution = minimize(
            _objective,
            initial,
            args=(mu, sigma, current_weight, cfg),
            bounds=bounds,
            method="SLSQP",
            options={"maxiter": 200, "ftol": 1e-10},
        )
        if solution.success:
            return np.clip(solution.x, cfg.min_weight, cfg.max_weight)
    except Exception:
        pass

    return _grid_fallback(mu, sigma, current_weight, cfg)


def _objective(weights: np.ndarray, mu: np.ndarray, sigma: np.ndarray, current_weight: float, cfg: MPCConfig) -> float:
    previous = np.concatenate([[current_weight], weights[:-1]])
    turnover = weights - previous
    reward = mu * weights
    risk = cfg.risk_aversion * (sigma**2) * (weights**2)
    trading = cfg.turnover_penalty * (turnover**2) + cfg.transaction_cost * np.abs(turnover)
    return float(np.sum(-reward + risk + trading))


def _pad_to_horizon(values: np.ndarray, horizon: int) -> np.ndarray:
    if values.size == 0:
        return np.zeros(horizon)
    if values.size >= horizon:
        return values[:horizon]
    return np.pad(values, (0, horizon - values.size), mode="edge")


def _grid_fallback(mu: np.ndarray, sigma: np.ndarray, current_weight: float, cfg: MPCConfig) -> np.ndarray:
    grid = np.linspace(cfg.min_weight, cfg.max_weight, 101)
    best_weight = min(
        grid,
        key=lambda weight: _objective(np.full(cfg.horizon, weight), mu, sigma, current_weight, cfg),
    )
    return np.full(cfg.horizon, best_weight)

