# 2330.TW Train/Holdout Backtest

Generated on 2026-06-06.

## Protocol

This run uses a non-overlapping chronological split:

| Period | Start | End | Rows | Purpose |
| --- | --- | --- | ---: | --- |
| Train | 2010-01-04 | 2021-12-29 | 2943 | MPC hyperparameter selection |
| Holdout | 2021-12-30 | 2025-12-30 | 969 | Final out-of-sample backtest |

The holdout period was not used for parameter selection.

## Data

- Symbol: `2330.TW`
- Rows: `3912`
- Date range: `2010-01-04` to `2025-12-30`
- Local file: `data/2330_long.csv`
- SHA256: `ce5a8c4eae99c32894b4d52090abca2c3cf9bd36ab6483d859971f48f96ea886`

## Command

```powershell
$env:PYTHONPATH='src'
python -B -m twstock_kline_mpc_control fetch 2330 --start 2010-01-01 --end 2025-12-31 --out data/2330_long.csv
python -B -m twstock_kline_mpc_control calibrate data/2330_long.csv --holdout-years 4 --grid-out reports/2330_long_train_grid.csv --holdout-out reports/2330_long_holdout_backtest.csv
```

## Selected MPC Configuration

The best configuration was selected on train data only:

| Parameter | Value |
| --- | ---: |
| Horizon | `10` |
| Risk aversion | `20.0` |
| Turnover penalty | `0.5` |
| Transaction cost | `0.001` |

## Result

| Metric | Train | Holdout |
| --- | ---: | ---: |
| Total return | `2430.67%` | `402.46%` |
| Annualized return | `31.89%` | `52.24%` |
| Annualized volatility | `14.53%` | `18.77%` |
| Sharpe | `2.1951` | `2.7831` |
| Max drawdown | `-11.81%` | `-8.02%` |
| Final equity | `25,306,686.11` | `5,024,644.52` |

## Interpretation

This result is more defensible than the earlier single-period backtest because
the final holdout years are not used for tuning. It is still a historical
simulation, not a live-trading guarantee. The next robustness checks should be:

- Repeat with 3-year and 5-year holdout windows.
- Repeat across all tested stocks.
- Add walk-forward validation, where parameters are periodically reselected
  using only past data.

