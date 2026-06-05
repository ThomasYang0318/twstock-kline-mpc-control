import numpy as np

from twstock_kline_mpc_control.mpc import MPCConfig, optimize_weight_plan


def test_optimizer_respects_bounds():
    config = MPCConfig(horizon=3, min_weight=0.0, max_weight=0.7)
    plan = optimize_weight_plan(
        expected_returns=np.array([0.02, 0.01, 0.015]),
        volatilities=np.array([0.02, 0.02, 0.02]),
        current_weight=0.0,
        config=config,
    )

    assert len(plan) == 3
    assert np.all(plan >= 0.0)
    assert np.all(plan <= 0.7)


def test_optimizer_reduces_exposure_for_negative_signal():
    config = MPCConfig(horizon=3, min_weight=0.0, max_weight=1.0, turnover_penalty=0.0)
    plan = optimize_weight_plan(
        expected_returns=np.array([-0.03, -0.02, -0.01]),
        volatilities=np.array([0.02, 0.02, 0.02]),
        current_weight=0.5,
        config=config,
    )

    assert plan[0] < 0.5

