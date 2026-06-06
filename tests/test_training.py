import pandas as pd

from twstock_kline_mpc_control.training import calibrate_mpc, split_train_holdout


def _frame(periods=2600):
    close = pd.Series(range(100, 100 + periods), dtype=float)
    return pd.DataFrame(
        {
            "date": pd.bdate_range("2015-01-01", periods=periods),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": range(1000, 1000 + periods),
        }
    )


def test_split_train_holdout_has_no_overlap():
    split = split_train_holdout(_frame(), holdout_years=4)

    assert split.train["date"].max() < split.holdout["date"].min()
    assert len(split.train) > len(split.holdout)


def test_calibrate_mpc_evaluates_holdout_with_best_train_config():
    result = calibrate_mpc(
        _frame(),
        holdout_years=4,
        horizons=(3,),
        risk_aversions=(5.0, 10.0),
        turnover_penalties=(0.1,),
    )

    assert len(result.grid_results) == 2
    assert result.best_config.horizon == 3
    assert result.holdout_result.summary["final_equity"] > 0
    assert result.split.train_end < result.split.holdout_start
